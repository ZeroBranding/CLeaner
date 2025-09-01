#!/bin/bash

# GermanCodeZero-Cleaner Starter Script
# =====================================

echo "🛡️  GermanCodeZero-Cleaner"
echo "=================================="
echo "KI-gestützte System-Optimierung"
echo ""

# Prüfe Python-Installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 ist nicht installiert!"
    echo "   Installieren Sie Python 3.8+ von python.org"
    exit 1
fi

# Prüfe Python-Version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python $PYTHON_VERSION erkannt"

# Wechsle ins Projektverzeichnis
cd "$(dirname "$0")"

# Installiere Abhängigkeiten falls nötig
if [ ! -f ".dependencies_installed" ]; then
    echo "📦 Installiere Abhängigkeiten..."
    python3 -m pip install --user -r requirements.txt
    
    if [ $? -eq 0 ]; then
        touch .dependencies_installed
        echo "✅ Abhängigkeiten installiert"
    else
        echo "❌ Fehler bei der Installation der Abhängigkeiten"
        exit 1
    fi
fi

# Starte Anwendung
echo "🚀 Starte GermanCodeZero-Cleaner..."
python3 main.py

# Prüfe Exit-Code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Fehler beim Starten der Anwendung!"
    echo "   Prüfen Sie die Installation und Abhängigkeiten."
    read -p "Drücken Sie Enter zum Beenden..."
fi