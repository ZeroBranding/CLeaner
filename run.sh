#!/bin/bash

# 🚀 Holographic AI System Monitor Runner
# Quick launch script with environment setup

echo "🌌 Holographic AI System Monitor"
echo "================================"

# Check Python version
python3 --version

# Check if virtual environment should be created
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/installed
fi

# Test the application
echo "🧪 Running tests..."
python test_app.py

# Launch the application
echo "🚀 Launching application..."
python main.py