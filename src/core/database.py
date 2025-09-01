"""
Database Management System für GermanCodeZero-Cleaner
=====================================================

Hochperformante Datenbank-Verwaltung mit SQLite und optionaler
PostgreSQL-Unterstützung für Premium-Features.
"""

import sqlite3
import json
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib
import pickle
import zlib
from contextlib import contextmanager
import logging

# Optional: PostgreSQL Support für Cloud-Features
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

from config import get_app_data_dir, SECURITY_CONFIG


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ScanRecord:
    """Datensatz für System-Scans."""
    id: Optional[int] = None
    timestamp: datetime = None
    duration_seconds: float = 0.0
    total_files: int = 0
    total_size: int = 0
    categories: Dict[str, int] = None
    cleaned_files: int = 0
    freed_space: int = 0
    user_id: Optional[str] = None
    system_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.categories is None:
            self.categories = {}
        if self.system_info is None:
            self.system_info = {}


@dataclass
class CleaningHistory:
    """Historie von Bereinigungsvorgängen."""
    id: Optional[int] = None
    scan_id: int = None
    timestamp: datetime = None
    files_deleted: List[str] = None
    total_size_freed: int = 0
    backup_path: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.files_deleted is None:
            self.files_deleted = []


@dataclass
class UserSettings:
    """Benutzer-Einstellungen."""
    user_id: str
    auto_scan_enabled: bool = True
    data_sharing_enabled: bool = False
    premium_user: bool = False
    premium_expiry: Optional[datetime] = None
    selected_categories: List[str] = None
    theme: str = "dark"
    language: str = "de"
    notifications_enabled: bool = True
    scan_schedule: Optional[Dict[str, Any]] = None
    custom_paths: List[str] = None
    excluded_paths: List[str] = None
    
    def __post_init__(self):
        if self.selected_categories is None:
            self.selected_categories = ["temp_files", "cache", "logs"]
        if self.custom_paths is None:
            self.custom_paths = []
        if self.excluded_paths is None:
            self.excluded_paths = []


