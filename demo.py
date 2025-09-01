#!/usr/bin/env python3
"""
GermanCodeZero-Cleaner Demo
===========================

Vereinfachte Demo-Version ohne externe Abhängigkeiten.
Zeigt das UI-Design und die grundlegende Funktionalität.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading
import time
import tempfile
import random
from datetime import datetime
from pathlib import Path

# ============================================================================
# DEMO CONFIGURATION
# ============================================================================

APP_NAME = "GermanCodeZero-Cleaner"
APP_VERSION = "1.0.0 (Demo)"

# Vereinfachtes Theme
THEME = {
    "bg_dark": "#0a0a0a",
    "bg_medium": "#1a1a1a", 
    "bg_light": "#2a2a2a",
    "accent_blue": "#00d4ff",
    "accent_green": "#10b981",
    "accent_red": "#ef4444",
    "text_white": "#ffffff",
    "text_gray": "#a1a1aa"
}

# ============================================================================
# DEMO APPLICATION
# ============================================================================

class GermanCodeZeroCleanerDemo:
    """Demo-Version der Anwendung."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_ui()
        
        # Demo-Daten
        self.demo_scan_results = self.generate_demo_data()
        self.is_scanning = False
        
    def setup_window(self):
        """Konfiguriert das Hauptfenster."""
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1000x700")
        self.root.configure(bg=THEME["bg_dark"])
        
        # Zentriere Fenster
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
        
        # Style konfigurieren
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom Styles
        style.configure('Header.TLabel', 
                       background=THEME["bg_medium"],
                       foreground=THEME["accent_blue"],
                       font=('Arial', 16, 'bold'))
        
        style.configure('Title.TLabel',
                       background=THEME["bg_dark"],
                       foreground=THEME["text_white"],
                       font=('Arial', 12, 'bold'))
        
        style.configure('Demo.TButton',
                       background=THEME["accent_blue"],
                       foreground=THEME["text_white"],
                       font=('Arial', 10, 'bold'))
    
    def create_ui(self):
        """Erstellt die Benutzeroberfläche."""
        # Header
        header_frame = tk.Frame(self.root, bg=THEME["bg_medium"], height=80)
        header_frame.pack(fill="x", pady=0)
        header_frame.pack_propagate(False)
        
        # Logo und Titel
        title_label = tk.Label(
            header_frame,
            text="🛡️ GermanCodeZero-Cleaner",
            bg=THEME["bg_medium"],
            fg=THEME["accent_blue"],
            font=("Arial", 20, "bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="KI-gestützte System-Optimierung mit 3D-Interface (DEMO)",
            bg=THEME["bg_medium"],
            fg=THEME["text_gray"],
            font=("Arial", 10)
        )
        subtitle_label.place(x=20, y=50)
        
        # Navigation
        nav_frame = tk.Frame(header_frame, bg=THEME["bg_medium"])
        nav_frame.pack(side="right", padx=20, pady=20)
        
        scan_btn = tk.Button(
            nav_frame,
            text="🔍 Demo Scan",
            bg=THEME["accent_green"],
            fg=THEME["text_white"],
            font=("Arial", 10, "bold"),
            command=self.start_demo_scan,
            relief="flat",
            padx=15,
            pady=5
        )
        scan_btn.pack(side="left", padx=5)
        
        ai_btn = tk.Button(
            nav_frame,
            text="🤖 KI-Demo",
            bg=THEME["accent_blue"],
            fg=THEME["text_white"],
            font=("Arial", 10, "bold"),
            command=self.show_ai_demo,
            relief="flat",
            padx=15,
            pady=5
        )
        ai_btn.pack(side="left", padx=5)
        
        # Main Content
        main_frame = tk.Frame(self.root, bg=THEME["bg_dark"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Linke Seite - 3D Visualisierung (Platzhalter)
        left_panel = tk.Frame(main_frame, bg=THEME["bg_medium"], width=500)
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # 3D-Platzhalter mit Animation
        self.canvas = tk.Canvas(
            left_panel,
            bg=THEME["bg_dark"],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.animate_3d_placeholder()
        
        # Rechte Seite - Kontrollen
        right_panel = tk.Frame(main_frame, bg=THEME["bg_medium"], width=400)
        right_panel.pack(side="right", fill="y", padx=5, pady=5)
        right_panel.pack_propagate(False)
        
        self.create_control_panel(right_panel)
        self.create_results_panel(right_panel)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg=THEME["bg_medium"], height=50)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="💻 Demo-Version | 🆓 Kostenlose Nutzung | 🚀 Vollversion mit Premium-Features",
            bg=THEME["bg_medium"],
            fg=THEME["text_gray"],
            font=("Arial", 9)
        )
        footer_label.pack(pady=15)
    
    def create_control_panel(self, parent):
        """Erstellt das Kontrollpanel."""
        control_frame = tk.Frame(parent, bg=THEME["bg_light"])
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Titel
        title_label = tk.Label(
            control_frame,
            text="🎛️ Scan-Kontrollen",
            bg=THEME["bg_light"],
            fg=THEME["accent_blue"],
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Kategorie-Checkboxes
        self.category_vars = {}
        categories = [
            ("temp_files", "🗂️ Temporäre Dateien"),
            ("cache", "💾 Cache-Dateien"),
            ("logs", "📋 Log-Dateien"),
            ("duplicates", "👥 Duplikate"),
            ("registry", "🔧 Registry (Windows)")
        ]
        
        for cat_id, cat_name in categories:
            var = tk.BooleanVar(value=True)
            self.category_vars[cat_id] = var
            
            cb = tk.Checkbutton(
                control_frame,
                text=cat_name,
                variable=var,
                bg=THEME["bg_light"],
                fg=THEME["text_white"],
                selectcolor=THEME["bg_dark"],
                font=("Arial", 10)
            )
            cb.pack(anchor="w", padx=20, pady=3)
        
        # Scan-Button
        self.scan_button = tk.Button(
            control_frame,
            text="🚀 DEMO SYSTEM SCANNEN",
            bg=THEME["accent_green"],
            fg=THEME["text_white"],
            font=("Arial", 12, "bold"),
            command=self.start_demo_scan,
            relief="flat",
            padx=20,
            pady=10
        )
        self.scan_button.pack(fill="x", padx=20, pady=20)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        
        # Status
        self.status_label = tk.Label(
            control_frame,
            text="Bereit für Demo-Scan",
            bg=THEME["bg_light"],
            fg=THEME["text_gray"],
            font=("Arial", 9)
        )
        self.status_label.pack(pady=5)
    
    def create_results_panel(self, parent):
        """Erstellt das Ergebnispanel."""
        results_frame = tk.Frame(parent, bg=THEME["bg_light"])
        results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Titel
        title_label = tk.Label(
            results_frame,
            text="📊 Demo Scan-Ergebnisse",
            bg=THEME["bg_light"],
            fg=THEME["accent_blue"],
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Scrollbare Liste
        canvas = tk.Canvas(results_frame, bg=THEME["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=THEME["bg_dark"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Aktions-Buttons
        action_frame = tk.Frame(results_frame, bg=THEME["bg_light"])
        action_frame.pack(fill="x", padx=10, pady=10)
        
        clean_btn = tk.Button(
            action_frame,
            text="🧹 Demo Bereinigung",
            bg=THEME["accent_red"],
            fg=THEME["text_white"],
            font=("Arial", 10, "bold"),
            command=self.demo_cleaning,
            relief="flat",
            padx=10,
            pady=5
        )
        clean_btn.pack(side="left", padx=5)
        
        select_all_btn = tk.Button(
            action_frame,
            text="✅ Alle Demo-Items",
            bg=THEME["bg_light"],
            fg=THEME["text_white"],
            font=("Arial", 9),
            command=self.select_all_demo,
            relief="flat",
            padx=10,
            pady=5
        )
        select_all_btn.pack(side="right", padx=5)
    
    def animate_3d_placeholder(self):
        """Animiert den 3D-Platzhalter."""
        def draw_frame():
            self.canvas.delete("animation")
            
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                self.root.after(50, draw_frame)
                return
            
            center_x = width // 2
            center_y = height // 2
            
            # Animierte Hologramm-Linien
            current_time = time.time()
            
            # Rotierender Rahmen
            for i in range(8):
                angle = (current_time + i * 0.5) % (2 * 3.14159)
                
                x1 = center_x + 100 * math.cos(angle)
                y1 = center_y + 100 * math.sin(angle)
                x2 = center_x + 120 * math.cos(angle)
                y2 = center_y + 120 * math.sin(angle)
                
                intensity = int(100 + 155 * (math.sin(current_time * 3 + i) + 1) / 2)
                color = f"#{0:02x}{intensity:02x}{intensity:02x}"
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color,
                    width=2,
                    tags="animation"
                )
            
            # Zentraler Text
            glow = int(150 + 105 * math.sin(current_time * 2))
            text_color = f"#{0:02x}{glow:02x}{glow:02x}"
            
            self.canvas.create_text(
                center_x, center_y,
                text="🌟 3D-HOLOGRAMM\\nVISUALISIERUNG\\n\\n💫 Demo-Modus\\n🔮 Simulierte Daten\\n✨ Animierte Effekte",
                fill=text_color,
                font=("Arial", 12, "bold"),
                justify="center",
                tags="animation"
            )
            
            # Grid-Effekt
            grid_size = 30
            for i in range(0, width, grid_size):
                alpha = int(30 + 20 * math.sin(current_time + i * 0.1))
                color = f"#{0:02x}{alpha:02x}{alpha:02x}"
                
                self.canvas.create_line(
                    i, 0, i, height,
                    fill=color,
                    width=1,
                    tags="animation"
                )
            
            for i in range(0, height, grid_size):
                alpha = int(30 + 20 * math.sin(current_time + i * 0.1))
                color = f"#{0:02x}{alpha:02x}{alpha:02x}"
                
                self.canvas.create_line(
                    0, i, width, i,
                    fill=color,
                    width=1,
                    tags="animation"
                )
            
            self.root.after(50, draw_frame)
        
        # Importiere math hier für die Animation
        import math
        self.root.after(100, draw_frame)
    
    def generate_demo_data(self):
        """Generiert Demo-Scan-Daten."""
        demo_data = {
            "temp_files": {
                "count": random.randint(150, 500),
                "size_mb": random.randint(50, 200),
                "examples": [
                    "C:\\\\Temp\\\\chrome_temp_12345.tmp",
                    "C:\\\\Users\\\\User\\\\AppData\\\\Local\\\\Temp\\\\install.log",
                    "C:\\\\Windows\\\\Temp\\\\update_cache.tmp"
                ]
            },
            "cache": {
                "count": random.randint(80, 300),
                "size_mb": random.randint(100, 500),
                "examples": [
                    "Browser-Cache (Chrome, Firefox, Edge)",
                    "Windows Store Cache",
                    "Anwendungs-Cache-Dateien"
                ]
            },
            "logs": {
                "count": random.randint(30, 150),
                "size_mb": random.randint(10, 100),
                "examples": [
                    "Windows Event Logs",
                    "Anwendungs-Protokolle",
                    "System-Debug-Logs"
                ]
            },
            "duplicates": {
                "count": random.randint(20, 80),
                "size_mb": random.randint(50, 300),
                "examples": [
                    "Doppelte Bilder in Downloads",
                    "Identische Dokumente",
                    "Backup-Kopien"
                ]
            },
            "registry": {
                "count": random.randint(10, 50),
                "size_mb": random.randint(1, 10),
                "examples": [
                    "Verwaiste Startup-Einträge",
                    "Ungültige Anwendungsreferenzen",
                    "Alte Deinstallations-Einträge"
                ]
            }
        }
        
        return demo_data
    
    def start_demo_scan(self):
        """Startet den Demo-Scan."""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.scan_button.configure(text="🔄 Demo-Scanning...", state="disabled")
        
        # Starte Scan-Animation
        threading.Thread(target=self.demo_scan_process, daemon=True).start()
    
    def demo_scan_process(self):
        """Demo-Scan-Prozess."""
        categories = [cat for cat, var in self.category_vars.items() if var.get()]
        
        for i, category in enumerate(categories):
            if not self.is_scanning:
                break
            
            # Update Progress
            progress = (i + 1) / len(categories) * 100
            status = f"Scanne {category}..."
            
            self.root.after(0, lambda p=progress, s=status: self.update_scan_progress(p, s))
            
            # Simuliere Scan-Zeit
            time.sleep(random.uniform(0.5, 2.0))
        
        # Scan abgeschlossen
        self.root.after(0, self.on_demo_scan_complete)
    
    def update_scan_progress(self, progress: float, status: str):
        """Aktualisiert den Scan-Fortschritt."""
        self.progress_var.set(progress)
        self.status_label.configure(text=status)
    
    def on_demo_scan_complete(self):
        """Wird aufgerufen, wenn der Demo-Scan abgeschlossen ist."""
        self.is_scanning = False
        self.scan_button.configure(text="🚀 DEMO SYSTEM SCANNEN", state="normal")
        self.status_label.configure(text="Demo-Scan abgeschlossen!")
        
        # Zeige Ergebnisse
        self.display_demo_results()
        
        # Zeige KI-Empfehlung
        self.root.after(1000, self.show_demo_ai_recommendation)
    
    def display_demo_results(self):
        """Zeigt die Demo-Ergebnisse an."""
        # Lösche vorherige Ergebnisse
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Übersicht
        total_files = sum(data["count"] for data in self.demo_scan_results.values())
        total_mb = sum(data["size_mb"] for data in self.demo_scan_results.values())
        
        overview_text = f"📈 {total_files:,} Demo-Dateien gefunden\\n💾 {total_mb:.1f} MB Speicher freigegeben\\n⏱️ Demo-Scan-Dauer: 2.3s"
        
        overview_label = tk.Label(
            self.scrollable_frame,
            text=overview_text,
            bg=THEME["bg_dark"],
            fg=THEME["accent_green"],
            font=("Arial", 11, "bold"),
            justify="left"
        )
        overview_label.pack(pady=10, anchor="w")
        
        # Kategorien anzeigen
        category_names = {
            "temp_files": "🗂️ Temporäre Dateien",
            "cache": "💾 Cache-Dateien",
            "logs": "📋 Log-Dateien",
            "duplicates": "👥 Duplikate",
            "registry": "🔧 Registry-Einträge"
        }
        
        for category, data in self.demo_scan_results.items():
            if category not in self.category_vars or not self.category_vars[category].get():
                continue
            
            # Kategorie-Header
            header_frame = tk.Frame(self.scrollable_frame, bg=THEME["bg_light"])
            header_frame.pack(fill="x", pady=5, padx=5)
            
            header_text = f"{category_names.get(category, category)} ({data['count']} Dateien, {data['size_mb']} MB)"
            
            header_label = tk.Label(
                header_frame,
                text=header_text,
                bg=THEME["bg_light"],
                fg=THEME["text_white"],
                font=("Arial", 10, "bold")
            )
            header_label.pack(pady=5)
            
            # Beispiel-Dateien
            for example in data["examples"][:3]:
                item_frame = tk.Frame(self.scrollable_frame, bg=THEME["bg_dark"])
                item_frame.pack(fill="x", pady=1, padx=10)
                
                # Checkbox
                cb_var = tk.BooleanVar(value=True)
                cb = tk.Checkbutton(
                    item_frame,
                    variable=cb_var,
                    bg=THEME["bg_dark"],
                    selectcolor=THEME["bg_light"]
                )
                cb.pack(side="left", padx=5, pady=2)
                
                # Datei-Info
                info_label = tk.Label(
                    item_frame,
                    text=f"{example}\\n{random.randint(1, 50)} MB - Demo-Datei",
                    bg=THEME["bg_dark"],
                    fg=THEME["text_gray"],
                    font=("Arial", 8),
                    justify="left",
                    anchor="w"
                )
                info_label.pack(side="left", fill="x", expand=True, padx=5, pady=2)
    
    def demo_cleaning(self):
        """Demo-Bereinigungsprozess."""
        total_files = sum(data["count"] for data in self.demo_scan_results.values())
        total_mb = sum(data["size_mb"] for data in self.demo_scan_results.values())
        
        confirm_text = f"DEMO: Möchten Sie {total_files} Demo-Dateien ({total_mb} MB) bereinigen?\\n\\nDies ist nur eine Demonstration - keine echten Dateien werden gelöscht."
        
        if messagebox.askyesno("Demo-Bereinigung", confirm_text):
            self.execute_demo_cleaning()
    
    def execute_demo_cleaning(self):
        """Führt Demo-Bereinigung durch."""
        # Demo-Bereinigungsfenster
        cleaning_window = tk.Toplevel(self.root)
        cleaning_window.title("Demo-Bereinigung")
        cleaning_window.geometry("400x200")
        cleaning_window.configure(bg=THEME["bg_dark"])
        cleaning_window.transient(self.root)
        cleaning_window.grab_set()
        
        # Zentriere Fenster
        x = (self.root.winfo_x() + self.root.winfo_width() // 2) - 200
        y = (self.root.winfo_y() + self.root.winfo_height() // 2) - 100
        cleaning_window.geometry(f"400x200+{x}+{y}")
        
        progress_label = tk.Label(
            cleaning_window,
            text="🧹 Demo-Bereinigung läuft...",
            bg=THEME["bg_dark"],
            fg=THEME["accent_blue"],
            font=("Arial", 14, "bold")
        )
        progress_label.pack(pady=30)
        
        demo_progress = ttk.Progressbar(
            cleaning_window,
            length=300,
            mode='determinate'
        )
        demo_progress.pack(pady=20)
        
        # Simuliere Bereinigung
        def simulate():
            for i in range(101):
                demo_progress['value'] = i
                cleaning_window.update()
                time.sleep(0.03)
            
            cleaning_window.destroy()
            messagebox.showinfo(
                "Demo Erfolgreich", 
                "✅ Demo-Bereinigung abgeschlossen!\\n\\nIn der Vollversion würden echte Dateien bereinigt.\\n\\n🚀 Ihr System würde jetzt optimaler laufen!"
            )
        
        threading.Thread(target=simulate, daemon=True).start()
    
    def select_all_demo(self):
        """Demo für 'Alle auswählen'."""
        messagebox.showinfo("Demo", "✅ Alle Demo-Elemente wurden ausgewählt!")
    
    def show_ai_demo(self):
        """Zeigt KI-Demo-Chat."""
        ai_window = tk.Toplevel(self.root)
        ai_window.title("🤖 KI-Assistent Demo")
        ai_window.geometry("500x400")
        ai_window.configure(bg=THEME["bg_dark"])
        
        # Chat-Bereich
        chat_frame = tk.Frame(ai_window, bg=THEME["bg_medium"])
        chat_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        chat_text = tk.Text(
            chat_frame,
            bg=THEME["bg_dark"],
            fg=THEME["text_white"],
            font=("Arial", 10),
            wrap="word",
            state="disabled"
        )
        chat_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Eingabebereich
        input_frame = tk.Frame(ai_window, bg=THEME["bg_dark"])
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        entry = tk.Entry(
            input_frame,
            bg=THEME["bg_medium"],
            fg=THEME["text_white"],
            font=("Arial", 10),
            insertbackground=THEME["text_white"]
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        send_btn = tk.Button(
            input_frame,
            text="Demo Senden",
            bg=THEME["accent_blue"],
            fg=THEME["text_white"],
            font=("Arial", 9, "bold"),
            command=lambda: self.demo_ai_response(chat_text, entry),
            relief="flat"
        )
        send_btn.pack(side="right")
        
        # Enter-Taste
        entry.bind("<Return>", lambda e: self.demo_ai_response(chat_text, entry))
        
        # Begrüßung
        welcome = "🤖 KI-Assistent (Demo-Modus)\\n\\nHallo! Ich bin Ihr lokaler KI-Assistent. In der Vollversion kann ich:\\n\\n✨ Dateien intelligent analysieren\\n🔍 Personalisierte Empfehlungen geben\\n🛡️ Sicherheitsrisiken erklären\\n📊 Detaillierte Berichte erstellen\\n\\nStellen Sie mir eine Demo-Frage!"
        
        chat_text.configure(state="normal")
        chat_text.insert("end", welcome + "\\n\\n")
        chat_text.configure(state="disabled")
        chat_text.see("end")
    
    def demo_ai_response(self, chat_text, entry):
        """Demo KI-Antwort."""
        message = entry.get().strip()
        if not message:
            return
        
        # Zeige Benutzernachricht
        chat_text.configure(state="normal")
        chat_text.insert("end", f"Sie: {message}\\n\\n")
        entry.delete(0, "end")
        
        # Demo-Antworten
        demo_responses = [
            "🤖 Basierend auf Ihrer Demo-Anfrage empfehle ich, mit temporären Dateien zu beginnen. Diese sind am sichersten zu löschen und bieten sofortige Performance-Verbesserung.",
            
            "🧠 Ihr Demo-System zeigt typische Anzeichen von Cache-Ansammlung. Eine Bereinigung würde etwa 150-300 MB freigeben und die Startzeiten verbessern.",
            
            "📊 Die gefundenen Demo-Duplikate nehmen wertvollen Speicherplatz ein. In der Vollversion kann ich Ihnen beim intelligenten Löschen helfen, während wichtige Originale erhalten bleiben.",
            
            "🔧 Ihre Demo-Registry enthält einige verwaiste Einträge. Diese können die Systemleistung beeinträchtigen, sind aber sicher entfernbar.",
            
            "✨ In der Vollversion würde ich jetzt eine detaillierte Analyse Ihres echten Systems durchführen und personalisierte Empfehlungen basierend auf Ihren Nutzungsmustern geben."
        ]
        
        import random
        response = random.choice(demo_responses)
        
        # Simuliere Tippt-Indikator
        chat_text.insert("end", "🤖 KI tippt...\\n")
        chat_text.configure(state="disabled")
        chat_text.see("end")
        
        def show_response():
            time.sleep(1.5)  # Simuliere Verarbeitungszeit
            
            chat_text.configure(state="normal")
            # Entferne "tippt..."-Nachricht
            chat_text.delete("end-2l", "end-1l")
            chat_text.insert("end", f"🤖 KI: {response}\\n\\n")
            chat_text.configure(state="disabled")
            chat_text.see("end")
        
        threading.Thread(target=show_response, daemon=True).start()
    
    def show_demo_ai_recommendation(self):
        """Zeigt Demo-KI-Empfehlung."""
        total_files = sum(data["count"] for data in self.demo_scan_results.values())
        total_mb = sum(data["size_mb"] for data in self.demo_scan_results.values())
        
        recommendation = f"""🧠 KI-Analyse (Demo)
        
🚀 Großes Optimierungspotential erkannt!

📊 Scan-Ergebnisse:
• {total_files:,} Dateien analysiert
• {total_mb:.1f} MB Datenmüll gefunden
• 5 Kategorien identifiziert

💡 Empfehlung:
1. Beginnen Sie mit temporären Dateien (höchste Sicherheit)
2. Bereinigen Sie Browser-Cache für Privacy-Schutz  
3. Entfernen Sie Duplikate für Speicheroptimierung
4. Registry-Bereinigung für bessere Performance

⚡ Erwartete Verbesserung:
• 15-25% schnellerer Systemstart
• Reduzierte Fragmentierung
• Mehr verfügbarer Speicherplatz

🔮 In der Vollversion würde die KI Ihr echtes System analysieren und personalisierte Optimierungsstrategien vorschlagen."""
        
        messagebox.showinfo("🤖 KI-Demo-Empfehlung", recommendation)
    
    def run(self):
        """Startet die Demo-Anwendung."""
        print("🚀 Starte GermanCodeZero-Cleaner Demo...")
        print("🎮 Demo-Features:")
        print("   • Moderne 3D-UI-Simulation")
        print("   • Animierte Hologramm-Effekte")
        print("   • KI-Assistent-Demo")
        print("   • System-Scan-Simulation")
        print()
        
        self.root.mainloop()


# ============================================================================
# DEMO ENTRY POINT
# ============================================================================

def main():
    """Demo-Hauptfunktion."""
    print("🛡️ GermanCodeZero-Cleaner Demo")
    print("="*40)
    print("🎯 Dies ist eine Demo-Version ohne externe Abhängigkeiten")
    print("🚀 Vollversion verfügbar mit: python main.py")
    print()
    
    try:
        demo_app = GermanCodeZeroCleanerDemo()
        demo_app.run()
        
    except KeyboardInterrupt:
        print("\\n👋 Demo beendet")
    except Exception as e:
        print(f"❌ Demo-Fehler: {e}")
        print("💡 Versuchen Sie die Vollversion: python main.py")

if __name__ == "__main__":
    main()