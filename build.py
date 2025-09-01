"""
Build-Skript für GermanCodeZero-Cleaner
=======================================

Erstellt eine ausführbare Datei für Windows/macOS/Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json

def print_build_banner():
    """Zeigt das Build-Banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏗️  GermanCodeZero-Cleaner Build System              ║
    ║                                                              ║
    ║          Erstelle ausführbare Desktop-Anwendung             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_build_requirements():
    """Prüft Build-Anforderungen."""
    print("🔍 Prüfe Build-Anforderungen...")
    
    required_packages = ["pyinstaller", "auto-py-to-exe"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} nicht gefunden")
    
    if missing_packages:
        print(f"\n📦 Installiere fehlende Pakete: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ Alle Build-Abhängigkeiten installiert")
        except subprocess.CalledProcessError:
            print("❌ Fehler bei der Installation der Build-Abhängigkeiten")
            return False
    
    return True

def create_pyinstaller_spec():
    """Erstellt eine PyInstaller-Spezifikationsdatei."""
    print("\n📝 Erstelle PyInstaller-Konfiguration...")
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Pfade
project_root = r"{Path.cwd()}"
main_script = os.path.join(project_root, "main.py")

block_cipher = None

a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, "assets"), "assets"),
        (os.path.join(project_root, "config"), "config"),
        (os.path.join(project_root, "*.py"), "."),
    ],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'pygame',
        'moderngl',
        'numpy',
        'psutil',
        'send2trash',
        'pandas',
        'requests',
        'aiohttp',
        'asyncio',
        'threading',
        'multiprocessing',
        'hashlib',
        'winreg',
        'pathlib',
        'datetime',
        'json',
        'tempfile',
        'shutil',
        'mimetypes',
        'platform',
        'urllib',
        'zipfile'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'jupyter',
        'notebook',
        'IPython'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GermanCodeZero-Cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI-Anwendung
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, "assets", "icon.ico") if os.path.exists(os.path.join(project_root, "assets", "icon.ico")) else None,
    version_file=None,
)

# Windows-spezifische Optionen
if sys.platform == "win32":
    exe.version = "1.0.0"
    exe.description = "GermanCodeZero-Cleaner - KI-gestützte System-Optimierung"
    exe.company = "GermanCodeZero"
    exe.copyright = "© 2024 GermanCodeZero"
"""
    
    with open("germancodezero_cleaner.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ PyInstaller-Spezifikation erstellt")

def build_executable():
    """Erstellt die ausführbare Datei."""
    print("\n🏗️ Erstelle ausführbare Datei...")
    
    try:
        # Verwende PyInstaller mit Spec-Datei
        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            "germancodezero_cleaner.spec"
        ]
        
        print(f"Führe aus: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build erfolgreich!")
            
            # Zeige Build-Ergebnisse
            dist_dir = Path("dist")
            if dist_dir.exists():
                exe_files = list(dist_dir.glob("*.exe")) + list(dist_dir.glob("GermanCodeZero-Cleaner"))
                
                for exe_file in exe_files:
                    size_mb = exe_file.stat().st_size / (1024 * 1024)
                    print(f"📦 Erstellt: {exe_file} ({size_mb:.1f} MB)")
        else:
            print("❌ Build fehlgeschlagen!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ PyInstaller nicht gefunden!")
        print("   Installieren Sie mit: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ Build-Fehler: {e}")
        return False
    
    return True

def create_installer():
    """Erstellt einen Windows-Installer."""
    if platform.system() != "Windows":
        print("⚠️  Installer-Erstellung nur unter Windows verfügbar")
        return
    
    print("\n📦 Erstelle Windows-Installer...")
    
    # NSIS-Skript (vereinfacht)
    nsis_content = f'''
!define APP_NAME "GermanCodeZero-Cleaner"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "GermanCodeZero"
!define APP_URL "https://germancodezero.com"
!define APP_EXECUTABLE "GermanCodeZero-Cleaner.exe"

Name "${{APP_NAME}}"
OutFile "${{APP_NAME}}_Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
RequestExecutionLevel admin

Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\\*"
    
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortcut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\*.*"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
SectionEnd
'''
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_content)
    
    print("✅ NSIS-Installer-Skript erstellt")
    print("   Verwenden Sie NSIS zum Kompilieren: makensis installer.nsi")

def optimize_build():
    """Optimiert die erstellte Anwendung."""
    print("\n⚡ Optimiere Build...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Dist-Verzeichnis nicht gefunden")
        return
    
    # UPX-Komprimierung (falls verfügbar)
    try:
        exe_files = list(dist_dir.glob("*.exe"))
        for exe_file in exe_files:
            original_size = exe_file.stat().st_size
            
            subprocess.run(["upx", "--best", str(exe_file)], 
                         capture_output=True, check=False)
            
            if exe_file.exists():
                compressed_size = exe_file.stat().st_size
                compression_ratio = (1 - compressed_size / original_size) * 100
                print(f"✅ {exe_file.name} komprimiert: {compression_ratio:.1f}% kleiner")
    
    except FileNotFoundError:
        print("⚠️  UPX nicht gefunden - Komprimierung übersprungen")
        print("   Installieren Sie UPX für kleinere Dateien: https://upx.github.io/")

def create_portable_version():
    """Erstellt eine portable Version."""
    print("\n💼 Erstelle portable Version...")
    
    portable_dir = Path("portable")
    portable_dir.mkdir(exist_ok=True)
    
    # Kopiere notwendige Dateien
    files_to_copy = [
        "main.py",
        "config.py", 
        "ui_components.py",
        "cleaner_engine.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, portable_dir / file_name)
    
    # Kopiere Assets
    if Path("assets").exists():
        shutil.copytree("assets", portable_dir / "assets", dirs_exist_ok=True)
    
    # Erstelle portable Launcher
    portable_launcher = f"""@echo off
