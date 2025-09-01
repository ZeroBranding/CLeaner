# Cleaner – Systemreiniger der nächsten Generation

Cleaner ist ein plattformübergreifendes Open-Source-Werkzeug, das ähnlich wie „CCleaner“ überflüssige Dateien findet und entfernt, Treiberprobleme erkennt und mithilfe lokaler Sprachmodelle intelligente Empfehlungen ausspricht.

## Haupt-Features

1. Hardware-spezifische Datenmüll-Bereinigung
   * CPU- und GPU-Cache-Dateien
   * RAM-Auslagerungs-/Hibernation-Dateien
   * Temporäre SSD- und Festplatten-Artefakte (Log- und Cache-Verzeichnisse)
   * Mainboard-bezogene Firmware-Logs
   * Netzteil-(PSU)-Diagnose-Berichte (sofern vorhanden)
2. Treiber-Identifizierung & Update-Empfehlungen
3. Schnelle Übersichtssysteme: Temperatur, Auslastung, Lebensdauer-Statistiken
4. Integrierte lokalen LLMs für Kontexterkennung & Benutzerinteraktion
   * Deutsches 8B-Modell über Ollama
   * GPT-OSS-20B für erweiterte Analysen
5. Erweiterbare Plugin-Architektur – implementiere eigene Module im Verzeichnis `cleaner/hardware` oder `cleaner/plugins`.

## Installation

```bash
# Python-Umgebung anlegen (empfohlen)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

LLM-Modelle:
1. [Ollama](https://ollama.ai) installieren und das deutsche 8B-Modell herunterladen:
   ```bash
   ollama pull deutsch-8b
   ```
2. GPT-OSS-20B installieren (ggf. über HuggingFace) und Pfad in der Umgebungsvariable `GPT_OSS_MODEL_PATH` setzen.

## Verwendung

```bash
python -m cleaner.clean
# oder
python main.py clean
```

Beispiele:
* Komplettreinigung mit Standard-Profil
  ```bash
  cleaner clean
  ```
* Nur Treiberanalyse
  ```bash
  cleaner drivers scan
  ```

## Roadmap
* Automatische Zeitpläne
* GUI auf Basis von Electron oder Qt
* Cloud-Sync der Reinigungsprofile (optional)

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.