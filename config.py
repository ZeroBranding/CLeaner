"""
Konfigurationsdatei für GermanCodeZero-Cleaner
==============================================

Zentrale Konfiguration für alle App-Komponenten.
"""

import os
from pathlib import Path
from typing import Dict, List

# ============================================================================
# APP CONFIGURATION
# ============================================================================

APP_CONFIG = {
    "name": "GermanCodeZero-Cleaner",
    "version": "1.0.0",
    "author": "GermanCodeZero",
    "description": "KI-gestützte System-Optimierung mit 3D-Interface",
    "website": "https://germancodezero.com",
    "support_email": "support@germancodezero.com"
}

# ============================================================================
# UI THEMES & DESIGN
# ============================================================================

# Futuristische Dark Theme Farben
DARK_THEME = {
    "bg_primary": "#0a0a0a",      # Tiefes Schwarz
    "bg_secondary": "#1a1a1a",    # Dunkles Grau
    "bg_tertiary": "#2a2a2a",     # Mittleres Grau
    "bg_quaternary": "#3a3a3a",   # Helles Grau
    
    # Accent Colors - Cyberpunk-inspiriert
    "accent_blue": "#00d4ff",     # Cyan-Blau
    "accent_purple": "#a855f7",   # Lila
    "accent_green": "#10b981",    # Grün
    "accent_red": "#ef4444",      # Rot
    "accent_yellow": "#f59e0b",   # Gelb/Orange
    
    # Text Colors
    "text_primary": "#ffffff",    # Weiß
    "text_secondary": "#a1a1aa",  # Grau
    "text_tertiary": "#71717a",   # Dunkleres Grau
    
    # Special Effects
    "hologram_glow": "#00ffff",   # Cyan-Glow
    "neon_pink": "#ff0080",       # Neon Pink
    "electric_blue": "#0080ff",   # Elektrisches Blau
    "matrix_green": "#00ff41",    # Matrix Grün
}

# Alternative Light Theme (falls gewünscht)
LIGHT_THEME = {
    "bg_primary": "#ffffff",
    "bg_secondary": "#f8fafc", 
    "bg_tertiary": "#e2e8f0",
    "accent_blue": "#0ea5e9",
    "accent_purple": "#8b5cf6",
    "accent_green": "#059669",
    "accent_red": "#dc2626",
    "text_primary": "#1f2937",
    "text_secondary": "#6b7280",
    "hologram_glow": "#06b6d4"
}

# ============================================================================
# 3D GRAPHICS SETTINGS
# ============================================================================

GRAPHICS_CONFIG = {
    "enable_3d": True,
    "enable_animations": True,
    "enable_hologram_effects": True,
    "target_fps": 60,
    "vsync": True,
    "antialiasing": 4,  # MSAA samples
    "shadow_quality": "high",  # low, medium, high, ultra
    "particle_density": "medium",  # low, medium, high
    "glow_intensity": 0.8,
    "animation_speed": 1.0
}

# OpenGL Shader-Konfiguration
SHADER_CONFIG = {
    "vertex_shader_version": "#version 330 core",
    "fragment_shader_version": "#version 330 core",
    "max_lights": 8,
    "shadow_map_size": 2048,
    "bloom_enabled": True,
    "motion_blur_enabled": False
}

# ============================================================================
# SYSTEM SCANNING CONFIGURATION
# ============================================================================

