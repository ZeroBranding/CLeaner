"""
Erweiterte UI-Komponenten für GermanCodeZero-Cleaner
===================================================

Moderne, animierte UI-Komponenten mit 3D-Effekten und Hologramm-Design.
"""

import tkinter as tk
import customtkinter as ctk
import math
import time
import threading
from typing import Callable, Optional, Any, List, Dict
from config import DARK_THEME, GRAPHICS_CONFIG


# ============================================================================
# ANIMIERTE KOMPONENTEN
# ============================================================================

class AnimatedProgressBar(ctk.CTkProgressBar):
    """Fortschrittsbalken mit Glow-Effekt und Animationen."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.glow_intensity = 0.0
        self.animation_running = False
        
    def set_animated(self, value: float, duration: float = 1.0):
        """Setzt den Wert mit sanfter Animation."""
        if self.animation_running:
            return
            
        start_value = self.get()
        value_diff = value - start_value
        steps = int(duration * 60)  # 60 FPS
        
        self.animation_running = True
        
        def animate_step(step: int):
            if step >= steps:
                self.set(value)
                self.animation_running = False
                return
            
            # Easing-Funktion für sanfte Animation
            progress = step / steps
            eased_progress = 1 - (1 - progress) ** 3  # Ease-out cubic
            
            current_value = start_value + (value_diff * eased_progress)
            self.set(current_value)
            
            # Glow-Effekt
            self.glow_intensity = math.sin(time.time() * 5) * 0.3 + 0.7
            
            self.after(16, lambda: animate_step(step + 1))  # ~60 FPS
        
        animate_step(0)


class HologramButton(ctk.CTkButton):
    """Button mit Hologramm-Effekt und Hover-Animationen."""
    
    def __init__(self, master, **kwargs):
        # Extrahiere custom properties
        self.glow_color = kwargs.pop('glow_color', DARK_THEME["hologram_glow"])
        self.hover_glow = kwargs.pop('hover_glow', True)
        
        super().__init__(master, **kwargs)
        
        self.glow_intensity = 0.0
        self.is_hovering = False
        
        # Bind Hover-Events
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
        
        # Starte Glow-Animation
        self._start_glow_animation()
    
    def _on_hover_enter(self, event):
        """Hover-Enter-Event."""
        self.is_hovering = True
        if self.hover_glow:
            self._animate_glow(1.0)
    
    def _on_hover_leave(self, event):
        """Hover-Leave-Event."""
        self.is_hovering = False
        if self.hover_glow:
            self._animate_glow(0.3)
    
    def _start_glow_animation(self):
        """Startet die Glow-Animation."""
        def animate():
            while True:
                self.glow_intensity = math.sin(time.time() * 2) * 0.2 + 0.5
                if self.is_hovering:
                    self.glow_intensity *= 1.5
                time.sleep(1/60)  # 60 FPS
        
        threading.Thread(target=animate, daemon=True).start()
    
    def _animate_glow(self, target_intensity: float):
        """Animiert den Glow-Effekt."""
        # Vereinfachte Implementierung
        pass


class Matrix3DPanel(ctk.CTkFrame):
    """3D-Panel mit Matrix-Effekt für Datenvisualisierung."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.canvas = tk.Canvas(
            self,
            bg=DARK_THEME["bg_primary"],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        self.matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        self.drops = []
        self.animation_running = False
        
        self._initialize_matrix()
        self._start_animation()
    
    def _initialize_matrix(self):
        """Initialisiert die Matrix-Animation."""
        self.canvas.update_idletasks()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            self.after(100, self._initialize_matrix)
            return
        
        font_size = 12
        columns = width // font_size
        
        self.drops = []
        for i in range(columns):
            self.drops.append({
                'x': i * font_size,
                'y': -font_size,
                'speed': 2 + (i % 3),
                'char_index': 0
            })
    
    def _start_animation(self):
        """Startet die Matrix-Animation."""
        if self.animation_running:
            return
            
        self.animation_running = True
        self._animate_frame()
    
    def _animate_frame(self):
        """Animiert einen Frame der Matrix."""
        if not self.animation_running:
            return
        
        self.canvas.delete("matrix")
        
        height = self.canvas.winfo_height()
        
        for drop in self.drops:
            # Zeichne Zeichen
            char = self.matrix_chars[drop['char_index'] % len(self.matrix_chars)]
            
            # Gradient-Effekt
            alpha = min(255, max(0, 255 - (drop['y'] % 200)))
            color = f"#{0:02x}{alpha:02x}{0:02x}"  # Grün-Gradient
            
            self.canvas.create_text(
                drop['x'], drop['y'],
                text=char,
                fill=color,
                font=("Courier", 12),
                tags="matrix"
            )
            
            # Update Position
            drop['y'] += drop['speed']
            drop['char_index'] += 1
            
            # Reset wenn außerhalb des Bildschirms
            if drop['y'] > height + 50:
                drop['y'] = -20
                drop['char_index'] = 0
        
        # Nächster Frame
        self.after(50, self._animate_frame)
    
    def stop_animation(self):
        """Stoppt die Animation."""
        self.animation_running = False


