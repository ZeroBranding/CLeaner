#!/usr/bin/env python3
"""
Cleaner Pro - Python Backend Entry Point
========================================

This file serves as the entry point for the Python backend functionality
when running the application in CLI mode or for backend services.

The main application interface is now handled by the Electron/React frontend.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleaner_pro.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for CLI mode"""
    print("🚀 Cleaner Pro - Python Backend")
    print("=" * 40)
    print("The main application is now available through the Electron/React interface.")
    print("Use 'npm run dev' to start the full application.")
    print()
    print("For CLI operations, use the cleaner module directly:")
    print("  python -m cleaner.cli")
    print()
    
    # Check if we're in CLI mode
    if len(sys.argv) > 1:
        logger.info(f"CLI arguments detected: {sys.argv[1:]}")
        print("CLI mode detected. Please use the cleaner module for CLI operations.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
