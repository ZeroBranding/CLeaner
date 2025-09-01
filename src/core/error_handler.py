"""
Error Handler und Logging System für GermanCodeZero-Cleaner
===========================================================

Zentralisiertes Error Handling und strukturiertes Logging.
"""

import os
import sys
import logging
import traceback
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
from enum import Enum
import json

from config import DEBUG_CONFIG, get_log_dir


# ============================================================================
# ERROR TYPES
# ============================================================================

class ErrorSeverity(Enum):
    """Fehler-Schweregrad."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Fehler-Kategorien."""
    SYSTEM = "system"
    HARDWARE = "hardware"
    SCAN = "scan"
    CLEANING = "cleaning"
    DATABASE = "database"
    AI = "ai"
    NETWORK = "network"
    UI = "ui"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class CleanerException(Exception):
    """Basis-Exception für alle Cleaner-Fehler."""
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.ERROR, details: Dict[str, Any] = None):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.now()


class ScanException(CleanerException):
    """Scan-spezifische Exception."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.SCAN, ErrorSeverity.ERROR, details)


class CleaningException(CleanerException):
    """Bereinigungs-spezifische Exception."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.CLEANING, ErrorSeverity.ERROR, details)


class HardwareException(CleanerException):
    """Hardware-spezifische Exception."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.HARDWARE, ErrorSeverity.WARNING, details)


class AIException(CleanerException):
    """AI-spezifische Exception."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.AI, ErrorSeverity.WARNING, details)


class PermissionException(CleanerException):
    """Berechtigungs-Exception."""
    def __init__(self, message: str, path: str = None):
        details = {"path": path} if path else {}
        super().__init__(message, ErrorCategory.PERMISSION, ErrorSeverity.ERROR, details)


# ============================================================================
# CUSTOM LOGGER
# ============================================================================

class CleanerLogger:
    """Erweiterter Logger mit strukturiertem Logging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.setup_logger()
    
    def setup_logger(self):
        """Konfiguriert Logger."""
        # Log Level
        level = getattr(logging, DEBUG_CONFIG["log_level"], logging.INFO)
        self.logger.setLevel(level)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File Handler
        if DEBUG_CONFIG["log_to_file"]:
            log_dir = get_log_dir()
            log_file = log_dir / f"cleaner_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = RotatingFileHandler(
                str(log_file),
                maxBytes=DEBUG_CONFIG["max_log_size_mb"] * 1024 * 1024,
                backupCount=5
            )
            file_handler.setLevel(level)
            file_formatter = JsonFormatter()
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def log_exception(self, exc: Exception, context: Dict[str, Any] = None):
        """Loggt Exception mit Kontext."""
        if isinstance(exc, CleanerException):
            log_data = {
                "error_type": exc.__class__.__name__,
                "message": str(exc),
                "category": exc.category.value,
                "severity": exc.severity.value,
                "details": exc.details,
                "context": context or {},
                "traceback": traceback.format_exc()
            }
            
            if exc.severity == ErrorSeverity.CRITICAL:
                self.logger.critical(json.dumps(log_data))
            elif exc.severity == ErrorSeverity.ERROR:
                self.logger.error(json.dumps(log_data))
            elif exc.severity == ErrorSeverity.WARNING:
                self.logger.warning(json.dumps(log_data))
            else:
                self.logger.info(json.dumps(log_data))
        else:
            # Standard Exception
            self.logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    def debug(self, message: str, **kwargs):
        """Debug-Log."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Info-Log."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning-Log."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Error-Log."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical-Log."""
        self.logger.critical(message, extra=kwargs)


# ============================================================================
# LOG FORMATTERS
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Farbiger Console-Formatter."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """JSON-Formatter für strukturiertes Logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Füge Extra-Daten hinzu
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Bei Exceptions
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info else None
            }
        
        return json.dumps(log_data, default=str)