class DataVisualization3D(ctk.CTkFrame):
    """3D-Datenvisualisierung mit Hardware-Beschleunigung."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.data_points = []
        self.rotation_angle = 0.0
        self.zoom_level = 1.0
        
        # Canvas für 3D-Rendering
        self.canvas = tk.Canvas(
            self,
            bg=DARK_THEME["bg_primary"],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Mouse-Interaktion
        self.canvas.bind("<Button-1>", self._on_mouse_click)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        self._start_rotation_animation()
    
    def update_data(self, scan_result):
        """Aktualisiert die Visualisierung mit neuen Scan-Daten."""
        if not scan_result:
            return
        
        self.data_points = []
        
        # Konvertiere Scan-Ergebnisse zu 3D-Punkten
        for category, items in scan_result.categories.items():
            if not items:
                continue
                
            total_size = sum(item.size for item in items)
            
            # Größe bestimmt Höhe, Anzahl bestimmt Breite
            height = min(total_size / (1024 * 1024), 100)  # Max 100 für Skalierung
            width = min(len(items), 50)
            
            self.data_points.append({
                'category': category,
                'height': height,
                'width': width,
                'color': self._get_category_color(category),
                'items_count': len(items),
                'total_size': total_size
            })
        
        self._render_3d_scene()
    
    def _get_category_color(self, category: str) -> str:
        """Gibt die Farbe für eine Kategorie zurück."""
        colors = {
            "temp_files": DARK_THEME["accent_blue"],
            "cache": DARK_THEME["accent_purple"],
            "logs": DARK_THEME["accent_yellow"],
            "duplicates": DARK_THEME["accent_red"],
            "registry": DARK_THEME["accent_green"]
        }
        return colors.get(category, DARK_THEME["text_secondary"])
    
    def _render_3d_scene(self):
        """Rendert die 3D-Szene."""
        self.canvas.delete("3d")
        
        if not self.data_points:
            # Zeige Platzhalter
            self._render_placeholder()
            return
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_x = width // 2
        center_y = height // 2
        
        # 3D-Transformation (vereinfacht)
        for i, point in enumerate(self.data_points):
            # Position im 3D-Raum
            x = (i - len(self.data_points) / 2) * 80 * self.zoom_level
            y = 0
            z = 0
            
            # Rotation anwenden
            cos_angle = math.cos(self.rotation_angle)
            sin_angle = math.sin(self.rotation_angle)
            
            rotated_x = x * cos_angle - z * sin_angle
            rotated_z = x * sin_angle + z * cos_angle
            
            # Projektion auf 2D
            screen_x = center_x + rotated_x
            screen_y = center_y - point['height'] * 2
            
            # Zeichne 3D-Balken
            self._draw_3d_bar(screen_x, screen_y, point)
    
    def _draw_3d_bar(self, x: float, y: float, data_point: Dict):
        """Zeichnet einen 3D-Balken für eine Datenkategorie."""
        width = 40
        height = data_point['height'] * 2
        depth = 20
        
        # Hauptbalken
        self.canvas.create_rectangle(
            x - width//2, y,
            x + width//2, y + height,
            fill=data_point['color'],
            outline=DARK_THEME["hologram_glow"],
            width=2,
            tags="3d"
        )
        
        # 3D-Tiefe (vereinfacht)
        self.canvas.create_polygon(
            x + width//2, y,
            x + width//2 + depth, y - depth,
            x + width//2 + depth, y + height - depth,
            x + width//2, y + height,
            fill=data_point['color'],
            outline=DARK_THEME["hologram_glow"],
            tags="3d"
        )
        
        # Top-Fläche
        self.canvas.create_polygon(
            x - width//2, y,
            x + width//2, y,
            x + width//2 + depth, y - depth,
            x - width//2 + depth, y - depth,
            fill=data_point['color'],
            outline=DARK_THEME["hologram_glow"],
            tags="3d"
        )
        
        # Label
        size_mb = data_point['total_size'] / (1024 * 1024)
        label_text = f"{data_point['category']}\n{data_point['items_count']} Dateien\n{size_mb:.1f} MB"
        
        self.canvas.create_text(
            x, y + height + 30,
            text=label_text,
            fill=DARK_THEME["text_primary"],
            font=("Arial", 8),
            justify="center",
            tags="3d"
        )
    
    def _render_placeholder(self):
        """Rendert Platzhalter-Grafik."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_x = width // 2
        center_y = height // 2
        
        # Hologramm-Grid
        grid_size = 20
        
        for i in range(0, width, grid_size):
            alpha = int(50 + 30 * math.sin(time.time() + i * 0.1))
            color = f"#{0:02x}{alpha:02x}{alpha:02x}"
            
            self.canvas.create_line(
                i, 0, i, height,
                fill=color,
                width=1,
                tags="3d"
            )
        
        for i in range(0, height, grid_size):
            alpha = int(50 + 30 * math.sin(time.time() + i * 0.1))
            color = f"#{0:02x}{alpha:02x}{alpha:02x}"
            
            self.canvas.create_line(
                0, i, width, i,
                fill=color,
                width=1,
                tags="3d"
            )
        
        # Zentraler Text
        self.canvas.create_text(
            center_x, center_y,
            text="🌟 3D-HOLOGRAMM-VISUALISIERUNG\n\n💫 Bereit für System-Scan\n🔮 Hardware-beschleunigte Analyse\n✨ Echtzeit-Datenvisualisierung",
            fill=DARK_THEME["hologram_glow"],
            font=("Arial", 14, "bold"),
            justify="center",
            tags="3d"
        )
    
    def _start_rotation_animation(self):
        """Startet die Rotations-Animation."""
        def animate():
            while True:
                self.rotation_angle += 0.01
                if self.rotation_angle > 2 * math.pi:
                    self.rotation_angle = 0
                
                self.after(0, self._render_3d_scene)
                time.sleep(1/60)  # 60 FPS
        
        threading.Thread(target=animate, daemon=True).start()
    
    def _on_mouse_click(self, event):
        """Mouse-Click-Event."""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
    
    def _on_mouse_drag(self, event):
        """Mouse-Drag-Event für Rotation."""
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        
        self.rotation_angle += dx * 0.01
        
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
        self._render_3d_scene()
    
    def _on_mouse_wheel(self, event):
        """Mouse-Wheel-Event für Zoom."""
        zoom_factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_level *= zoom_factor
        self.zoom_level = max(0.5, min(3.0, self.zoom_level))
        
        self._render_3d_scene()


