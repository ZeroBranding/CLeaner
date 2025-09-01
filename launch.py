#!/usr/bin/env python3
"""
🚀 Holographic AI System Monitor Launcher
Quick setup and launch script with dependency checking
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'PyQt6', 'psutil', 'numpy', 'cryptography', 'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.lower().replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (missing)")
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

def check_ollama():
    """Check Ollama installation"""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama installed")
            
            # Check for Llama3 model
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "llama3" in result.stdout:
                print("✅ Llama3 model available")
            else:
                print("⚠️  Llama3 model not found")
                print("   Run: ollama pull llama3:8b")
        else:
            print("❌ Ollama not installed")
            print("   Install: curl -fsSL https://ollama.ai/install.sh | sh")
            
    except FileNotFoundError:
        print("❌ Ollama not found")
        print("   Install: curl -fsSL https://ollama.ai/install.sh | sh")

def launch_application():
    """Launch the main application"""
    print("\n🚀 Launching Holographic AI System Monitor...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        # Import and run main application
        from main import main
        return main()
        
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main launcher function"""
    print("🌌 Holographic AI System Monitor Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        if not install_missing_packages(missing):
            sys.exit(1)
    
    # Check Ollama
    print("\n🤖 Checking AI support...")
    check_ollama()
    
    # Launch application
    return launch_application()

if __name__ == "__main__":
    sys.exit(main())