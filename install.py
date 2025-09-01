"""
Installations-Skript für GermanCodeZero-Cleaner
===============================================

Automatische Installation aller Abhängigkeiten und Setup.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path
import json

def print_banner():
    """Zeigt das Installations-Banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          🛡️  GermanCodeZero-Cleaner Installation            ║
    ║                                                              ║
    ║     KI-gestützte System-Optimierung mit 3D-Interface        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_system_requirements():
    """Prüft System-Anforderungen."""
    print("🔍 Prüfe System-Anforderungen...")
    
    # Python-Version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ erforderlich")
        print(f"   Aktuelle Version: {python_version.major}.{python_version.minor}")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Betriebssystem
    os_name = platform.system()
    if os_name not in ["Windows", "Darwin", "Linux"]:
        print(f"❌ Nicht unterstütztes Betriebssystem: {os_name}")
        return False
    
    print(f"✅ Betriebssystem: {os_name} {platform.release()}")
    
    # Speicher
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb < 4:
            print(f"⚠️  Warnung: Nur {memory_gb:.1f} GB RAM verfügbar (empfohlen: 4+ GB)")
        else:
            print(f"✅ Arbeitsspeicher: {memory_gb:.1f} GB")
    except ImportError:
        print("⚠️  Kann Speicher nicht prüfen (psutil nicht installiert)")
    
    return True

def install_python_dependencies():
    """Installiert Python-Abhängigkeiten."""
    print("\n📦 Installiere Python-Abhängigkeiten...")
    
    try:
        # Upgrade pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Installiere requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Python-Abhängigkeiten erfolgreich installiert")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei der Installation: {e}")
        return False

def setup_ollama():
    """Installiert und konfiguriert Ollama für lokale KI."""
    print("\n🤖 Richte lokale KI (Ollama) ein...")
    
    system = platform.system().lower()
    
    if system == "windows":
        ollama_url = "https://ollama.ai/download/windows"
        print("📥 Lade Ollama für Windows herunter...")
        print(f"   Bitte besuchen Sie: {ollama_url}")
        print("   Oder führen Sie aus: winget install Ollama.Ollama")
        
    elif system == "darwin":
        print("📥 Installiere Ollama für macOS...")
        print("   Führen Sie aus: brew install ollama")
        
    elif system == "linux":
        print("📥 Installiere Ollama für Linux...")
        try:
            # Lade Ollama-Installationsskript
            subprocess.check_call([
                "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
            ], shell=True)
            print("✅ Ollama erfolgreich installiert")
        except:
            print("⚠️  Manuelle Installation erforderlich: https://ollama.ai/download/linux")
    
    # Lade Standard-Modell
    print("\n🧠 Lade KI-Modell (llama2:7b)...")
    try:
        subprocess.check_call(["ollama", "pull", "llama2:7b"])
        print("✅ KI-Modell erfolgreich geladen")
    except:
        print("⚠️  KI-Modell konnte nicht geladen werden. Manuell ausführen: ollama pull llama2:7b")

def create_desktop_shortcut():
    """Erstellt Desktop-Verknüpfung."""
    print("\n🔗 Erstelle Desktop-Verknüpfung...")
    
    if platform.system() == "Windows":
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "GermanCodeZero-Cleaner.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = str(Path.cwd() / "main.py")
            shortcut.WorkingDirectory = str(Path.cwd())
            shortcut.IconLocation = str(Path.cwd() / "assets" / "icon.ico")
            shortcut.Description = "GermanCodeZero-Cleaner - KI-gestützte System-Optimierung"
            shortcut.save()
            
            print("✅ Desktop-Verknüpfung erstellt")
            
        except ImportError:
            print("⚠️  win32com nicht verfügbar. Installieren Sie: pip install pywin32")
        except Exception as e:
            print(f"⚠️  Verknüpfung konnte nicht erstellt werden: {e}")

