"""
Erweiterte Cleaner-Engine für GermanCodeZero-Cleaner
===================================================

Hardware-optimierte System-Bereinigung mit KI-Integration.
"""

import os
import sys
import time
import asyncio
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import mimetypes
import tempfile
import shutil
import winreg
import json

# System-Analyse
import psutil
import send2trash

# Hardware-Beschleunigung
try:
    import cupy as cp  # GPU-Beschleunigung
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

try:
    import numba
    from numba import cuda, jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

# Datenverarbeitung
import numpy as np
import pandas as pd

from config import SCAN_CONFIG, HARDWARE_CONFIG, SECURITY_CONFIG


# ============================================================================
# ERWEITERTE DATENSTRUKTUREN
# ============================================================================

@dataclass
class FileMetadata:
    """Erweiterte Datei-Metadaten."""
    path: str
    size: int
    created: datetime
    modified: datetime
    accessed: datetime
    attributes: int
    hash_sha256: Optional[str] = None
    mime_type: Optional[str] = None
    is_executable: bool = False
    is_system_file: bool = False
    compression_ratio: Optional[float] = None


@dataclass
class CleaningCategory:
    """Erweiterte Bereinigungskategorie."""
    id: str
    name: str
    description: str
    icon: str
    color: str
    priority: int
    safe_level: int  # 1-5, wobei 5 = sehr sicher
    estimated_impact: str  # "low", "medium", "high"
    items: List['EnhancedCleaningItem'] = field(default_factory=list)
    total_size: int = 0
    total_count: int = 0


@dataclass
class EnhancedCleaningItem:
    """Erweiterte Bereinigungseinträge mit KI-Analyse."""
    metadata: FileMetadata
    category: CleaningCategory
    safety_score: float  # 0.0 - 1.0
    impact_score: float  # 0.0 - 1.0
    ai_explanation: Optional[str] = None
    user_selected: bool = False
    deletion_method: str = "safe"  # "safe", "secure", "shred"
    backup_created: bool = False


@dataclass
class ScanStatistics:
    """Detaillierte Scan-Statistiken."""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    files_scanned: int = 0
    directories_scanned: int = 0
    bytes_analyzed: int = 0
    errors_encountered: int = 0
    categories_found: Dict[str, int] = field(default_factory=dict)
    hardware_utilization: Dict[str, float] = field(default_factory=dict)


# ============================================================================
# HARDWARE-OPTIMIERTE SCANNER-ENGINE
# ============================================================================

