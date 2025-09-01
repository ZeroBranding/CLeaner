# Cleaner Pro – Systemreiniger der nächsten Generation

**Cleaner Pro** ist ein intelligenter, plattformübergreifender Systemreiniger, der mit einer modernen React/Electron-Oberfläche und einem leistungsstarken Python-Kern ausgestattet ist. Die Anwendung findet und entfernt nicht nur überflüssige Dateien, sondern identifiziert auch Treiberprobleme und gibt mithilfe von integrierten Sprachmodellen intelligente Empfehlungen zur Systemoptimierung.

## Technologie-Stack

*   **Frontend:** React, TypeScript, Vite, Tailwind CSS
*   **Desktop App:** Electron
*   **Backend & Core-Logik:** Python
*   **KI-Integration:** Lokale LLMs (über Ollama und Transformers)

## Haupt-Features

1.  **Hardware-spezifische Datenmüll-Bereinigung:**
    *   CPU- und GPU-Cache-Dateien
    *   RAM-Auslagerungs-/Hibernation-Dateien
    *   Temporäre SSD- und Festplatten-Artefakte (Log- und Cache-Verzeichnisse)
    *   Mainboard-bezogene Firmware-Logs
2.  **Treiber-Identifizierung & Update-Empfehlungen**
3.  **System-Übersicht in Echtzeit:** Temperatur, Auslastung und Lebensdauer-Statistiken
4.  **Integrierte lokale LLMs** für kontextbezogene Analysen und Benutzerinteraktion
5.  **Erweiterbare Plugin-Architektur:** Eigene Module können einfach im Verzeichnis `cleaner/hardware` hinzugefügt werden.

## Installation & Einrichtung

Für die Entwicklungsumgebung werden sowohl Python als auch Node.js benötigt.

### 1. Backend (Python)

```bash
# 1. Python-Umgebung anlegen (empfohlen)
python -m venv venv
# Windows: venv\\Scripts\\activate
# Linux/macOS: source venv/bin/activate

# 2. Abhängigkeiten installieren
pip install -r requirements.txt
```

### 2. Frontend (Node.js & Electron)

```bash
# 1. Node.js Abhängigkeiten installieren
npm install

# 2. Anwendung im Entwicklungsmodus starten
npm run dev
```

### 3. KI-Modelle (Optional)

1.  [Ollama](https://ollama.ai) installieren und das gewünschte Modell herunterladen:
    ```bash
    ollama pull llama3 # Beispiel
    ```
2.  Für andere Modelle (z.B. über HuggingFace), den Pfad in der entsprechenden Konfigurationsdatei oder Umgebungsvariable setzen.

## Verfügbare Skripte

Die folgenden Skripte sind in der `package.json` definiert und können mit `npm run <script-name>` ausgeführt werden:

| Skript             | Beschreibung                                                                  |
| ------------------ | ----------------------------------------------------------------------------- |
| `dev`              | Startet die Electron-Anwendung im Entwicklungsmodus mit Hot-Reloading.          |
| `build`            | Baut das Frontend und den Main-Prozess für die Produktion.                    |
| `lint`             | Überprüft den TypeScript/JavaScript-Code auf Stil- und Syntaxfehler.          |
| `test`             | Führt die Tests mit Vitest aus.                                               |
| `format`           | Formatiert den gesamten Code mit Prettier.                                    |
| `electron:dev`     | Startet nur den Electron-Wrapper im Entwicklungsmodus.                        |

## Verwendung der CLI (Python-Kern)

Die Kernfunktionalität kann auch direkt über die Kommandozeile genutzt werden.

```bash
# Beispiel: Komplette Reinigung mit Standard-Profil
python main.py clean

# Beispiel: Nur Treiberanalyse durchführen
python main.py drivers scan
```

## Roadmap

*   Automatische Reinigungs-Zeitpläne
*   Cloud-Synchronisierung von Reinigungsprofilen (optional)
*   Erweiterte System-Tweaking-Optionen

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.