SCAN_CONFIG = {
    # Allgemeine Scan-Einstellungen
    "max_scan_threads": 8,
    "enable_gpu_acceleration": True,
    "scan_timeout_seconds": 300,
    "max_file_size_mb": 1024,  # Maximale Dateigröße für Hash-Berechnung
    
    # Windows-spezifische Pfade
    "windows_temp_paths": [
        "%TEMP%",
        "%TMP%", 
        "%LOCALAPPDATA%\\Temp",
        "%APPDATA%\\Local\\Temp",
        "C:\\Windows\\Temp",
        "C:\\Windows\\Prefetch",
        "C:\\Windows\\SoftwareDistribution\\Download",
        "C:\\Windows\\Logs",
        "C:\\ProgramData\\Microsoft\\Windows\\WER"
    ],
    
    # Browser-Cache-Pfade
    "browser_cache_paths": {
        "chrome": "%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Cache",
        "edge": "%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\Cache",
        "firefox": "%APPDATA%\\Mozilla\\Firefox\\Profiles",
        "opera": "%APPDATA%\\Opera Software\\Opera Stable\\Cache",
        "brave": "%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Cache"
    },
    
    # Sichere Dateierweiterungen für Löschung
    "safe_extensions": {
        "temp_files": [".tmp", ".temp", ".bak", ".old", ".~", ".swp"],
        "cache": [".cache", ".dat", ".db-wal", ".db-shm", ".etl"],
        "logs": [".log", ".txt", ".out", ".err", ".dmp"],
        "thumbnails": [".db", ".thumbdata"]
    },
    
    # Kritische Pfade - NIEMALS löschen
    "critical_paths": [
        "windows", "system32", "syswow64", "program files", 
        "program files (x86)", "boot", "recovery", 
        "users\\default", "programdata\\microsoft\\windows\\systemapps"
    ],
    
    # Registry-Bereiche für Bereinigung
    "registry_cleanup_keys": [
        "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
        "HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache",
        "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs"
    ]
}

# ============================================================================
# AI/LLM CONFIGURATION
# ============================================================================

AI_CONFIG = {
    # Lokale LLM-Einstellungen
    "default_model": "llama2:7b",
    "fallback_model": "tinyllama:1.1b",
    "max_context_length": 4096,
    "temperature": 0.7,
    "top_p": 0.9,
    
    # Ollama-Konfiguration
    "ollama_host": "localhost",
    "ollama_port": 11434,
    "ollama_timeout": 30,
    
    # KI-Prompts
    "system_prompts": {
        "file_explanation": """Du bist ein hilfreicher System-Experte. Erkläre dem Benutzer auf Deutsch in 1-2 Sätzen, was diese Datei ist und warum sie sicher gelöscht werden kann. Sei präzise und verständlich.""",
        
        "cleaning_recommendation": """Du bist ein System-Optimierungs-Experte. Analysiere die Scan-Ergebnisse und gib eine konkrete Empfehlung auf Deutsch, welche Bereiche zuerst bereinigt werden sollten und warum.""",
        
        "general_assistant": """Du bist der KI-Assistent von GermanCodeZero-Cleaner. Hilf dem Benutzer bei Fragen zur System-Optimierung, erkläre gefundene Dateien und gib Empfehlungen. Antworte immer auf Deutsch und sei hilfsbereit."""
    }
}

# ============================================================================
# MONETIZATION & BUSINESS MODEL
# ============================================================================

BUSINESS_CONFIG = {
    # Freemium-Modell
    "free_tier": {
        "ad_frequency_minutes": 10,
        "max_scans_per_day": 5,
        "data_sharing_bonus_months": 1,
        "data_threshold_gb": 10,  # GB Datenmüll für kostenlosen Monat
    },
    
    # Premium-Tier
    "premium_tier": {
        "monthly_price_eur": 4.99,
        "yearly_price_eur": 49.99,
        "data_threshold_gb": 6.5,  # 35% weniger als kostenlose User
        "priority_support": True,
        "advanced_3d_effects": True,
        "detailed_reports": True
    },
    
    # Daten-Sharing-Programm
    "data_sharing": {
        "endpoint": "https://api.germancodezero.com/data-collection",
        "encryption_key": "user_specific_key",
        "anonymization_level": "high",
        "retention_days": 90,
        "data_types": ["file_metadata", "scan_statistics", "performance_metrics"]
    }
}

# ============================================================================
# HARDWARE OPTIMIZATION
# ============================================================================

