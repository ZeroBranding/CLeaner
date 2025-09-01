"""
⚙️ Configuration Management
Secure API key storage and application settings
"""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Config:
    """Application configuration manager"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".holographic_ai"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.settings = {
            # UI Settings
            'window_width': 1400,
            'window_height': 900,
            'theme': 'dark_neon',
            'animation_speed': 1.0,
            'hologram_intensity': 1.0,
            'particle_count': 1000,
            
            # Performance Settings
            'target_fps': 60,
            'vsync_enabled': True,
            'hardware_acceleration': True,
            'auto_quality_adjustment': True,
            
            # AI Settings
            'default_provider': 'auto',
            'response_timeout': 30.0,
            'max_tokens': 1024,
            'temperature': 0.7,
            
            # Monitoring Settings
            'update_interval': 1000,  # ms
            'history_retention_days': 30,
            'enable_gpu_monitoring': True,
            'enable_temperature_monitoring': True,
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.settings[key] = value
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            import json
            config_file = self.config_dir / "config.json"
            with open(config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            import json
            config_file = self.config_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

# Global config instance
config = Config()

# API Key Setup Instructions
API_SETUP_INSTRUCTIONS = """
🔑 API Key Setup Instructions:

To enable cloud AI providers, you'll need to set up API keys:

1. **Google Gemini 1.5**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create a free API key
   - Run: python -c "from src.core.database import DatabaseManager; db = DatabaseManager(); db.store_api_key('gemini', 'YOUR_API_KEY')"

2. **Groq (Free & Fast)**:
   - Visit: https://console.groq.com/keys
   - Create a free account and API key
   - Run: python -c "from src.core.database import DatabaseManager; db = DatabaseManager(); db.store_api_key('groq', 'YOUR_API_KEY')"

3. **Deepseek 3.1**:
   - Visit: https://platform.deepseek.com/api_keys
   - Create an API key
   - Run: python -c "from src.core.database import DatabaseManager; db = DatabaseManager(); db.store_api_key('deepseek', 'YOUR_API_KEY')"

4. **Local Ollama (Recommended for privacy)**:
   - Install: curl -fsSL https://ollama.ai/install.sh | sh
   - Run: ollama pull llama3:8b
   - No API key needed!

The application will work with Ollama local AI even without cloud API keys.
"""