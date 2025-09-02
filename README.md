# Cleaner Pro – Systemreiniger der nächsten Generation

**Cleaner Pro** ist eine moderne, KI-gestützte System-Reinigungs-Anwendung mit einem leistungsstarken Python-Kern und einer intuitiven 3D-Benutzeroberfläche, die auf Electron und React basiert.

## Features

### 🧹 Intelligente System-Reinigung
- **Hardware-beschleunigter Scan**: Nutzt CPU, GPU, RAM optimal.
- **Umfassende Analyse**: Findet temporäre Dateien, Cache, Duplikate und mehr.
- **KI-gestützte Kategorisierung**: Ein lokales LLM erklärt gefundene Dateien und gibt Empfehlungen.
- **Sichere Löschung**: Eingebaute Schutzmechanismen verhindern das versehentliche Löschen wichtiger Systemdateien.

### 🎨 Moderne 3D-Benutzeroberfläche
- **Hologramm-Effekte**: Futuristische Visualisierungen des Scan-Prozesses.
- **Echtzeit-Statistiken**: Live-Anzeige der Systemgesundheit und des Reinigungsfortschritts.
- **Responsive Design**: Optimiert für verschiedene Bildschirmgrößen.

### 🤖 KI-Integration
- **Lokale LLM**: Die KI läuft offline auf Ihrem Gerät, um maximalen Datenschutz zu gewährleisten.
- **Interaktive Erklärungen**: Verständliche Beschreibungen der Scan-Ergebnisse.
- **Intelligente Empfehlungen**: Die KI schlägt optimale Reinigungsstrategien vor.

## Technologie-Stack

*   **Frontend:** React, TypeScript, Vite, Tailwind CSS
*   **Desktop App:** Electron
*   **Backend & Core-Logik:** Python
*   **KI-Integration:** Lokale LLMs (über Ollama und Transformers)
*   **3D-Rendering:** WebGL

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

## Roadmap

*   Automatische Reinigungs-Zeitpläne
*   Cloud-Synchronisierung von Reinigungsprofilen (optional)
*   Erweiterte System-Tweaking-Optionen
*   Freemium-Modell mit optionalem Premium-Abo für werbefreie Nutzung

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
