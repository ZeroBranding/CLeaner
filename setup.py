"""
🚀 Holographic AI System Monitor Setup
Installation and configuration script
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True

def setup_ollama():
    """Setup Ollama for local AI"""
    print("🤖 Setting up Ollama for local AI...")
    
    try:
        # Check if Ollama is installed
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("📥 Ollama not found. Please install it manually:")
            print("   curl -fsSL https://ollama.ai/install.sh | sh")
            return False
        
        print("✅ Ollama found!")
        
        # Check if Llama3 model is available
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        
        if "llama3:8b" not in result.stdout:
            print("📥 Downloading Llama3-8B model (this may take a while)...")
            subprocess.check_call(["ollama", "pull", "llama3:8b"])
            print("✅ Llama3-8B model downloaded!")
        else:
            print("✅ Llama3-8B model already available!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ollama setup failed: {e}")
        return False
    except FileNotFoundError:
        print("📥 Ollama not found. Please install it manually:")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        return False

def check_gpu_support():
    """Check for AMD GPU support"""
    print("🎮 Checking GPU support...")
    
    try:
        # Check for AMD GPU
        result = subprocess.run(["lspci"], capture_output=True, text=True)
        
        if "AMD" in result.stdout and "Radeon" in result.stdout:
            print("✅ AMD GPU detected!")
            
            # Check for ROCm
            try:
                subprocess.run(["rocm-smi", "--version"], capture_output=True, check=True)
                print("✅ ROCm detected - advanced GPU monitoring available!")
            except:
                print("⚠️  ROCm not found - basic GPU monitoring only")
                print("   For advanced GPU monitoring, install ROCm:")
                print("   https://rocm.docs.amd.com/en/latest/deploy/linux/quick_start.html")
        else:
            print("⚠️  AMD GPU not detected - GPU monitoring may be limited")
        
    except Exception as e:
        print(f"⚠️  GPU check failed: {e}")

def create_desktop_entry():
    """Create desktop entry for easy launching"""
    try:
        desktop_dir = Path.home() / ".local/share/applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_entry = f"""[Desktop Entry]
Name=Holographic AI Monitor
Comment=Advanced system monitor with AI integration
Exec={sys.executable} {Path.cwd() / 'main.py'}
Icon={Path.cwd() / 'assets/icon.png'}
Terminal=false
Type=Application
Categories=System;Monitor;
"""
        
        desktop_file = desktop_dir / "holographic-ai-monitor.desktop"
        with open(desktop_file, 'w') as f:
            f.write(desktop_entry)
        
        os.chmod(desktop_file, 0o755)
        print("✅ Desktop entry created!")
        
    except Exception as e:
        print(f"⚠️  Failed to create desktop entry: {e}")

def main():
    """Main setup function"""
    print("🚀 Holographic AI System Monitor Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup Ollama
    setup_ollama()
    
    # Check GPU support
    check_gpu_support()
    
    # Create desktop entry
    create_desktop_entry()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Run: python main.py")
    print("2. Set up API keys for cloud providers (see config.py)")
    print("3. Enjoy the holographic experience!")
    
    print("\n" + "=" * 50)
    print("🔑 API Key Setup:")
    print("Run this after getting your API keys:")
    print("python -c \"from src.core.database import DatabaseManager; db = DatabaseManager(); db.store_api_key('groq', 'YOUR_GROQ_KEY')\"")

if __name__ == "__main__":
    main()