class NeonLabel(ctk.CTkLabel):
    """Label mit Neon-Glow-Effekt."""
    
    def __init__(self, master, glow_color=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.glow_color = glow_color or DARK_THEME["neon_pink"]
        self.glow_intensity = 0.0
        
        self._start_glow_animation()
    
    def _start_glow_animation(self):
        """Startet die Glow-Animation."""
        def animate():
            while True:
                self.glow_intensity = math.sin(time.time() * 3) * 0.5 + 0.5
                # In echter Implementierung würde hier der Glow-Effekt angewendet
                time.sleep(1/30)  # 30 FPS für Labels
        
        threading.Thread(target=animate, daemon=True).start()


class ParticleSystem(ctk.CTkFrame):
    """Partikelsystem für Hintergrund-Effekte."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.canvas = tk.Canvas(
            self,
            bg=DARK_THEME["bg_primary"],
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        self.particles = []
        self.max_particles = 50
        
        self._initialize_particles()
        self._start_particle_animation()
    
    def _initialize_particles(self):
        """Initialisiert die Partikel."""
        import random
        
        for _ in range(self.max_particles):
            particle = {
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'size': random.randint(1, 3),
                'color': random.choice([
                    DARK_THEME["accent_blue"],
                    DARK_THEME["accent_purple"],
                    DARK_THEME["hologram_glow"]
                ]),
                'life': random.uniform(0.5, 1.0)
            }
            self.particles.append(particle)
    
    def _start_particle_animation(self):
        """Startet die Partikel-Animation."""
        def animate():
            while True:
                self._update_particles()
                self.after(0, self._render_particles)
                time.sleep(1/60)  # 60 FPS
        
        threading.Thread(target=animate, daemon=True).start()
    
    def _update_particles(self):
        """Aktualisiert Partikel-Positionen."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        for particle in self.particles:
            # Update Position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Bounce off edges
            if particle['x'] <= 0 or particle['x'] >= width:
                particle['vx'] *= -1
            if particle['y'] <= 0 or particle['y'] >= height:
                particle['vy'] *= -1
            
            # Update Life
            particle['life'] -= 0.001
            
            # Respawn if dead
            if particle['life'] <= 0:
                import random
                particle['x'] = random.randint(0, width)
                particle['y'] = random.randint(0, height)
                particle['life'] = 1.0
    
    def _render_particles(self):
        """Rendert die Partikel."""
        self.canvas.delete("particles")
        
        for particle in self.particles:
            alpha = int(particle['life'] * 255)
            size = particle['size']
            
            self.canvas.create_oval(
                particle['x'] - size, particle['y'] - size,
                particle['x'] + size, particle['y'] + size,
                fill=particle['color'],
                outline="",
                tags="particles"
            )


class AnimatedStats(ctk.CTkFrame):
    """Animierte Statistik-Anzeige."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.stats = {}
        self.animated_values = {}
        
        self._create_stat_displays()
    
    def _create_stat_displays(self):
        """Erstellt die Statistik-Anzeigen."""
        # Grid-Layout für Statistiken
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # CPU-Nutzung
        self.cpu_frame = self._create_stat_frame("💻 CPU", "0%", DARK_THEME["accent_blue"])
        self.cpu_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # RAM-Nutzung
        self.ram_frame = self._create_stat_frame("🧠 RAM", "0%", DARK_THEME["accent_purple"])
        self.ram_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Gefundene Dateien
        self.files_frame = self._create_stat_frame("📁 Dateien", "0", DARK_THEME["accent_green"])
        self.files_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Freigegeben Speicher
        self.storage_frame = self._create_stat_frame("💾 Speicher", "0 MB", DARK_THEME["accent_red"])
        self.storage_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Starte Live-Updates
        self._start_live_updates()
    
    def _create_stat_frame(self, title: str, initial_value: str, color: str) -> ctk.CTkFrame:
        """Erstellt einen Statistik-Frame."""
        frame = ctk.CTkFrame(
            self,
            fg_color=DARK_THEME["bg_tertiary"],
            corner_radius=10
        )
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color
        )
        title_label.pack(pady=5)
        
        value_label = ctk.CTkLabel(
            frame,
            text=initial_value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=DARK_THEME["text_primary"]
        )
        value_label.pack(pady=5)
        
        # Speichere Label-Referenz
        frame.value_label = value_label
        
        return frame
    
    def _start_live_updates(self):
        """Startet Live-Updates der Statistiken."""
        def update_stats():
            while True:
                try:
                    import psutil
                    
                    # CPU-Nutzung
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.after(0, lambda: self._update_stat_display(
                        self.cpu_frame.value_label, f"{cpu_percent:.1f}%"
                    ))
                    
                    # RAM-Nutzung
                    memory = psutil.virtual_memory()
                    ram_percent = memory.percent
                    self.after(0, lambda: self._update_stat_display(
                        self.ram_frame.value_label, f"{ram_percent:.1f}%"
                    ))
                    
                except Exception as e:
                    print(f"Statistik-Update fehlgeschlagen: {e}")
                
                time.sleep(2)  # Update alle 2 Sekunden
        
        threading.Thread(target=update_stats, daemon=True).start()
    
    def _update_stat_display(self, label: ctk.CTkLabel, new_value: str):
        """Aktualisiert eine Statistik-Anzeige mit Animation."""
        label.configure(text=new_value)
    
    def update_scan_stats(self, scan_result):
        """Aktualisiert Statistiken basierend auf Scan-Ergebnissen."""
        if not scan_result:
            return
        
        # Dateien-Anzahl
        self.files_frame.value_label.configure(text=f"{scan_result.total_files:,}")
        
        # Speicher-Größe
        size_mb = scan_result.total_size / (1024 * 1024)
        if size_mb >= 1024:
            size_text = f"{size_mb / 1024:.1f} GB"
        else:
            size_text = f"{size_mb:.1f} MB"
        
        self.storage_frame.value_label.configure(text=size_text)


# ============================================================================
# ERWEITERTE DIALOGE
# ============================================================================

class ModernDialog(ctk.CTkToplevel):
    """Basis-Klasse für moderne Dialoge mit Animationen."""
    
    def __init__(self, parent, title: str, size: tuple = (400, 300)):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.configure(fg_color=DARK_THEME["bg_primary"])
        
        # Zentriere Dialog
        self.transient(parent)
        self.grab_set()
        
        self._center_window()
        self._setup_animations()
    
    def _center_window(self):
        """Zentriert das Fenster auf dem Bildschirm."""
        self.update_idletasks()
        
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_animations(self):
        """Setzt Eingangs-Animation auf."""
        # Fade-in-Effekt
        self.attributes("-alpha", 0.0)
        self._fade_in()
    
    def _fade_in(self, alpha: float = 0.0):
        """Fade-in-Animation."""
        if alpha >= 1.0:
            return
        
        self.attributes("-alpha", alpha)
        self.after(16, lambda: self._fade_in(alpha + 0.05))


class ConfirmationDialog(ModernDialog):
    """Moderner Bestätigungs-Dialog."""
    
    def __init__(self, parent, title: str, message: str, callback: Callable[[bool], None]):
        super().__init__(parent, title, (450, 200))
        
        self.callback = callback
        self.result = False
        
        self._create_content(message)
    
    def _create_content(self, message: str):
        """Erstellt den Dialog-Inhalt."""
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text="⚠️",
            font=ctk.CTkFont(size=32),
            text_color=DARK_THEME["accent_yellow"]
        )
        icon_label.pack(pady=15)
        
        # Nachricht
        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_primary"],
            wraplength=400,
            justify="center"
        )
        message_label.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        yes_button = HologramButton(
            button_frame,
            text="✅ Ja",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=DARK_THEME["accent_green"],
            command=self._on_yes,
            glow_color=DARK_THEME["accent_green"]
        )
        yes_button.pack(side="left", padx=10)
        
        no_button = HologramButton(
            button_frame,
            text="❌ Nein",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=DARK_THEME["accent_red"],
            command=self._on_no,
            glow_color=DARK_THEME["accent_red"]
        )
        no_button.pack(side="left", padx=10)
    
    def _on_yes(self):
        """Ja-Button geklickt."""
        self.result = True
        self.callback(True)
        self.destroy()
    
    def _on_no(self):
        """Nein-Button geklickt."""
        self.result = False
        self.callback(False)
        self.destroy()


class ProgressDialog(ModernDialog):
    """Fortschritts-Dialog mit Animationen."""
    
    def __init__(self, parent, title: str, total_steps: int):
        super().__init__(parent, title, (400, 150))
        
        self.total_steps = total_steps
        self.current_step = 0
        
        self._create_content()
    
    def _create_content(self):
        """Erstellt den Dialog-Inhalt."""
        # Status-Label
        self.status_label = ctk.CTkLabel(
            self,
            text="Initialisierung...",
            font=ctk.CTkFont(size=14),
            text_color=DARK_THEME["text_primary"]
        )
        self.status_label.pack(pady=20)
        
        # Animierter Progress Bar
        self.progress_bar = AnimatedProgressBar(
            self,
            width=350,
            height=20,
            fg_color=DARK_THEME["bg_secondary"],
            progress_color=DARK_THEME["accent_blue"]
        )
        self.progress_bar.pack(pady=10)
        
        # Schritt-Anzeige
        self.step_label = ctk.CTkLabel(
            self,
            text=f"Schritt 0 von {self.total_steps}",
            font=ctk.CTkFont(size=10),
            text_color=DARK_THEME["text_secondary"]
        )
        self.step_label.pack(pady=5)
    
    def update_progress(self, step: int, status: str):
        """Aktualisiert den Fortschritt."""
        self.current_step = step
        progress = step / self.total_steps
        
        self.status_label.configure(text=status)
        self.progress_bar.set_animated(progress)
        self.step_label.configure(text=f"Schritt {step} von {self.total_steps}")
    
    def complete(self, success_message: str = "Abgeschlossen!"):
        """Markiert den Vorgang als abgeschlossen."""
        self.status_label.configure(text=success_message)
        self.progress_bar.set_animated(1.0)
        self.step_label.configure(text=f"✅ Erfolgreich abgeschlossen")
        
        # Auto-close nach 2 Sekunden
        self.after(2000, self.destroy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_glow_effect(widget, glow_color: str, intensity: float = 1.0):
    """Erstellt einen Glow-Effekt um ein Widget."""
    # Vereinfachte Implementierung - in echter App würde hier
    # ein echter Glow-Effekt mit Canvas oder Custom Drawing erstellt
    pass

def animate_widget_entrance(widget, animation_type: str = "fade_in"):
    """Animiert das Erscheinen eines Widgets."""
    if animation_type == "fade_in":
        # Fade-in-Animation
        pass
    elif animation_type == "slide_up":
        # Slide-up-Animation
        pass
    elif animation_type == "scale_in":
        # Scale-in-Animation
        pass

def create_hologram_border(parent, width: int, height: int) -> tk.Canvas:
    """Erstellt einen animierten Hologramm-Rahmen."""
    canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=DARK_THEME["bg_primary"],
        highlightthickness=0
    )
    
    def animate_border():
        while True:
            canvas.delete("border")
            
            # Animierte Eckpunkte
            time_offset = time.time() * 2
            
            for i in range(4):
                angle = (i * math.pi / 2) + time_offset
                glow = (math.sin(angle) + 1) / 2
                
                color_intensity = int(100 + glow * 155)
                color = f"#{0:02x}{color_intensity:02x}{color_intensity:02x}"
                
                # Zeichne Eckpunkte
                corner_size = 20
                if i == 0:  # Top-left
                    canvas.create_line(0, 0, corner_size, 0, fill=color, width=3, tags="border")
                    canvas.create_line(0, 0, 0, corner_size, fill=color, width=3, tags="border")
                elif i == 1:  # Top-right
                    canvas.create_line(width-corner_size, 0, width, 0, fill=color, width=3, tags="border")
                    canvas.create_line(width, 0, width, corner_size, fill=color, width=3, tags="border")
                elif i == 2:  # Bottom-right
                    canvas.create_line(width, height-corner_size, width, height, fill=color, width=3, tags="border")
                    canvas.create_line(width-corner_size, height, width, height, fill=color, width=3, tags="border")
                elif i == 3:  # Bottom-left
                    canvas.create_line(0, height-corner_size, 0, height, fill=color, width=3, tags="border")
                    canvas.create_line(0, height, corner_size, height, fill=color, width=3, tags="border")
            
            time.sleep(1/30)  # 30 FPS
    
    threading.Thread(target=animate_border, daemon=True).start()
    return canvas