title GermanCodeZero-Cleaner (Portable)
echo GermanCodeZero-Cleaner - Portable Version
echo ==========================================
echo.

REM Prüfe Python-Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Fehler: Python ist nicht installiert oder nicht im PATH!
    echo Bitte installieren Sie Python 3.8+ von python.org
    pause
    exit /b 1
)

REM Installiere Abhängigkeiten lokal
echo Installiere Abhängigkeiten...
python -m pip install --user -r requirements.txt

REM Starte Anwendung
echo Starte GermanCodeZero-Cleaner...
python main.py

if errorlevel 1 (
    echo.
    echo Fehler beim Starten!
    pause
)
"""
    
    with open(portable_dir / "start_portable.bat", "w", encoding="utf-8") as f:
        f.write(portable_launcher)
    
    print("✅ Portable Version erstellt")
    print(f"   Verzeichnis: {portable_dir.absolute()}")

def cleanup_build_files():
    """Räumt Build-Dateien auf."""
    print("\n🧹 Räume Build-Dateien auf...")
    
    cleanup_dirs = ["build", "__pycache__"]
    cleanup_files = ["*.pyc", "*.pyo", "*.spec"]
    
    for dir_name in cleanup_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✅ {dir_name}/ entfernt")
    
    # Entferne .pyc-Dateien rekursiv
    for pyc_file in Path(".").rglob("*.pyc"):
        pyc_file.unlink()
    
    for pyo_file in Path(".").rglob("*.pyo"):
        pyo_file.unlink()
    
    print("✅ Build-Dateien bereinigt")

def main():
    """Haupt-Build-Routine."""
    print_build_banner()
    
    # Build-Anforderungen prüfen
    if not check_build_requirements():
        sys.exit(1)
    
    # Menü für Build-Optionen
    print("\n🎯 Build-Optionen:")
    print("   1. Ausführbare Datei erstellen")
    print("   2. Portable Version erstellen")
    print("   3. Windows-Installer erstellen")
    print("   4. Alles erstellen")
    print("   5. Build-Dateien bereinigen")
    
    try:
        choice = input("\nWählen Sie eine Option (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Build abgebrochen")
        sys.exit(0)
    
    if choice == "1":
        create_pyinstaller_spec()
        build_executable()
        optimize_build()
        
    elif choice == "2":
        create_portable_version()
        
    elif choice == "3":
        create_pyinstaller_spec()
        if build_executable():
            create_installer()
        
    elif choice == "4":
        print("\n🚀 Vollständiger Build...")
        create_pyinstaller_spec()
        if build_executable():
            optimize_build()
            create_installer()
        create_portable_version()
        
    elif choice == "5":
        cleanup_build_files()
        
    else:
        print("❌ Ungültige Auswahl")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 Build-Prozess abgeschlossen!")
    print("="*60)
    print()
    print("📁 Erstellte Dateien:")
    
    # Zeige erstellte Dateien
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   📦 {file.name} ({size_mb:.1f} MB)")
    
    portable_dir = Path("portable")
    if portable_dir.exists():
        print(f"   💼 Portable Version: {portable_dir.absolute()}")
    
    print()
    print("🚀 Ihre Anwendung ist bereit für die Verteilung!")

if __name__ == "__main__":
    main()