class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Rotierender File Handler."""
    pass


# ============================================================================
# ERROR HANDLER
# ============================================================================

class ErrorHandler:
    """Zentraler Error Handler."""
    
    def __init__(self):
        self.logger = CleanerLogger(__name__)
        self.error_callbacks: Dict[ErrorCategory, List[Callable]] = {}
        self.error_count = 0
        self.error_history = []
        self.max_history = 100
    
    def register_callback(self, category: ErrorCategory, callback: Callable):
        """Registriert Error-Callback für Kategorie."""
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)
    
    def handle_exception(self, exc: Exception, context: Dict[str, Any] = None) -> bool:
        """Behandelt Exception zentral."""
        self.error_count += 1
        
        # Log Exception
        self.logger.log_exception(exc, context)
        
        # Speichere in Historie
        error_entry = {
            "timestamp": datetime.now(),
            "exception": exc,
            "context": context
        }
        self.error_history.append(error_entry)
        
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        # Rufe Callbacks auf
        if isinstance(exc, CleanerException):
            if exc.category in self.error_callbacks:
                for callback in self.error_callbacks[exc.category]:
                    try:
                        callback(exc)
                    except Exception as cb_exc:
                        self.logger.error(f"Error callback failed: {cb_exc}")
        
        # Entscheide über Recovery
        return self._should_recover(exc)
    
    def _should_recover(self, exc: Exception) -> bool:
        """Entscheidet ob Recovery möglich ist."""
        if isinstance(exc, CleanerException):
            # Kritische Fehler -> Kein Recovery
            if exc.severity == ErrorSeverity.CRITICAL:
                return False
            
            # Permission Errors -> Recovery möglich
            if exc.category == ErrorCategory.PERMISSION:
                return True
            
            # AI/Network Errors -> Recovery möglich
            if exc.category in [ErrorCategory.AI, ErrorCategory.NETWORK]:
                return True
        
        # Standard: Kein Recovery
        return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Gibt Error-Statistiken zurück."""
        stats = {
            "total_errors": self.error_count,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recent_errors": []
        }
        
        # Analysiere Historie
        for entry in self.error_history:
            exc = entry["exception"]
            
            if isinstance(exc, CleanerException):
                # Nach Kategorie
                cat = exc.category.value
                stats["errors_by_category"][cat] = stats["errors_by_category"].get(cat, 0) + 1
                
                # Nach Severity
                sev = exc.severity.value
                stats["errors_by_severity"][sev] = stats["errors_by_severity"].get(sev, 0) + 1
        
        # Letzte Fehler
        for entry in self.error_history[-10:]:
            exc = entry["exception"]
            stats["recent_errors"].append({
                "timestamp": entry["timestamp"].isoformat(),
                "type": exc.__class__.__name__,
                "message": str(exc)
            })
        
        return stats
    
    def clear_history(self):
        """Löscht Error-Historie."""
        self.error_history = []
        self.error_count = 0


# ============================================================================
# DECORATORS
# ============================================================================

def handle_errors(category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 fallback_value=None):
    """Decorator für automatisches Error Handling."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Erstelle CleanerException wenn nötig
                if not isinstance(e, CleanerException):
                    e = CleanerException(
                        str(e),
                        category=category,
                        severity=severity,
                        details={"function": func.__name__}
                    )
                
                # Handle Exception
                handler = get_error_handler()
                recovered = handler.handle_exception(e)
                
                if recovered and fallback_value is not None:
                    return fallback_value
                else:
                    raise e
        
        return wrapper
    return decorator


def retry_on_error(max_retries: int = 3, delay: float = 1.0,
                   backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """Decorator für automatische Wiederholung bei Fehlern."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        logger = CleanerLogger(__name__)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s: {e}")
                        
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= backoff
                    else:
                        break
            
            # Alle Versuche fehlgeschlagen
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


# ============================================================================
# SINGLETON
# ============================================================================

_error_handler_instance: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Gibt Singleton Error Handler zurück."""
    global _error_handler_instance
    
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    
    return _error_handler_instance


# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================

def setup_global_exception_handler():
    """Installiert globalen Exception Handler."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        handler = get_error_handler()
        exc = exc_type(exc_value)
        handler.handle_exception(exc)
    
    sys.excepthook = handle_exception


# Initialisiere bei Import
setup_global_exception_handler()