@dataclass
class PerformanceMetric:
    """Performance-Metriken für Analyse."""
    id: Optional[int] = None
    timestamp: datetime = None
    metric_type: str = ""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_io: float = 0.0
    gpu_usage: float = 0.0
    operation: str = ""
    duration_ms: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Hauptklasse für Datenbank-Verwaltung."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialisiert den Datenbank-Manager."""
        if db_path is None:
            db_path = get_app_data_dir() / "cleaner.db"
        
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Cache für häufige Abfragen
        self.cache = {}
        self.cache_ttl = 300  # 5 Minuten
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialisiert die Datenbank und erstellt Tabellen."""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                isolation_level=None  # Autocommit
            )
            
            # Enable optimizations
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA synchronous=NORMAL")
            self.connection.execute("PRAGMA cache_size=10000")
            self.connection.execute("PRAGMA temp_store=MEMORY")
            
            self._create_tables()
            self._create_indexes()
            
            self.logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_tables(self):
        """Erstellt alle erforderlichen Tabellen."""
        queries = [
            # Scan-Historie
            """
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration_seconds REAL,
                total_files INTEGER,
                total_size INTEGER,
                categories TEXT,
                cleaned_files INTEGER DEFAULT 0,
                freed_space INTEGER DEFAULT 0,
                user_id TEXT,
                system_info TEXT
            )
            """,
            
            # Bereinigungshistorie
            """
            CREATE TABLE IF NOT EXISTS cleaning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                files_deleted TEXT,
                total_size_freed INTEGER,
                backup_path TEXT,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                FOREIGN KEY (scan_id) REFERENCES scan_history(id)
            )
            """,
            
            # Benutzer-Einstellungen
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id TEXT PRIMARY KEY,
                auto_scan_enabled BOOLEAN DEFAULT 1,
                data_sharing_enabled BOOLEAN DEFAULT 0,
                premium_user BOOLEAN DEFAULT 0,
                premium_expiry DATETIME,
                selected_categories TEXT,
                theme TEXT DEFAULT 'dark',
                language TEXT DEFAULT 'de',
                notifications_enabled BOOLEAN DEFAULT 1,
                scan_schedule TEXT,
                custom_paths TEXT,
                excluded_paths TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Performance-Metriken
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                disk_io REAL,
                gpu_usage REAL,
                operation TEXT,
                duration_ms REAL
            )
            """,
            
            # Datei-Hashes für Duplikat-Erkennung
            """
            CREATE TABLE IF NOT EXISTS file_hashes (
                file_path TEXT PRIMARY KEY,
                hash_value TEXT NOT NULL,
                file_size INTEGER,
                last_modified DATETIME,
                scan_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # AI-Erklärungen Cache
            """
            CREATE TABLE IF NOT EXISTS ai_explanations (
                file_pattern TEXT PRIMARY KEY,
                explanation TEXT,
                category TEXT,
                safety_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Premium-Features Tracking
            """
            CREATE TABLE IF NOT EXISTS premium_features (
                user_id TEXT PRIMARY KEY,
                activation_date DATETIME,
                expiry_date DATETIME,
                feature_usage TEXT,
                data_shared_mb INTEGER DEFAULT 0,
                free_months_earned INTEGER DEFAULT 0
            )
            """
        ]
        
        with self.lock:
            for query in queries:
                self.connection.execute(query)
    
    def _create_indexes(self):
        """Erstellt Indizes für bessere Performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_scan_timestamp ON scan_history(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_scan_user ON scan_history(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_cleaning_scan ON cleaning_history(scan_id)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_type ON performance_metrics(metric_type)",
            "CREATE INDEX IF NOT EXISTS idx_hash_value ON file_hashes(hash_value)",
            "CREATE INDEX IF NOT EXISTS idx_ai_category ON ai_explanations(category)"
        ]
        
        with self.lock:
            for index in indexes:
                self.connection.execute(index)
    
    @contextmanager
    def transaction(self):
        """Context Manager für Transaktionen."""
        with self.lock:
            try:
                self.connection.execute("BEGIN")
                yield self.connection
                self.connection.execute("COMMIT")
            except Exception as e:
                self.connection.execute("ROLLBACK")
                raise e
    
    # ========================================================================
    # SCAN OPERATIONS
    # ========================================================================
    
    def save_scan_result(self, scan_record: ScanRecord) -> int:
        """Speichert ein Scan-Ergebnis."""
        query = """
            INSERT INTO scan_history 
            (timestamp, duration_seconds, total_files, total_size, categories, 
             cleaned_files, freed_space, user_id, system_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.lock:
            cursor = self.connection.execute(query, (
                scan_record.timestamp,
                scan_record.duration_seconds,
                scan_record.total_files,
                scan_record.total_size,
                json.dumps(scan_record.categories),
                scan_record.cleaned_files,
                scan_record.freed_space,
                scan_record.user_id,
                json.dumps(scan_record.system_info)
            ))
            
            return cursor.lastrowid
    
    def get_scan_history(self, user_id: Optional[str] = None, 
                        limit: int = 100) -> List[ScanRecord]:
        """Holt die Scan-Historie."""
        if user_id:
            query = """
                SELECT * FROM scan_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            params = (user_id, limit)
        else:
            query = """
                SELECT * FROM scan_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            params = (limit,)
        
        with self.lock:
            cursor = self.connection.execute(query, params)
            rows = cursor.fetchall()
        
        records = []
        for row in rows:
            record = ScanRecord(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]) if row[1] else None,
                duration_seconds=row[2],
                total_files=row[3],
                total_size=row[4],
                categories=json.loads(row[5]) if row[5] else {},
                cleaned_files=row[6],
                freed_space=row[7],
                user_id=row[8],
                system_info=json.loads(row[9]) if row[9] else {}
            )
            records.append(record)
        
        return records
    
    def get_scan_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Berechnet Scan-Statistiken."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT 
                COUNT(*) as total_scans,
                SUM(total_files) as total_files_scanned,
                SUM(total_size) as total_size_found,
                SUM(cleaned_files) as total_files_cleaned,
                SUM(freed_space) as total_space_freed,
                AVG(duration_seconds) as avg_scan_duration
            FROM scan_history
            WHERE timestamp > ?
        """
        
        with self.lock:
            cursor = self.connection.execute(query, (cutoff_date,))
            row = cursor.fetchone()
        
        return {
            "total_scans": row[0] or 0,
            "total_files_scanned": row[1] or 0,
            "total_size_found": row[2] or 0,
            "total_files_cleaned": row[3] or 0,
            "total_space_freed": row[4] or 0,
            "avg_scan_duration": row[5] or 0
        }
    
    # ========================================================================
    # CLEANING OPERATIONS
    # ========================================================================
    
    def save_cleaning_history(self, cleaning: CleaningHistory) -> int:
        """Speichert Bereinigungshistorie."""
        query = """
            INSERT INTO cleaning_history
            (scan_id, timestamp, files_deleted, total_size_freed, 
             backup_path, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.lock:
            cursor = self.connection.execute(query, (
                cleaning.scan_id,
                cleaning.timestamp,
                json.dumps(cleaning.files_deleted),
                cleaning.total_size_freed,
                cleaning.backup_path,
                cleaning.success,
                cleaning.error_message
            ))
            
            return cursor.lastrowid
    
    def get_cleaning_history(self, scan_id: Optional[int] = None,
                            limit: int = 100) -> List[CleaningHistory]:
        """Holt Bereinigungshistorie."""
        if scan_id:
            query = """
                SELECT * FROM cleaning_history 
                WHERE scan_id = ? 
                ORDER BY timestamp DESC
            """
            params = (scan_id,)
        else:
            query = """
                SELECT * FROM cleaning_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            params = (limit,)
        
        with self.lock:
            cursor = self.connection.execute(query, params)
            rows = cursor.fetchall()
        
        history = []
        for row in rows:
            record = CleaningHistory(
                id=row[0],
                scan_id=row[1],
                timestamp=datetime.fromisoformat(row[2]) if row[2] else None,
                files_deleted=json.loads(row[3]) if row[3] else [],
                total_size_freed=row[4],
                backup_path=row[5],
                success=bool(row[6]),
                error_message=row[7]
            )
            history.append(record)
        
        return history
    
    # ========================================================================
    # USER SETTINGS
    # ========================================================================
    
    def save_user_settings(self, settings: UserSettings):
        """Speichert Benutzer-Einstellungen."""
        query = """
            INSERT OR REPLACE INTO user_settings
            (user_id, auto_scan_enabled, data_sharing_enabled, premium_user,
             premium_expiry, selected_categories, theme, language,
             notifications_enabled, scan_schedule, custom_paths, excluded_paths,
             updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        with self.lock:
            self.connection.execute(query, (
                settings.user_id,
                settings.auto_scan_enabled,
                settings.data_sharing_enabled,
                settings.premium_user,
                settings.premium_expiry,
                json.dumps(settings.selected_categories),
                settings.theme,
                settings.language,
                settings.notifications_enabled,
                json.dumps(settings.scan_schedule) if settings.scan_schedule else None,
                json.dumps(settings.custom_paths),
                json.dumps(settings.excluded_paths)
            ))
    
    def get_user_settings(self, user_id: str) -> Optional[UserSettings]:
        """Holt Benutzer-Einstellungen."""
        query = "SELECT * FROM user_settings WHERE user_id = ?"
        
        with self.lock:
            cursor = self.connection.execute(query, (user_id,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return UserSettings(
            user_id=row[0],
            auto_scan_enabled=bool(row[1]),
            data_sharing_enabled=bool(row[2]),
            premium_user=bool(row[3]),
            premium_expiry=datetime.fromisoformat(row[4]) if row[4] else None,
            selected_categories=json.loads(row[5]) if row[5] else [],
            theme=row[6],
            language=row[7],
            notifications_enabled=bool(row[8]),
            scan_schedule=json.loads(row[9]) if row[9] else None,
            custom_paths=json.loads(row[10]) if row[10] else [],
            excluded_paths=json.loads(row[11]) if row[11] else []
        )
    
    # ========================================================================
    # PERFORMANCE METRICS
    # ========================================================================
    
    def save_performance_metric(self, metric: PerformanceMetric):
        """Speichert Performance-Metrik."""
        query = """
            INSERT INTO performance_metrics
            (timestamp, metric_type, cpu_usage, memory_usage, disk_io,
             gpu_usage, operation, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.lock:
            self.connection.execute(query, (
                metric.timestamp,
                metric.metric_type,
                metric.cpu_usage,
                metric.memory_usage,
                metric.disk_io,
                metric.gpu_usage,
                metric.operation,
                metric.duration_ms
            ))
    
    def get_performance_metrics(self, metric_type: Optional[str] = None,
                               hours: int = 24) -> List[PerformanceMetric]:
        """Holt Performance-Metriken."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if metric_type:
            query = """
                SELECT * FROM performance_metrics 
                WHERE metric_type = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """
            params = (metric_type, cutoff_time)
        else:
            query = """
                SELECT * FROM performance_metrics 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            """
            params = (cutoff_time,)
        
        with self.lock:
            cursor = self.connection.execute(query, params)
            rows = cursor.fetchall()
        
        metrics = []
        for row in rows:
            metric = PerformanceMetric(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]) if row[1] else None,
                metric_type=row[2],
                cpu_usage=row[3],
                memory_usage=row[4],
                disk_io=row[5],
                gpu_usage=row[6],
                operation=row[7],
                duration_ms=row[8]
            )
            metrics.append(metric)
        
        return metrics
    
    # ========================================================================
    # FILE HASH OPERATIONS
    # ========================================================================
    
    def save_file_hash(self, file_path: str, hash_value: str, 
                      file_size: int, last_modified: datetime):
        """Speichert Datei-Hash für Duplikat-Erkennung."""
        query = """
            INSERT OR REPLACE INTO file_hashes
            (file_path, hash_value, file_size, last_modified, scan_date)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        with self.lock:
            self.connection.execute(query, (
                file_path, hash_value, file_size, last_modified
            ))
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Holt gespeicherten Hash für eine Datei."""
        query = "SELECT hash_value FROM file_hashes WHERE file_path = ?"
        
        with self.lock:
            cursor = self.connection.execute(query, (file_path,))
            row = cursor.fetchone()
        
        return row[0] if row else None
    
    def find_duplicate_hashes(self) -> Dict[str, List[str]]:
        """Findet alle Dateien mit identischen Hashes."""
        query = """
            SELECT hash_value, GROUP_CONCAT(file_path, '|') as paths
            FROM file_hashes
            GROUP BY hash_value
            HAVING COUNT(*) > 1
        """
        
        with self.lock:
            cursor = self.connection.execute(query)
            rows = cursor.fetchall()
        
        duplicates = {}
        for row in rows:
            hash_value = row[0]
            paths = row[1].split('|') if row[1] else []
            duplicates[hash_value] = paths
        
        return duplicates
    
    def cleanup_old_hashes(self, days: int = 30):
        """Entfernt alte Hash-Einträge."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = "DELETE FROM file_hashes WHERE scan_date < ?"
        
        with self.lock:
            self.connection.execute(query, (cutoff_date,))
    
    # ========================================================================
    # AI CACHE OPERATIONS
    # ========================================================================
    
    def save_ai_explanation(self, file_pattern: str, explanation: str,
                           category: str, safety_score: float):
        """Speichert AI-Erklärung im Cache."""
        query = """
            INSERT OR REPLACE INTO ai_explanations
            (file_pattern, explanation, category, safety_score, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        with self.lock:
            self.connection.execute(query, (
                file_pattern, explanation, category, safety_score
            ))
    
    def get_ai_explanation(self, file_pattern: str) -> Optional[Tuple[str, float]]:
        """Holt AI-Erklärung aus Cache."""
        query = """
            SELECT explanation, safety_score 
            FROM ai_explanations 
            WHERE file_pattern = ?
        """
        
        with self.lock:
            cursor = self.connection.execute(query, (file_pattern,))
            row = cursor.fetchone()
        
        return (row[0], row[1]) if row else None
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def vacuum(self):
        """Optimiert die Datenbank."""
        with self.lock:
            self.connection.execute("VACUUM")
            self.connection.execute("ANALYZE")
    
    def get_database_size(self) -> int:
        """Gibt die Datenbankgröße in Bytes zurück."""
        return self.db_path.stat().st_size if self.db_path.exists() else 0
    
    def export_data(self, export_path: Path) -> bool:
        """Exportiert Datenbank für Backup."""
        try:
            with self.lock:
                with sqlite3.connect(str(export_path)) as backup_conn:
                    self.connection.backup(backup_conn)
            return True
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return False
    
    def import_data(self, import_path: Path) -> bool:
        """Importiert Datenbank aus Backup."""
        try:
            if not import_path.exists():
                return False
            
            with self.lock:
                with sqlite3.connect(str(import_path)) as source_conn:
                    source_conn.backup(self.connection)
            return True
        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            return False
    
    def close(self):
        """Schließt die Datenbankverbindung."""
        if self.connection:
            with self.lock:
                self.connection.close()
                self.connection = None
    
    def __del__(self):
        """Destruktor - schließt Verbindung."""
        self.close()


# ============================================================================
# ASYNC DATABASE MANAGER (für Premium Cloud Features)
# ============================================================================

class AsyncDatabaseManager:
    """Asynchroner Datenbank-Manager für Cloud-Features."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialisiert den Connection Pool."""
        if not ASYNCPG_AVAILABLE:
            raise RuntimeError("asyncpg not available")
        
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
    
    async def save_cloud_backup(self, user_id: str, data: Dict[str, Any]):
        """Speichert Cloud-Backup."""
        query = """
            INSERT INTO cloud_backups (user_id, data, timestamp)
            VALUES ($1, $2, $3)
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                user_id,
                json.dumps(data),
                datetime.now()
            )
    
    async def get_cloud_backup(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Holt Cloud-Backup."""
        query = """
            SELECT data FROM cloud_backups 
            WHERE user_id = $1 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
        
        return json.loads(row['data']) if row else None
    
    async def close(self):
        """Schließt den Connection Pool."""
        if self.pool:
            await self.pool.close()


# ============================================================================
# DATABASE SINGLETON
# ============================================================================

_database_instance: Optional[DatabaseManager] = None
_database_lock = threading.Lock()


def get_database() -> DatabaseManager:
    """Gibt die Singleton-Datenbankinstanz zurück."""
    global _database_instance
    
    if _database_instance is None:
        with _database_lock:
            if _database_instance is None:
                _database_instance = DatabaseManager()
    
    return _database_instance


def close_database():
    """Schließt die globale Datenbankverbindung."""
    global _database_instance
    
    if _database_instance:
        with _database_lock:
            _database_instance.close()
            _database_instance = None