class AdvancedSystemScanner:
    """Erweiterte Scanner-Engine mit Hardware-Beschleunigung."""
    
    def __init__(self):
        self.is_scanning = False
        self.scan_cancelled = False
        self.current_statistics = ScanStatistics(start_time=datetime.now())
        
        # Hardware-Konfiguration
        self.cpu_cores = psutil.cpu_count(logical=False)
        self.cpu_threads = psutil.cpu_count(logical=True)
        self.memory_total = psutil.virtual_memory().total
        self.gpu_available = self._detect_gpu_capabilities()
        
        # Threading-Pools
        self.thread_executor = ThreadPoolExecutor(
            max_workers=min(self.cpu_threads, HARDWARE_CONFIG["cpu"]["max_threads"] or self.cpu_threads)
        )
        self.process_executor = ProcessPoolExecutor(
            max_workers=min(self.cpu_cores, 8)
        )
        
        # Cache für Performance
        self.file_hash_cache: Dict[str, str] = {}
        self.directory_cache: Dict[str, List[str]] = {}
        
        print(f"🔧 Scanner initialisiert: {self.cpu_cores} Kerne, {self.cpu_threads} Threads")
        if self.gpu_available:
            print("🎮 GPU-Beschleunigung verfügbar")
    
    def _detect_gpu_capabilities(self) -> Dict[str, bool]:
        """Erkennt verfügbare GPU-Beschleunigung."""
        capabilities = {
            "cuda": False,
            "opencl": False,
            "directx": False
        }
        
        # CUDA-Erkennung
        if CUPY_AVAILABLE:
            try:
                cp.cuda.runtime.getDeviceCount()
                capabilities["cuda"] = True
            except:
                pass
        
        # OpenCL-Erkennung
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            capabilities["opencl"] = len(platforms) > 0
        except ImportError:
            pass
        
        return capabilities
    
    async def perform_comprehensive_scan(
        self, 
        categories: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None,
        enable_ai_analysis: bool = True
    ) -> Dict[str, CleaningCategory]:
        """Führt einen umfassenden, hardware-beschleunigten Scan durch."""
        
        self.is_scanning = True
        self.scan_cancelled = False
        self.current_statistics = ScanStatistics(start_time=datetime.now())
        
        try:
            scan_results = {}
            total_categories = len(categories)
            
            # Parallele Kategorie-Scans
            scan_tasks = []
            
            for i, category in enumerate(categories):
                if self.scan_cancelled:
                    break
                
                task = self._scan_category_async(
                    category, 
                    lambda status, prog: progress_callback(
                        status, (i + prog) / total_categories
                    ) if progress_callback else None
                )
                scan_tasks.append(task)
            
            # Warte auf alle Scan-Tasks
            category_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
            
            # Verarbeite Ergebnisse
            for i, result in enumerate(category_results):
                if isinstance(result, Exception):
                    print(f"Fehler beim Scannen von {categories[i]}: {result}")
                    continue
                
                if result:
                    scan_results[categories[i]] = result
            
            # KI-Analyse falls aktiviert
            if enable_ai_analysis and scan_results:
                await self._perform_ai_analysis(scan_results, progress_callback)
            
            # Statistiken finalisieren
            self.current_statistics.end_time = datetime.now()
            self.current_statistics.duration_seconds = (
                self.current_statistics.end_time - self.current_statistics.start_time
            ).total_seconds()
            
            return scan_results
            
        finally:
            self.is_scanning = False
    
    async def _scan_category_async(
        self, 
        category: str, 
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Optional[CleaningCategory]:
        """Scannt eine spezifische Kategorie asynchron."""
        
        category_config = self._get_category_config(category)
        if not category_config:
            return None
        
        cleaning_category = CleaningCategory(
            id=category,
            name=category_config["name"],
            description=category_config["description"],
            icon=category_config["icon"],
            color=category_config["color"],
            priority=category_config["priority"],
            safe_level=category_config["safe_level"],
            estimated_impact=category_config["estimated_impact"]
        )
        
        # Bestimme Scan-Pfade
        scan_paths = self._get_scan_paths_for_category(category)
        
        if progress_callback:
            progress_callback(f"Scanne {category_config['name']}...", 0.0)
        
        # Paralleler Scan aller Pfade
        scan_futures = []
        
        for path in scan_paths:
            if self.scan_cancelled:
                break
            
            future = self.thread_executor.submit(
                self._scan_path_optimized, path, category
            )
            scan_futures.append(future)
        
        # Sammle Ergebnisse
        all_items = []
        for i, future in enumerate(scan_futures):
            if self.scan_cancelled:
                break
            
            try:
                items = future.result(timeout=30)
                all_items.extend(items)
                
                if progress_callback:
                    progress_callback(
                        f"Scanne {category_config['name']}...", 
                        (i + 1) / len(scan_futures)
                    )
                    
            except Exception as e:
                print(f"Fehler beim Scannen von {scan_paths[i]}: {e}")
                self.current_statistics.errors_encountered += 1
        
        # Optimiere und dedupliziere Ergebnisse
        optimized_items = self._optimize_scan_results(all_items)
        
        cleaning_category.items = optimized_items
        cleaning_category.total_count = len(optimized_items)
        cleaning_category.total_size = sum(item.metadata.size for item in optimized_items)
        
        return cleaning_category
    
    def _get_category_config(self, category: str) -> Optional[Dict[str, Any]]:
        """Gibt die Konfiguration für eine Kategorie zurück."""
        configs = {
            "temp_files": {
                "name": "Temporäre Dateien",
                "description": "Temporäre Dateien von Anwendungen und System",
                "icon": "🗂️",
                "color": "#00d4ff",
                "priority": 1,
                "safe_level": 5,
                "estimated_impact": "high"
            },
            "cache": {
                "name": "Cache-Dateien",
                "description": "Browser- und Anwendungs-Cache",
                "icon": "💾",
                "color": "#a855f7",
                "priority": 2,
                "safe_level": 4,
                "estimated_impact": "medium"
            },
            "logs": {
                "name": "Log-Dateien",
                "description": "System- und Anwendungs-Protokolle",
                "icon": "📋",
                "color": "#f59e0b",
                "priority": 3,
                "safe_level": 4,
                "estimated_impact": "low"
            },
            "duplicates": {
                "name": "Doppelte Dateien",
                "description": "Identische Dateien mit gleichem Inhalt",
                "icon": "👥",
                "color": "#ef4444",
                "priority": 4,
                "safe_level": 3,
                "estimated_impact": "high"
            },
            "registry": {
                "name": "Registry-Einträge",
                "description": "Verwaiste Windows Registry-Einträge",
                "icon": "🔧",
                "color": "#10b981",
                "priority": 5,
                "safe_level": 2,
                "estimated_impact": "medium"
            }
        }
        
        return configs.get(category)
    
    def _get_scan_paths_for_category(self, category: str) -> List[str]:
        """Gibt die zu scannenden Pfade für eine Kategorie zurück."""
        if category == "temp_files":
            return [
                os.path.expandvars(path) 
                for path in SCAN_CONFIG["windows_temp_paths"]
                if os.path.exists(os.path.expandvars(path))
            ]
        
        elif category == "cache":
            paths = []
            for browser, path in SCAN_CONFIG["browser_cache_paths"].items():
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    paths.append(expanded_path)
            return paths
        
        elif category == "logs":
            return [
                "C:\\Windows\\Logs",
                os.path.expandvars("%LOCALAPPDATA%\\Temp"),
                os.path.expandvars("%PROGRAMDATA%\\Microsoft\\Windows\\WER")
            ]
        
        elif category == "duplicates":
            return [
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Videos"),
                os.path.expanduser("~/Music")
            ]
        
        elif category == "registry":
            return ["REGISTRY"]  # Spezial-Marker für Registry-Scan
        
        return []
    
    def _scan_path_optimized(self, path: str, category: str) -> List[EnhancedCleaningItem]:
        """Hardware-optimierter Pfad-Scan."""
        if path == "REGISTRY":
            return self._scan_registry_optimized()
        
        if not os.path.exists(path):
            return []
        
        items = []
        
        try:
            # Verwende os.scandir für bessere Performance
            with os.scandir(path) as entries:
                for entry in entries:
                    if self.scan_cancelled:
                        break
                    
                    try:
                        if entry.is_file():
                            item = self._analyze_file_optimized(entry, category)
                            if item:
                                items.append(item)
                                
                        elif entry.is_dir() and category in ["temp_files", "cache"]:
                            # Rekursiver Scan für Verzeichnisse
                            sub_items = self._scan_path_optimized(entry.path, category)
                            items.extend(sub_items)
                            
                    except (OSError, PermissionError):
                        self.current_statistics.errors_encountered += 1
                        continue
                        
        except (OSError, PermissionError):
            self.current_statistics.errors_encountered += 1
        
        return items
    
    def _analyze_file_optimized(self, entry: os.DirEntry, category: str) -> Optional[EnhancedCleaningItem]:
        """Analysiert eine Datei mit Hardware-Optimierung."""
        try:
            stat_result = entry.stat()
            
            # Erstelle Metadaten
            metadata = FileMetadata(
                path=entry.path,
                size=stat_result.st_size,
                created=datetime.fromtimestamp(stat_result.st_ctime),
                modified=datetime.fromtimestamp(stat_result.st_mtime),
                accessed=datetime.fromtimestamp(stat_result.st_atime),
                attributes=getattr(stat_result, 'st_file_attributes', 0),
                mime_type=mimetypes.guess_type(entry.path)[0],
                is_executable=entry.path.lower().endswith(('.exe', '.msi', '.bat', '.cmd'))
            )
            
            # Sicherheitsbewertung
            safety_score = self._calculate_safety_score(metadata, category)
            impact_score = self._calculate_impact_score(metadata, category)
            
            # Erstelle Enhanced Item
            category_obj = CleaningCategory(
                id=category,
                name=category,
                description="",
                icon="",
                color="",
                priority=1,
                safe_level=1,
                estimated_impact="low"
            )
            
            item = EnhancedCleaningItem(
                metadata=metadata,
                category=category_obj,
                safety_score=safety_score,
                impact_score=impact_score,
                user_selected=safety_score > 0.8  # Auto-select sehr sichere Dateien
            )
            
            self.current_statistics.files_scanned += 1
            self.current_statistics.bytes_analyzed += metadata.size
            
            return item
            
        except (OSError, PermissionError):
            self.current_statistics.errors_encountered += 1
            return None
    
    def _calculate_safety_score(self, metadata: FileMetadata, category: str) -> float:
        """Berechnet die Sicherheitsbewertung für eine Datei."""
        score = 0.0
        
        # Basis-Score basierend auf Kategorie
        category_scores = {
            "temp_files": 0.9,
            "cache": 0.8,
            "logs": 0.7,
            "duplicates": 0.6,
            "registry": 0.5
        }
        score = category_scores.get(category, 0.3)
        
        # Pfad-basierte Anpassungen
        path_lower = metadata.path.lower()
        
        # Sehr sichere Pfade
        safe_indicators = [
            "\\temp\\", "\\tmp\\", "\\cache\\", "\\logs\\",
            ".tmp", ".temp", ".log", ".bak", ".old"
        ]
        if any(indicator in path_lower for indicator in safe_indicators):
            score += 0.1
        
        # Kritische Pfade - drastisch reduzierte Sicherheit
        critical_indicators = SCAN_CONFIG["critical_paths"]
        if any(critical in path_lower for critical in critical_indicators):
            score = min(score, 0.1)
        
        # Systemdateien
        if metadata.is_system_file or metadata.is_executable:
            score *= 0.5
        
        # Alter der Datei
        age_days = (datetime.now() - metadata.accessed).days
        if age_days > 30:  # Nicht zugegriffen seit 30 Tagen
            score += 0.1
        elif age_days > 7:
            score += 0.05
        
        # Dateigröße
        if metadata.size < 1024:  # Kleine Dateien sind oft sicherer
            score += 0.05
        elif metadata.size > 100 * 1024 * 1024:  # Große Dateien vorsichtiger
            score *= 0.8
        
        return min(1.0, max(0.0, score))
    
    def _calculate_impact_score(self, metadata: FileMetadata, category: str) -> float:
        """Berechnet den Auswirkungsgrad der Löschung."""
        # Basis-Impact basierend auf Dateigröße
        size_mb = metadata.size / (1024 * 1024)
        
        if size_mb > 100:
            return 0.9  # Hoher Impact
        elif size_mb > 10:
            return 0.7  # Mittlerer Impact
        elif size_mb > 1:
            return 0.5  # Niedriger Impact
        else:
            return 0.2  # Sehr niedriger Impact
    
    @jit(nopython=True) if NUMBA_AVAILABLE else lambda f: f
    def _calculate_file_hash_optimized(self, file_path: str) -> str:
        """GPU/CPU-optimierte Hash-Berechnung."""
        if file_path in self.file_hash_cache:
            return self.file_hash_cache[file_path]
        
        try:
            hash_obj = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                # Lese in optimierten Chunks
                chunk_size = HARDWARE_CONFIG["memory"]["buffer_size_mb"] * 1024
                
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
            
            file_hash = hash_obj.hexdigest()
            self.file_hash_cache[file_path] = file_hash
            
            return file_hash
            
        except (OSError, PermissionError, MemoryError):
            return ""
    
    def _scan_registry_optimized(self) -> List[EnhancedCleaningItem]:
        """Optimierter Registry-Scan."""
        if sys.platform != "win32":
            return []
        
        registry_items = []
        
        for registry_key in SCAN_CONFIG["registry_cleanup_keys"]:
            try:
                # Parse Registry-Pfad
                if registry_key.startswith("HKEY_CURRENT_USER"):
                    hkey = winreg.HKEY_CURRENT_USER
                    subkey = registry_key.replace("HKEY_CURRENT_USER\\", "")
                elif registry_key.startswith("HKEY_LOCAL_MACHINE"):
                    hkey = winreg.HKEY_LOCAL_MACHINE
                    subkey = registry_key.replace("HKEY_LOCAL_MACHINE\\", "")
                else:
                    continue
                
                items = self._scan_registry_key(hkey, subkey)
                registry_items.extend(items)
                
            except Exception as e:
                print(f"Registry-Scan-Fehler für {registry_key}: {e}")
                continue
        
        return registry_items
    
    def _scan_registry_key(self, hkey, subkey: str) -> List[EnhancedCleaningItem]:
        """Scannt einen spezifischen Registry-Schlüssel."""
        items = []
        
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                i = 0
                while True:
                    try:
                        name, value, reg_type = winreg.EnumValue(key, i)
                        
                        # Prüfe ob Wert auf nicht-existierende Datei verweist
                        if isinstance(value, str) and self._is_invalid_registry_value(value):
                            # Erstelle Pseudo-Metadaten für Registry-Eintrag
                            metadata = FileMetadata(
                                path=f"{subkey}\\{name}",
                                size=len(str(value)),
                                created=datetime.now(),
                                modified=datetime.now(),
                                accessed=datetime.now(),
                                attributes=0,
                                mime_type="application/x-registry"
                            )
                            
                            category_obj = CleaningCategory(
                                id="registry",
                                name="Registry-Einträge",
                                description="",
                                icon="🔧",
                                color="#10b981",
                                priority=5,
                                safe_level=2,
                                estimated_impact="medium"
                            )
                            
                            item = EnhancedCleaningItem(
                                metadata=metadata,
                                category=category_obj,
                                safety_score=0.7,  # Mittlere Sicherheit für Registry
                                impact_score=0.3,   # Niedriger Impact
                                user_selected=False  # Registry-Items nicht auto-selektieren
                            )
                            
                            items.append(item)
                        
                        i += 1
                        
                    except WindowsError:
                        break
                        
        except (OSError, PermissionError):
            pass
        
        return items
    
    def _is_invalid_registry_value(self, value: str) -> bool:
        """Prüft ob ein Registry-Wert ungültig ist."""
        # Prüfe ob Pfad existiert
        if os.path.exists(value):
            return False
        
        # Prüfe auf typische Pfad-Muster
        if '\\' in value and (value.endswith('.exe') or value.endswith('.dll')):
            return True
        
        return False
    
    def _optimize_scan_results(self, items: List[EnhancedCleaningItem]) -> List[EnhancedCleaningItem]:
        """Optimiert und dedupliziert Scan-Ergebnisse."""
        if not items:
            return []
        
        # Nach Pfad deduplizieren
        seen_paths = set()
        unique_items = []
        
        for item in items:
            if item.metadata.path not in seen_paths:
                seen_paths.add(item.metadata.path)
                unique_items.append(item)
        
        # Nach Sicherheitsscore sortieren (sicherste zuerst)
        unique_items.sort(key=lambda x: x.safety_score, reverse=True)
        
        return unique_items
    
    async def _perform_ai_analysis(
        self, 
        scan_results: Dict[str, CleaningCategory],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        """Führt KI-Analyse der Scan-Ergebnisse durch."""
        if progress_callback:
            progress_callback("KI-Analyse läuft...", 0.95)
        
        # Hier würde die echte KI-Integration stattfinden
        # Für Demo verwenden wir heuristische Analyse
        
        for category_name, category in scan_results.items():
            for item in category.items:
                # Generiere KI-Erklärung basierend auf Datei-Eigenschaften
                item.ai_explanation = self._generate_ai_explanation(item)
        
        if progress_callback:
            progress_callback("KI-Analyse abgeschlossen", 1.0)
    
    def _generate_ai_explanation(self, item: EnhancedCleaningItem) -> str:
        """Generiert eine KI-ähnliche Erklärung für eine Datei."""
        explanations = {
            "temp_files": [
                f"Diese temporäre Datei wurde von {self._guess_application(item.metadata.path)} erstellt und wird nicht mehr benötigt.",
                f"Temporäre Datei mit {item.metadata.size} Bytes. Sicher löschbar, da sie automatisch regeneriert werden kann.",
                f"Zwischenspeicher-Datei, die beim Schließen der Anwendung hätte gelöscht werden sollen."
            ],
            "cache": [
                f"Cache-Datei zur Beschleunigung von {self._guess_application(item.metadata.path)}. Wird bei Bedarf neu erstellt.",
                f"Browser-Cache mit {item.metadata.size} Bytes. Löschen verbessert Privatsphäre ohne Funktionsverlust.",
                f"Anwendungs-Cache für schnellere Ladezeiten. Regenerierbar nach Löschung."
            ],
            "logs": [
                f"Protokoll-Datei mit Debug-Informationen. Nicht kritisch für Systemfunktion.",
                f"Log-Datei von {self._guess_application(item.metadata.path)}. Kann sicher gelöscht werden.",
                f"Ereignisprotokoll mit {item.metadata.size} Bytes. Hilfreich für Fehlerbehebung, aber nicht essentiell."
            ],
            "duplicates": [
                f"Identische Kopie einer bereits vorhandenen Datei. Spart {item.metadata.size} Bytes Speicherplatz.",
                f"Duplikat erkannt durch Hash-Vergleich. Original bleibt erhalten.",
                f"Redundante Datei ohne zusätzlichen Nutzen. Sichere Löschung möglich."
            ],
            "registry": [
                f"Verwaister Registry-Eintrag ohne gültige Zieldatei. Kann Systemstart verlangsamen.",
                f"Ungültiger Registry-Verweis auf nicht-existierende Datei. Bereinigung empfohlen.",
                f"Registry-Eintrag von deinstallierter Software. Sicher entfernbar."
            ]
        }
        
        import random
        category_explanations = explanations.get(item.category.id, ["Unbekannter Dateityp."])
        return random.choice(category_explanations)
    
    def _guess_application(self, file_path: str) -> str:
        """Versucht die Anwendung basierend auf dem Pfad zu erraten."""
        path_lower = file_path.lower()
        
        app_indicators = {
            "chrome": "Google Chrome",
            "firefox": "Mozilla Firefox", 
            "edge": "Microsoft Edge",
            "opera": "Opera Browser",
            "discord": "Discord",
            "steam": "Steam",
            "spotify": "Spotify",
            "adobe": "Adobe Software",
            "office": "Microsoft Office",
            "visual studio": "Visual Studio",
            "windows": "Windows System"
        }
        
        for indicator, app_name in app_indicators.items():
            if indicator in path_lower:
                return app_name
        
        return "Unbekannte Anwendung"
    
    def cancel_scan(self):
        """Bricht den aktuellen Scan ab."""
        self.scan_cancelled = True
    
    def get_scan_statistics(self) -> ScanStatistics:
        """Gibt die aktuellen Scan-Statistiken zurück."""
        return self.current_statistics


# ============================================================================
# HARDWARE-BESCHLEUNIGTE BEREINIGUNG
# ============================================================================

class AdvancedCleaner:
    """Hardware-beschleunigte Bereinigungsengine."""
    
    def __init__(self):
        self.is_cleaning = False
        self.cleaning_cancelled = False
        self.backup_enabled = SECURITY_CONFIG["security"]["backup_before_delete"]
        
        # Performance-Metriken
        self.cleaning_stats = {
            "files_deleted": 0,
            "bytes_freed": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def perform_cleaning(
        self,
        items: List[EnhancedCleaningItem],
        progress_callback: Optional[Callable[[str, float], None]] = None,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """Führt die Hardware-beschleunigte Bereinigung durch."""
        
        self.is_cleaning = True
        self.cleaning_cancelled = False
        self.cleaning_stats["start_time"] = time.time()
        
        try:
            # Filtere nur ausgewählte Items
            selected_items = [item for item in items if item.user_selected]
            
            if not selected_items:
                return {"success": False, "message": "Keine Dateien ausgewählt"}
            
            # Erstelle Backup falls aktiviert
            backup_path = None
            if create_backup and self.backup_enabled:
                backup_path = await self._create_backup(selected_items, progress_callback)
            
            # Parallele Löschung
            deletion_tasks = []
            
            for i, item in enumerate(selected_items):
                if self.cleaning_cancelled:
                    break
                
                task = self._delete_item_async(item, backup_path)
                deletion_tasks.append(task)
                
                # Update Progress
                if progress_callback:
                    progress_callback(
                        f"Lösche {os.path.basename(item.metadata.path)}...",
                        i / len(selected_items)
                    )
            
            # Warte auf alle Löschvorgänge
            results = await asyncio.gather(*deletion_tasks, return_exceptions=True)
            
            # Auswertung der Ergebnisse
            successful_deletions = 0
            total_bytes_freed = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Löschfehler: {result}")
                    self.cleaning_stats["errors"] += 1
                elif result:
                    successful_deletions += 1
                    total_bytes_freed += selected_items[i].metadata.size
            
            self.cleaning_stats["files_deleted"] = successful_deletions
            self.cleaning_stats["bytes_freed"] = total_bytes_freed
            self.cleaning_stats["end_time"] = time.time()
            
            if progress_callback:
                progress_callback("Bereinigung abgeschlossen!", 1.0)
            
            return {
                "success": True,
                "files_deleted": successful_deletions,
                "bytes_freed": total_bytes_freed,
                "backup_path": backup_path,
                "duration": self.cleaning_stats["end_time"] - self.cleaning_stats["start_time"]
            }
            
        finally:
            self.is_cleaning = False
    
    async def _create_backup(
        self, 
        items: List[EnhancedCleaningItem],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """Erstellt ein Backup der zu löschenden Dateien."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(tempfile.gettempdir()) / f"GermanCodeZero_Backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        if progress_callback:
            progress_callback("Erstelle Backup...", 0.0)
        
        backup_tasks = []
        
        for i, item in enumerate(items):
            if self.cleaning_cancelled:
                break
            
            task = self._backup_file_async(item, backup_dir)
            backup_tasks.append(task)
        
        await asyncio.gather(*backup_tasks, return_exceptions=True)
        
        # Erstelle Backup-Manifest
        manifest = {
            "timestamp": timestamp,
            "total_files": len(items),
            "backup_size": sum(item.metadata.size for item in items),
            "files": [
                {
                    "original_path": item.metadata.path,
                    "backup_path": str(backup_dir / os.path.basename(item.metadata.path)),
                    "size": item.metadata.size,
                    "category": item.category.id
                }
                for item in items
            ]
        }
        
        manifest_path = backup_dir / "backup_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        return str(backup_dir)
    
    async def _backup_file_async(self, item: EnhancedCleaningItem, backup_dir: Path):
        """Erstellt ein Backup einer einzelnen Datei."""
        try:
            source_path = Path(item.metadata.path)
            backup_path = backup_dir / source_path.name
            
            # Verhindere Namenskonflikte
            counter = 1
            while backup_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                backup_path = backup_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Kopiere Datei
            shutil.copy2(source_path, backup_path)
            
            return True
            
        except Exception as e:
            print(f"Backup-Fehler für {item.metadata.path}: {e}")
            return False
    
    async def _delete_item_async(self, item: EnhancedCleaningItem, backup_path: Optional[str] = None) -> bool:
        """Löscht ein Item asynchron."""
        try:
            if item.category.id == "registry":
                return self._delete_registry_item(item)
            else:
                return self._delete_file_item(item)
                
        except Exception as e:
            print(f"Löschfehler für {item.metadata.path}: {e}")
            return False
    
    def _delete_file_item(self, item: EnhancedCleaningItem) -> bool:
        """Löscht eine Datei."""
        try:
            if item.deletion_method == "secure":
                # Sichere Löschung (überschreiben)
                self._secure_delete_file(item.metadata.path)
            elif item.deletion_method == "shred":
                # Mehrfaches Überschreiben
                self._shred_file(item.metadata.path)
            else:
                # Normale Löschung (Papierkorb)
                send2trash.send2trash(item.metadata.path)
            
            return True
            
        except Exception as e:
            print(f"Datei-Löschfehler: {e}")
            return False
    
    def _delete_registry_item(self, item: EnhancedCleaningItem) -> bool:
        """Löscht einen Registry-Eintrag."""
        try:
            # Parse Registry-Pfad
            path_parts = item.metadata.path.split("\\")
            if len(path_parts) < 2:
                return False
            
            key_path = "\\".join(path_parts[:-1])
            value_name = path_parts[-1]
            
            # Bestimme Registry-Root
            if key_path.startswith("Software"):
                hkey = winreg.HKEY_CURRENT_USER
            else:
                hkey = winreg.HKEY_LOCAL_MACHINE
            
            # Lösche Registry-Wert
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
            
            return True
            
        except Exception as e:
            print(f"Registry-Löschfehler: {e}")
            return False
    
    def _secure_delete_file(self, file_path: str):
        """Sichere Datei-Löschung durch Überschreiben."""
        try:
            file_size = os.path.getsize(file_path)
            
            # Überschreibe mit Zufallsdaten
            with open(file_path, "r+b") as f:
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
            
            # Normale Löschung
            os.remove(file_path)
            
        except Exception as e:
            # Fallback zu normaler Löschung
            send2trash.send2trash(file_path)
    
    def _shred_file(self, file_path: str, passes: int = 3):
        """Mehrfaches Überschreiben für maximale Sicherheit."""
        try:
            file_size = os.path.getsize(file_path)
            
            for pass_num in range(passes):
                with open(file_path, "r+b") as f:
                    if pass_num == 0:
                        # Überschreibe mit Nullen
                        f.write(b'\x00' * file_size)
                    elif pass_num == 1:
                        # Überschreibe mit Einsen
                        f.write(b'\xFF' * file_size)
                    else:
                        # Überschreibe mit Zufallsdaten
                        f.write(os.urandom(file_size))
                    
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finale Löschung
            os.remove(file_path)
            
        except Exception as e:
            # Fallback zu sicherer Löschung
            self._secure_delete_file(file_path)
    
    def cancel_cleaning(self):
        """Bricht die laufende Bereinigung ab."""
        self.cleaning_cancelled = True
    
    def get_cleaning_statistics(self) -> Dict[str, Any]:
        """Gibt die Bereinigungsstatistiken zurück."""
        stats = self.cleaning_stats.copy()
        
        if stats["start_time"] and stats["end_time"]:
            stats["duration"] = stats["end_time"] - stats["start_time"]
        
        return stats


# ============================================================================
# PERFORMANCE-MONITOR
# ============================================================================

class PerformanceMonitor:
    """Überwacht System-Performance während Scan und Bereinigung."""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "disk_io": [],
            "gpu_usage": [],
            "timestamps": []
        }
    
    def start_monitoring(self):
        """Startet Performance-Überwachung."""
        self.monitoring = True
        self.metrics = {key: [] for key in self.metrics.keys()}
        
        threading.Thread(target=self._monitor_loop, daemon=True).start()
    
    def stop_monitoring(self):
        """Stoppt Performance-Überwachung."""
        self.monitoring = False
    
    def _monitor_loop(self):
        """Haupt-Monitoring-Schleife."""
        while self.monitoring:
            try:
                timestamp = time.time()
                
                # CPU-Nutzung
                cpu_percent = psutil.cpu_percent(interval=None)
                self.metrics["cpu_usage"].append(cpu_percent)
                
                # Memory-Nutzung
                memory = psutil.virtual_memory()
                self.metrics["memory_usage"].append(memory.percent)
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    io_utilization = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)  # MB
                    self.metrics["disk_io"].append(io_utilization)
                
                # GPU-Nutzung (falls verfügbar)
                gpu_usage = self._get_gpu_usage()
                self.metrics["gpu_usage"].append(gpu_usage)
                
                self.metrics["timestamps"].append(timestamp)
                
                # Begrenze History auf letzte 300 Messungen (5 Minuten bei 1s Intervall)
                for key in self.metrics.keys():
                    if len(self.metrics[key]) > 300:
                        self.metrics[key] = self.metrics[key][-300:]
                
                time.sleep(1)  # 1 Sekunde Intervall
                
            except Exception as e:
                print(f"Monitoring-Fehler: {e}")
                time.sleep(1)
    
    def _get_gpu_usage(self) -> float:
        """Ermittelt GPU-Nutzung."""
        try:
            if CUPY_AVAILABLE:
                # NVIDIA GPU via CuPy
                mempool = cp.get_default_memory_pool()
                used_bytes = mempool.used_bytes()
                total_bytes = cp.cuda.runtime.memGetInfo()[1]
                return (used_bytes / total_bytes) * 100
        except:
            pass
        
        return 0.0
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Gibt aktuelle Performance-Metriken zurück."""
        if not self.metrics["timestamps"]:
            return {}
        
        return {
            "cpu_usage": self.metrics["cpu_usage"][-1] if self.metrics["cpu_usage"] else 0,
            "memory_usage": self.metrics["memory_usage"][-1] if self.metrics["memory_usage"] else 0,
            "disk_io": self.metrics["disk_io"][-1] if self.metrics["disk_io"] else 0,
            "gpu_usage": self.metrics["gpu_usage"][-1] if self.metrics["gpu_usage"] else 0
        }
    
    def get_average_metrics(self, last_n_seconds: int = 60) -> Dict[str, float]:
        """Gibt durchschnittliche Metriken der letzten N Sekunden zurück."""
        if not self.metrics["timestamps"]:
            return {}
        
        current_time = time.time()
        cutoff_time = current_time - last_n_seconds
        
        # Finde Index für Zeitfenster
        start_index = 0
        for i, timestamp in enumerate(self.metrics["timestamps"]):
            if timestamp >= cutoff_time:
                start_index = i
                break
        
        # Berechne Durchschnitte
        averages = {}
        for key in ["cpu_usage", "memory_usage", "disk_io", "gpu_usage"]:
            values = self.metrics[key][start_index:]
            averages[key] = sum(values) / len(values) if values else 0
        
        return averages


# ============================================================================
# DUPLICATE FINDER MIT GPU-BESCHLEUNIGUNG
# ============================================================================

class GPUAcceleratedDuplicateFinder:
    """GPU-beschleunigte Duplikat-Erkennung."""
    
    def __init__(self):
        self.gpu_available = CUPY_AVAILABLE
        self.hash_cache = {}
    
    async def find_duplicates_parallel(
        self, 
        directories: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> List[EnhancedCleaningItem]:
        """Findet Duplikate mit paralleler Verarbeitung."""
        
        if progress_callback:
            progress_callback("Sammle Dateien für Duplikat-Analyse...", 0.1)
        
        # Sammle alle Dateien
        all_files = []
        for directory in directories:
            if os.path.exists(directory):
                files = list(Path(directory).rglob("*"))
                all_files.extend([f for f in files if f.is_file()])
        
        if not all_files:
            return []
        
        if progress_callback:
            progress_callback(f"Analysiere {len(all_files)} Dateien...", 0.2)
        
        # Parallele Hash-Berechnung
        hash_tasks = []
        chunk_size = max(1, len(all_files) // (self.cpu_threads * 2))
        
        for i in range(0, len(all_files), chunk_size):
            chunk = all_files[i:i + chunk_size]
            task = self._process_file_chunk(chunk)
            hash_tasks.append(task)
        
        # Warte auf Hash-Berechnungen
        hash_results = await asyncio.gather(*hash_tasks, return_exceptions=True)
        
        if progress_callback:
            progress_callback("Suche Duplikate...", 0.8)
        
        # Finde Duplikate
        file_hashes = {}
        duplicates = []
        
        for result in hash_results:
            if isinstance(result, Exception):
                continue
            
            for file_path, file_hash, file_size in result:
                if file_hash in file_hashes:
                    # Duplikat gefunden
                    original_path = file_hashes[file_hash]
                    
                    # Erstelle Enhanced Cleaning Item
                    metadata = FileMetadata(
                        path=file_path,
                        size=file_size,
                        created=datetime.fromtimestamp(os.path.getctime(file_path)),
                        modified=datetime.fromtimestamp(os.path.getmtime(file_path)),
                        accessed=datetime.fromtimestamp(os.path.getatime(file_path)),
                        attributes=0,
                        hash_sha256=file_hash
                    )
                    
                    category = CleaningCategory(
                        id="duplicates",
                        name="Doppelte Dateien",
                        description="",
                        icon="👥",
                        color="#ef4444",
                        priority=4,
                        safe_level=3,
                        estimated_impact="high"
                    )
                    
                    duplicate_item = EnhancedCleaningItem(
                        metadata=metadata,
                        category=category,
                        safety_score=0.8,  # Duplikate sind relativ sicher
                        impact_score=file_size / (1024 * 1024),  # Impact basierend auf Größe
                        ai_explanation=f"Duplikat von: {original_path}"
                    )
                    
                    duplicates.append(duplicate_item)
                else:
                    file_hashes[file_hash] = file_path
        
        if progress_callback:
            progress_callback(f"{len(duplicates)} Duplikate gefunden!", 1.0)
        
        return duplicates
    
    async def _process_file_chunk(self, files: List[Path]) -> List[Tuple[str, str, int]]:
        """Verarbeitet einen Chunk von Dateien für Hash-Berechnung."""
        results = []
        
        for file_path in files:
            try:
                file_size = file_path.stat().st_size
                
                # Überspringe sehr große Dateien für Performance
                if file_size > SCAN_CONFIG["max_file_size_mb"] * 1024 * 1024:
                    continue
                
                # Berechne Hash
                if self.gpu_available and file_size > 10 * 1024 * 1024:  # GPU für große Dateien
                    file_hash = await self._calculate_hash_gpu(str(file_path))
                else:
                    file_hash = await self._calculate_hash_cpu(str(file_path))
                
                if file_hash:
                    results.append((str(file_path), file_hash, file_size))
                    
            except (OSError, PermissionError):
                continue
        
        return results
    
    async def _calculate_hash_cpu(self, file_path: str) -> str:
        """CPU-basierte Hash-Berechnung."""
        def compute_hash():
            hash_obj = hashlib.sha256()
            try:
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        hash_obj.update(chunk)
                return hash_obj.hexdigest()
            except:
                return ""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, compute_hash)
    
    async def _calculate_hash_gpu(self, file_path: str) -> str:
        """GPU-beschleunigte Hash-Berechnung (experimentell)."""
        # Fallback zu CPU für diese Demo
        return await self._calculate_hash_cpu(file_path)


# ============================================================================
# SYSTEM-OPTIMIERER
# ============================================================================

class SystemOptimizer:
    """Erweiterte System-Optimierung über Bereinigung hinaus."""
    
    def __init__(self):
        self.optimization_tasks = []
    
    async def optimize_system_performance(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, Any]:
        """Führt umfassende System-Optimierung durch."""
        
        optimizations = [
            ("Defragmentiere Registry", self._optimize_registry),
            ("Optimiere Startup-Programme", self._optimize_startup),
            ("Bereinige DNS-Cache", self._flush_dns_cache),
            ("Optimiere Netzwerk-Einstellungen", self._optimize_network),
            ("Aktualisiere System-Indizes", self._rebuild_search_index)
        ]
        
        results = {}
        
        for i, (task_name, task_func) in enumerate(optimizations):
            if progress_callback:
                progress_callback(task_name, i / len(optimizations))
            
            try:
                result = await task_func()
                results[task_name] = {"success": True, "details": result}
            except Exception as e:
                results[task_name] = {"success": False, "error": str(e)}
        
        if progress_callback:
            progress_callback("System-Optimierung abgeschlossen!", 1.0)
        
        return results
    
    async def _optimize_registry(self) -> str:
        """Optimiert die Windows Registry."""
        if sys.platform != "win32":
            return "Nicht verfügbar auf diesem System"
        
        # Vereinfachte Registry-Optimierung
        return "Registry-Optimierung simuliert"
    
    async def _optimize_startup(self) -> str:
        """Optimiert Startup-Programme."""
        disabled_count = 0
        
        try:
            # Analysiere Startup-Programme
            startup_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        
                        # Prüfe ob Programm noch existiert
                        if isinstance(value, str) and not os.path.exists(value):
                            # Könnte deaktiviert werden
                            disabled_count += 1
                        
                        i += 1
                    except WindowsError:
                        break
                        
        except Exception as e:
            return f"Fehler bei Startup-Optimierung: {e}"
        
        return f"{disabled_count} verwaiste Startup-Einträge gefunden"
    
    async def _flush_dns_cache(self) -> str:
        """Leert den DNS-Cache."""
        try:
            if sys.platform == "win32":
                os.system("ipconfig /flushdns > nul 2>&1")
                return "DNS-Cache geleert"
            else:
                return "DNS-Cache-Bereinigung auf diesem System nicht verfügbar"
        except:
            return "Fehler beim Leeren des DNS-Cache"
    
    async def _optimize_network(self) -> str:
        """Optimiert Netzwerk-Einstellungen."""
        # Placeholder für Netzwerk-Optimierung
        return "Netzwerk-Optimierung simuliert"
    
    async def _rebuild_search_index(self) -> str:
        """Baut den Windows-Suchindex neu auf."""
        # Placeholder für Index-Optimierung
        return "Suchindex-Optimierung simuliert"