def create_assets_directory():
    """Erstellt Assets-Verzeichnis mit Standard-Dateien."""
    print("\n🎨 Erstelle Assets...")
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Erstelle Standard-Icon (als Text-Datei für Demo)
    icon_content = """
    # GermanCodeZero-Cleaner Icon
    # In einer echten Implementierung wäre hier eine .ico-Datei
    
    🛡️ - Haupt-Icon
    🔍 - Scan-Icon  
    🧹 - Clean-Icon
    ⚙️ - Settings-Icon
    🤖 - AI-Icon
    """
    
    with open(assets_dir / "icon_info.txt", "w", encoding="utf-8") as f:
        f.write(icon_content)
    
    # Erstelle Konfigurationsdateien
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Standard-Konfiguration
    default_config = {
        "ui": {
            "theme": "dark",
            "enable_3d": True,
            "enable_animations": True,
            "language": "de"
        },
        "scanning": {
            "auto_scan_on_startup": False,
            "enable_gpu_acceleration": True,
            "max_threads": "auto"
        },
        "privacy": {
            "data_sharing_enabled": False,
            "analytics_enabled": False,
            "crash_reports": True
        },
        "premium": {
            "license_key": "",
            "expires": None
        }
    }
    
    with open(config_dir / "default_config.json", "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)
    
    print("✅ Assets und Konfiguration erstellt")

def create_batch_launcher():
    """Erstellt Batch-Datei für einfachen Start."""
    print("\n📄 Erstelle Launcher-Skript...")
    
    if platform.system() == "Windows":
        batch_content = f"""@echo off
title GermanCodeZero-Cleaner
echo Starte GermanCodeZero-Cleaner...
echo.

cd /d "{Path.cwd()}"
"{sys.executable}" main.py

if errorlevel 1 (
    echo.
    echo Fehler beim Starten der Anwendung!
    echo Prüfen Sie die Installation und Abhängigkeiten.
    pause
)
"""
        
        with open("start_cleaner.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        
        print("✅ start_cleaner.bat erstellt")
    
    else:
        # Shell-Skript für Unix-Systeme
        shell_content = f"""#!/bin/bash
echo "Starte GermanCodeZero-Cleaner..."

cd "{Path.cwd()}"
"{sys.executable}" main.py

if [ $? -ne 0 ]; then
    echo "Fehler beim Starten der Anwendung!"
    echo "Prüfen Sie die Installation und Abhängigkeiten."
    read -p "Drücken Sie Enter zum Beenden..."
fi
"""
        
        with open("start_cleaner.sh", "w", encoding="utf-8") as f:
            f.write(shell_content)
        
        # Ausführbar machen
        os.chmod("start_cleaner.sh", 0o755)
        
        print("✅ start_cleaner.sh erstellt")

def create_uninstaller():
    """Erstellt Deinstallations-Skript."""
    print("\n🗑️ Erstelle Deinstallationsskript...")
    
    uninstall_content = f"""#!/usr/bin/env python3
'''
GermanCodeZero-Cleaner Deinstallation
====================================
'''

import os
import shutil
import sys
from pathlib import Path

def uninstall():
    print("🗑️ Deinstalliere GermanCodeZero-Cleaner...")
    
    # Entferne Anwendungsdaten
    if sys.platform == "win32":
        app_data = Path.home() / "AppData" / "Roaming" / "GermanCodeZero-Cleaner"
    elif sys.platform == "darwin":
        app_data = Path.home() / "Library" / "Application Support" / "GermanCodeZero-Cleaner"
    else:
        app_data = Path.home() / ".local" / "share" / "GermanCodeZero-Cleaner"
    
    if app_data.exists():
        shutil.rmtree(app_data)
        print(f"✅ Anwendungsdaten entfernt: {{app_data}}")
    
    # Entferne Desktop-Verknüpfung
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "GermanCodeZero-Cleaner.lnk"
    if shortcut_path.exists():
        shortcut_path.unlink()
        print("✅ Desktop-Verknüpfung entfernt")
    
    print("✅ Deinstallation abgeschlossen")
    print("Vielen Dank, dass Sie GermanCodeZero-Cleaner verwendet haben!")

if __name__ == "__main__":
    uninstall()
"""
    
    with open("uninstall.py", "w", encoding="utf-8") as f:
        f.write(uninstall_content)
    
    print("✅ uninstall.py erstellt")

def main():
    """Haupt-Installationsroutine."""
    print_banner()
    
    # System-Anforderungen prüfen
    if not check_system_requirements():
        print("\n❌ System-Anforderungen nicht erfüllt!")
        sys.exit(1)
    
    print("\n🚀 Beginne Installation...")
    
    # Python-Abhängigkeiten installieren
    if not install_python_dependencies():
        print("\n❌ Installation der Abhängigkeiten fehlgeschlagen!")
        sys.exit(1)
    
    # Ollama für KI einrichten
    setup_ollama()
    
    # Assets und Konfiguration erstellen
    create_assets_directory()
    
    # Launcher-Skripte erstellen
    create_batch_launcher()
    
    # Desktop-Verknüpfung erstellen
    create_desktop_shortcut()
    
    # Deinstallationsskript erstellen
    create_uninstaller()
    
    print("\n" + "="*60)
    print("🎉 Installation erfolgreich abgeschlossen!")
    print("="*60)
    print()
    print("📋 Nächste Schritte:")
    print("   1. Starten Sie die Anwendung mit: python main.py")
    print("   2. Oder verwenden Sie: start_cleaner.bat (Windows)")
    print("   3. Für KI-Features: Stellen Sie sicher, dass Ollama läuft")
    print()
    print("📖 Dokumentation:")
    print("   - README.md für detaillierte Informationen")
    print("   - config.py für erweiterte Einstellungen")
    print()
    print("🆘 Support:")
    print("   - GitHub: https://github.com/germancodezero/cleaner")
    print("   - Email: support@germancodezero.com")
    print()
    print("Viel Spaß mit GermanCodeZero-Cleaner! 🚀")

if __name__ == "__main__":
    main()