HARDWARE_CONFIG = {
    # CPU-Optimierung
    "cpu": {
        "max_threads": "auto",  # oder spezifische Anzahl
        "thread_priority": "normal",  # low, normal, high
        "affinity_mask": None,  # CPU-Kerne-Maske
        "enable_hyperthreading": True
    },
    
    # RAM-Optimierung
    "memory": {
        "max_usage_percent": 80,
        "enable_memory_mapping": True,
        "buffer_size_mb": 64,
        "garbage_collection_threshold": 0.8
    },
    
    # GPU-Beschleunigung
    "gpu": {
        "enable_cuda": True,
        "enable_opencl": True,
        "preferred_device": "auto",  # auto, cuda, opencl, cpu
        "memory_limit_mb": 2048,
        "compute_capability_min": 3.5
    },
    
    # Storage-Optimierung
    "storage": {
        "enable_ssd_optimization": True,
        "read_buffer_size_kb": 256,
        "parallel_io_operations": 4,
        "enable_compression": False
    }
}

# ============================================================================
# SECURITY & PRIVACY
# ============================================================================

SECURITY_CONFIG = {
    # Datenschutz
    "privacy": {
        "collect_analytics": False,  # Standardmäßig aus
        "anonymize_paths": True,
        "encrypt_local_data": True,
        "secure_deletion": True,
        "gdpr_compliant": True
    },
    
    # Sicherheit
    "security": {
        "verify_file_signatures": True,
        "sandbox_mode": False,
        "admin_rights_required": False,
        "whitelist_mode": False,
        "backup_before_delete": True
    },
    
    # Verschlüsselung
    "encryption": {
        "algorithm": "AES-256-GCM",
        "key_derivation": "PBKDF2",
        "salt_length": 32,
        "iterations": 100000
    }
}

# ============================================================================
# DEVELOPMENT & DEBUG
# ============================================================================

DEBUG_CONFIG = {
    "enable_debug_mode": False,
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "log_to_file": True,
    "log_file_path": "logs/germancodezero_cleaner.log",
    "max_log_size_mb": 10,
    "performance_profiling": False,
    "memory_profiling": False,
    "gpu_profiling": False
}

# ============================================================================
# PLATFORM-SPECIFIC SETTINGS
# ============================================================================

PLATFORM_CONFIG = {
    "windows": {
        "enable_registry_scan": True,
        "enable_prefetch_cleanup": True,
        "enable_event_logs_cleanup": True,
        "enable_windows_update_cleanup": True,
        "enable_recycle_bin_analysis": True
    },
    
    "macos": {
        "enable_spotlight_cache": True,
        "enable_xcode_cache": True,
        "enable_browser_cache": True,
        "enable_system_logs": True
    },
    
    "linux": {
        "enable_package_cache": True,
        "enable_system_logs": True,
        "enable_thumbnail_cache": True,
        "enable_browser_cache": True
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_app_data_dir() -> Path:
    """Gibt das App-Datenverzeichnis zurück."""
    if os.name == 'nt':  # Windows
        base_dir = os.environ.get('APPDATA', '')
    elif sys.platform == 'darwin':  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support')
    else:  # Linux
        base_dir = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    
    app_dir = Path(base_dir) / "GermanCodeZero-Cleaner"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_config_file() -> Path:
    """Gibt den Pfad zur Konfigurationsdatei zurück."""
    return get_app_data_dir() / "config.json"

def get_log_dir() -> Path:
    """Gibt das Log-Verzeichnis zurück."""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir

def get_cache_dir() -> Path:
    """Gibt das Cache-Verzeichnis zurück."""
    cache_dir = get_app_data_dir() / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir

def is_admin() -> bool:
    """Prüft, ob die App mit Admin-Rechten läuft."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_system_info() -> Dict[str, str]:
    """Sammelt System-Informationen."""
    import platform
    import psutil
    
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "cpu_cores": str(psutil.cpu_count()),
        "memory_gb": str(round(psutil.virtual_memory().total / (1024**3), 1)),
        "python_version": platform.python_version()
    }