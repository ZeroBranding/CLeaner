"""
💾 Database Manager with AES-256 encryption
Handles conversation history, cache, and secure API key storage
"""

import sqlite3
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Secure database manager with encryption support"""
    
    def __init__(self, db_path: str = "holographic_ai.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        self._init_database()
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = Path(".encryption_key")
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            password = os.urandom(32)  # Random password
            salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Save key securely
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Hide the key file
            try:
                os.chmod(key_file, 0o600)
            except:
                pass
                
            return key
    
    def _init_database(self):
        """Initialize database with required tables"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            cursor = self.connection.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    ai_provider TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER DEFAULT 0,
                    response_time REAL DEFAULT 0.0
                )
            ''')
            
            # System stats cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stats_json TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Encrypted API keys
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    provider TEXT PRIMARY KEY,
                    encrypted_key TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME
                )
            ''')
            
            # User preferences
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def store_conversation(self, session_id: str, user_message: str, 
                          ai_response: str, ai_provider: str, 
                          tokens_used: int = 0, response_time: float = 0.0):
        """Store conversation in database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO conversations 
                (session_id, user_message, ai_response, ai_provider, tokens_used, response_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, user_message, ai_response, ai_provider, tokens_used, response_time))
            
            self.connection.commit()
            logger.debug(f"Conversation stored for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT user_message, ai_response, ai_provider, timestamp, tokens_used, response_time
                FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def store_api_key(self, provider: str, api_key: str):
        """Store encrypted API key"""
        try:
            encrypted_key = self.cipher_suite.encrypt(api_key.encode())
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO api_keys (provider, encrypted_key, last_used)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (provider, encrypted_key.decode()))
            
            self.connection.commit()
            logger.info(f"API key stored for provider: {provider}")
            
        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get decrypted API key"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT encrypted_key FROM api_keys WHERE provider = ?', (provider,))
            
            row = cursor.fetchone()
            if row:
                encrypted_key = row['encrypted_key'].encode()
                decrypted_key = self.cipher_suite.decrypt(encrypted_key)
                
                # Update last used timestamp
                cursor.execute('''
                    UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE provider = ?
                ''', (provider,))
                self.connection.commit()
                
                return decrypted_key.decode()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get API key for {provider}: {e}")
            return None
    
    def store_system_stats(self, stats: SystemStats):
        """Store system statistics for historical analysis"""
        try:
            stats_json = json.dumps({
                'cpu_percent': stats.cpu_percent,
                'cpu_freq': stats.cpu_freq,
                'cpu_temp': stats.cpu_temp,
                'memory_percent': stats.memory_percent,
                'memory_used': stats.memory_used,
                'memory_total': stats.memory_total,
                'gpu_percent': stats.gpu_percent,
                'gpu_memory_used': stats.gpu_memory_used,
                'gpu_memory_total': stats.gpu_memory_total,
                'gpu_temp': stats.gpu_temp,
                'disk_usage': stats.disk_usage,
                'network_io': stats.network_io,
                'timestamp': stats.timestamp
            })
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO system_stats (stats_json) VALUES (?)
            ''', (stats_json,))
            
            self.connection.commit()
            
            # Clean old stats (keep only last 1000 entries)
            cursor.execute('''
                DELETE FROM system_stats 
                WHERE id NOT IN (
                    SELECT id FROM system_stats 
                    ORDER BY timestamp DESC 
                    LIMIT 1000
                )
            ''')
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to store system stats: {e}")
    
    def get_performance_history(self, hours: int = 24) -> List[Dict]:
        """Get performance history for charts"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT stats_json, timestamp 
                FROM system_stats 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp ASC
            '''.format(hours))
            
            rows = cursor.fetchall()
            return [{'stats': json.loads(row['stats_json']), 'timestamp': row['timestamp']} 
                   for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return []
    
    def store_preference(self, key: str, value: Any):
        """Store user preference"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, json.dumps(value)))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to store preference: {e}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['value'])
            
            return default
            
        except Exception as e:
            logger.error(f"Failed to get preference: {e}")
            return default
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")