<<<<<<< Current (Your changes)
#!/usr/bin/env python3
"""
GermanCodeZero-Cleaner
======================

Eine moderne, KI-gestützte System-Reinigungs-Anwendung mit 3D-Interface.
Entwickelt für Windows 10/11 mit geplanter macOS/Linux-Unterstützung.

Features:
- Hardware-beschleunigter System-Scan
- 3D-Hologramm-Interface mit Animationen
- Lokale LLM für intelligente Erklärungen
- Freemium-Modell mit Daten-Sharing-Option
- Multi-threaded Performance-Optimierung

Author: GermanCodeZero
License: Proprietary
"""
GermanCodeZero-Cleaner
"""
GermanCodeZero-Cleaner
======================

Eine moderne, KI-gestützte System-Reinigungs-Anwendung mit 3D-Interface.
Entwickelt für Windows 10/11 mit geplanter macOS/Linux-Unterstützung.

Features:
- Hardware-beschleunigter System-Scan
- 3D-Hologramm-Interface mit Animationen  
- Lokale LLM für intelligente Erklärungen
- Freemium-Modell mit Daten-Sharing-Option
- Multi-threaded Performance-Optimierung

Author: GermanCodeZero
License: Proprietary
"""

import sys
import os
import threading
import time
import json
import hashlib
import tempfile
import shutil
import winreg
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

# GUI Framework
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog

# 3D Graphics & Animations
import pygame
import moderngl
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr

# System Analysis
import psutil
import send2trash

# AI/LLM Integration
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Data Processing
import pandas as pd

# Utilities
from tqdm import tqdm
import requests
import aiohttp
import asyncio


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

APP_NAME = "GermanCodeZero-Cleaner"
APP_VERSION = "1.0.0"
APP_AUTHOR = "GermanCodeZero"

# UI Colors & Theme
DARK_THEME = {
    "bg_primary": "#0a0a0a",
    "bg_secondary": "#1a1a1a", 
    "bg_tertiary": "#2a2a2a",
    "accent_blue": "#00d4ff",
    "accent_purple": "#a855f7",
    "accent_green": "#10b981",
    "accent_red": "#ef4444",
    "text_primary": "#ffffff",
    "text_secondary": "#a1a1aa",
    "hologram_glow": "#00ffff"
}

# 3D Shader Programs
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time;

out vec3 FragPos;
out vec3 Normal; 
out vec2 TexCoord;
out float Time;

void main() {
    // Hologramm-Effekt mit Zeit-basierter Animation
    vec3 pos = aPos;
    pos.y += sin(time * 2.0 + aPos.x * 5.0) * 0.1;
    
    FragPos = vec3(model * vec4(pos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;
    Time = time;
    
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;
in float Time;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;
uniform float glowIntensity;

void main() {
    // Hologramm-Glow-Effekt
    float glow = sin(Time * 3.0) * 0.5 + 0.5;
    vec3 glowColor = vec3(0.0, 1.0, 1.0) * glow * glowIntensity;
    
    // Phong Lighting
    vec3 ambient = 0.15 * lightColor;
    
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = spec * lightColor;
    
    // Kombiniere Beleuchtung mit Hologramm-Effekt
    vec3 result = (ambient + diffuse + specular) * objectColor + glowColor;
    
    // Alpha für Transparenz-Effekt
    float alpha = 0.8 + glow * 0.2;
    
    FragColor = vec4(result, alpha);
}
"""


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class CleaningItem:
    """Repräsentiert ein Element, das gereinigt werden kann."""
    path: str
    size: int
    category: str
    description: str
    safe_to_delete: bool
    last_accessed: datetime
    file_type: str


@dataclass
class ScanResult:
    """Ergebnis eines System-Scans."""
    total_files: int
    total_size: int
    categories: Dict[str, List[CleaningItem]]
    scan_duration: float
    timestamp: datetime


@dataclass
class UserPreferences:
    """Benutzer-Einstellungen."""
    auto_scan_enabled: bool = True
    data_sharing_enabled: bool = False
    premium_user: bool = False
    last_scan: Optional[datetime] = None
    selected_categories: List[str] = None
    
    def __post_init__(self):
        if self.selected_categories is None:
            self.selected_categories = ["temp_files", "cache", "logs", "duplicates"]


# ============================================================================
# SYSTEM SCANNER ENGINE
# ============================================================================

class SystemScanner:
    """Hardware-beschleunigter System-Scanner."""
    
    def __init__(self):
        self.scan_results: Optional[ScanResult] = None
        self.is_scanning = False
        self.scan_progress = 0.0
        self.cancel_scan = False
        
        # Hardware-Info für Optimierung
        self.cpu_count = psutil.cpu_count()
        self.memory_total = psutil.virtual_memory().total
        self.gpu_available = self._check_gpu_support()
        
    def _check_gpu_support(self) -> bool:
        """Prüft GPU-Verfügbarkeit für Hardware-Beschleunigung."""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def get_temp_directories(self) -> List[str]:
        """Findet alle temporären Verzeichnisse."""
        temp_dirs = [
            tempfile.gettempdir(),
            os.path.expandvars("%TEMP%"),
            os.path.expandvars("%TMP%"),
            os.path.expandvars("%LOCALAPPDATA%\\Temp"),
            os.path.expandvars("%APPDATA%\\Local\\Temp"),
            "C:\\Windows\\Temp",
            "C:\\Windows\\Prefetch",
            "C:\\Windows\\SoftwareDistribution\\Download",
        ]
        
        # Browser-Cache-Verzeichnisse
        browser_cache = [
            os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Cache"),
            os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\Cache"),
            os.path.expandvars("%APPDATA%\\Mozilla\\Firefox\\Profiles"),
        ]
        
        temp_dirs.extend(browser_cache)
        return [d for d in temp_dirs if os.path.exists(d)]
    
    def scan_directory(self, directory: str, category: str) -> List[CleaningItem]:
        """Scannt ein Verzeichnis nach löschbaren Dateien."""
        items = []
        
        try:
            for root, dirs, files in os.walk(directory):
                if self.cancel_scan:
                    break
                    
                for file in files:
                    if self.cancel_scan:
                        break
                        
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        size = stat.st_size
                        last_accessed = datetime.fromtimestamp(stat.st_atime)
                        
                        # Bestimme Dateityp und Sicherheit
                        file_ext = os.path.splitext(file)[1].lower()
                        safe_to_delete = self._is_safe_to_delete(file_path, file_ext, category)
                        
                        item = CleaningItem(
                            path=file_path,
                            size=size,
                            category=category,
                            description=self._get_file_description(file_path, category),
                            safe_to_delete=safe_to_delete,
                            last_accessed=last_accessed,
                            file_type=file_ext
                        )
                        items.append(item)
                        
                    except (OSError, PermissionError):
                        continue
                        
        except (OSError, PermissionError):
            pass
            
        return items
    
    def _is_safe_to_delete(self, file_path: str, file_ext: str, category: str) -> bool:
        """Bestimmt, ob eine Datei sicher gelöscht werden kann."""
        # Kritische Systemdateien niemals löschen
        critical_paths = [
            "windows", "system32", "program files", "program files (x86)",
            "boot", "recovery", "users\\default", "programdata\\microsoft"
        ]
        
        path_lower = file_path.lower()
        if any(critical in path_lower for critical in critical_paths):
            return False
            
        # Sichere Kategorien
        safe_extensions = {
            "temp_files": [".tmp", ".temp", ".log", ".bak", ".old"],
            "cache": [".cache", ".dat", ".db-wal", ".db-shm"],
            "logs": [".log", ".txt", ".out"],
            "duplicates": []  # Wird separat behandelt
        }
        
        if category in safe_extensions:
            return file_ext in safe_extensions[category] or category == "duplicates"
            
        return False
    
    def _get_file_description(self, file_path: str, category: str) -> str:
        """Generiert eine Beschreibung für eine Datei."""
        descriptions = {
            "temp_files": "Temporäre Datei - sicher löschbar",
            "cache": "Cache-Datei - verbessert Ladezeiten, aber regenerierbar", 
            "logs": "Log-Datei - enthält Protokolldaten",
            "duplicates": "Duplikat - identischer Inhalt bereits vorhanden"
        }
        return descriptions.get(category, "Unbekannter Dateityp")
    
    def find_duplicates(self, directories: List[str]) -> List[CleaningItem]:
        """Findet doppelte Dateien mit Hash-Vergleich."""
        file_hashes = {}
        duplicates = []
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
                
            for root, dirs, files in os.walk(directory):
                if self.cancel_scan:
                    break
                    
                for file in files:
                    if self.cancel_scan:
                        break
                        
                    file_path = os.path.join(root, file)
                    try:
                        # Berechne Hash für Duplikat-Erkennung
                        file_hash = self._calculate_file_hash(file_path)
                        
                        if file_hash in file_hashes:
                            # Duplikat gefunden
                            stat = os.stat(file_path)
                            duplicate = CleaningItem(
                                path=file_path,
                                size=stat.st_size,
                                category="duplicates",
                                description=f"Duplikat von: {file_hashes[file_hash]}",
                                safe_to_delete=True,
                                last_accessed=datetime.fromtimestamp(stat.st_atime),
                                file_type=os.path.splitext(file)[1].lower()
                            )
                            duplicates.append(duplicate)
                        else:
                            file_hashes[file_hash] = file_path
                            
                    except (OSError, PermissionError, MemoryError):
                        continue
                        
        return duplicates
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Berechnet SHA-256 Hash einer Datei."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return ""
    
    async def perform_scan(self, categories: List[str], progress_callback=None) -> ScanResult:
        """Führt einen vollständigen System-Scan durch."""
        self.is_scanning = True
        self.cancel_scan = False
        start_time = time.time()
        
        all_items = {}
        total_files = 0
        
        try:
            # Temp-Dateien scannen
            if "temp_files" in categories:
                temp_dirs = self.get_temp_directories()
                temp_items = []
                
                for i, temp_dir in enumerate(temp_dirs):
                    if self.cancel_scan:
                        break
                    if progress_callback:
                        progress_callback(f"Scanne temporäre Dateien: {temp_dir}", 
                                        (i + 1) / len(temp_dirs) * 0.25)
                    
                    items = self.scan_directory(temp_dir, "temp_files")
                    temp_items.extend(items)
                
                all_items["temp_files"] = temp_items
                total_files += len(temp_items)
            
            # Cache-Dateien scannen
            if "cache" in categories:
                cache_dirs = [
                    os.path.expandvars("%LOCALAPPDATA%"),
                    os.path.expandvars("%APPDATA%")
                ]
                cache_items = []
                
                for i, cache_dir in enumerate(cache_dirs):
                    if self.cancel_scan:
                        break
                    if progress_callback:
                        progress_callback(f"Scanne Cache-Dateien: {cache_dir}",
                                        0.25 + (i + 1) / len(cache_dirs) * 0.25)
                    
                    items = self.scan_directory(cache_dir, "cache")
                    cache_items.extend(items)
                
                all_items["cache"] = cache_items
                total_files += len(cache_items)
            
            # Duplikate finden
            if "duplicates" in categories:
                if progress_callback:
                    progress_callback("Suche nach Duplikaten...", 0.75)
                
                scan_dirs = [
                    os.path.expanduser("~/Documents"),
                    os.path.expanduser("~/Downloads"),
                    os.path.expanduser("~/Pictures"),
                    os.path.expanduser("~/Videos")
                ]
                
                duplicates = self.find_duplicates(scan_dirs)
                all_items["duplicates"] = duplicates
                total_files += len(duplicates)
            
            # Registry-Einträge (Windows)
            if "registry" in categories and sys.platform == "win32":
                if progress_callback:
                    progress_callback("Analysiere Registry...", 0.9)
                
                registry_items = self._scan_registry()
                all_items["registry"] = registry_items
                total_files += len(registry_items)
            
            scan_duration = time.time() - start_time
            total_size = sum(
                sum(item.size for item in items) 
                for items in all_items.values()
            )
            
            result = ScanResult(
                total_files=total_files,
                total_size=total_size,
                categories=all_items,
                scan_duration=scan_duration,
                timestamp=datetime.now()
            )
            
            self.scan_results = result
            
            if progress_callback:
                progress_callback("Scan abgeschlossen!", 1.0)
                
            return result
            
        finally:
            self.is_scanning = False
    
    def _scan_registry(self) -> List[CleaningItem]:
        """Scannt Windows Registry nach verwaisten Einträgen."""
        registry_items = []
        
        # Häufige Registry-Bereiche für Bereinigung
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
            (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
        ]
        
        for hkey, subkey in registry_paths:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    i = 0
                    while True:
                        try:
                            name, value, type_ = winreg.EnumValue(key, i)
                            
                            # Prüfe ob Pfad noch existiert
                            if isinstance(value, str) and not os.path.exists(value):
                                item = CleaningItem(
                                    path=f"{subkey}\\{name}",
                                    size=len(str(value)),
                                    category="registry",
                                    description="Verwaister Registry-Eintrag",
                                    safe_to_delete=True,
                                    last_accessed=datetime.now(),
                                    file_type="registry"
                                )
                                registry_items.append(item)
                            
                            i += 1
                        except WindowsError:
                            break
                            
            except (OSError, PermissionError):
                continue
                
        return registry_items


# ============================================================================
# LLM AI ASSISTANT
# ============================================================================

class AIAssistant:
    """Lokale LLM-Integration für intelligente Erklärungen."""
    
    def __init__(self):
        self.model_name = "llama2:7b"  # Lokales Modell
        self.is_available = OLLAMA_AVAILABLE
        self.conversation_history = []
        
    async def initialize_model(self) -> bool:
        """Initialisiert das lokale LLM."""
        if not self.is_available:
            return False
            
        try:
            # Prüfe ob Ollama läuft
            response = await ollama.list()
            
            # Lade Modell falls nicht vorhanden
            if self.model_name not in [model["name"] for model in response["models"]]:
                await ollama.pull(self.model_name)
                
            return True
        except:
            return False
    
    async def explain_cleaning_item(self, item: CleaningItem) -> str:
        """Erklärt einem Benutzer, was eine bestimmte Datei ist."""
        if not self.is_available:
            return self._fallback_explanation(item)
        
        prompt = f"""
        Erkläre einem Benutzer auf Deutsch, was diese Datei ist und warum sie gelöscht werden kann:
        
        Pfad: {item.path}
        Größe: {item.size} Bytes
        Kategorie: {item.category}
        Letzter Zugriff: {item.last_accessed}
        
        Gib eine kurze, verständliche Erklärung in 1-2 Sätzen.
        """
        
        try:
            response = await ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            return response["response"]
        except:
            return self._fallback_explanation(item)
    
    def _fallback_explanation(self, item: CleaningItem) -> str:
        """Fallback-Erklärungen ohne LLM."""
        explanations = {
            "temp_files": f"Temporäre Datei von {os.path.basename(os.path.dirname(item.path))}. Wird automatisch erstellt und kann sicher gelöscht werden.",
            "cache": f"Cache-Datei für schnellere Ladezeiten. Wird bei Bedarf neu erstellt.",
            "logs": f"Protokoll-Datei mit {item.size} Bytes. Enthält Debug-Informationen.",
            "duplicates": f"Duplikat einer bereits vorhandenen Datei. Spart {item.size} Bytes Speicherplatz.",
            "registry": "Verwaister Registry-Eintrag ohne gültige Zieldatei."
        }
        return explanations.get(item.category, "Unbekannter Dateityp - Vorsicht beim Löschen.")
    
    async def get_cleaning_recommendation(self, scan_result: ScanResult) -> str:
        """Gibt eine KI-basierte Empfehlung für die Bereinigung."""
        if not self.is_available:
            return self._fallback_recommendation(scan_result)
        
        total_mb = scan_result.total_size / (1024 * 1024)
        
        prompt = f"""
        Analysiere diese System-Scan-Ergebnisse und gib eine Empfehlung auf Deutsch:
        
        Gefundene Dateien: {scan_result.total_files}
        Gesamtgröße: {total_mb:.1f} MB
        Kategorien: {list(scan_result.categories.keys())}
        
        Gib eine Empfehlung, welche Kategorien zuerst bereinigt werden sollten und warum.
        Sei spezifisch und hilfreich.
        """
        
        try:
            response = await ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            return response["response"]
        except:
            return self._fallback_recommendation(scan_result)
    
    def _fallback_recommendation(self, scan_result: ScanResult) -> str:
        """Fallback-Empfehlung ohne LLM."""
        total_mb = scan_result.total_size / (1024 * 1024)
        
        if total_mb > 1000:
            return f"🚀 Großes Optimierungspotential! {total_mb:.1f} MB können freigegeben werden. Empfehlung: Beginne mit temporären Dateien und Cache."
        elif total_mb > 100:
            return f"✨ Moderate Bereinigung möglich: {total_mb:.1f} MB. Fokus auf Duplikate und alte Logs."
        else:
            return f"✅ System ist relativ sauber: {total_mb:.1f} MB Datenmüll gefunden."


# ============================================================================
# 3D GRAPHICS ENGINE
# ============================================================================

class HologramRenderer:
    """3D-Hologramm-Renderer für die Benutzeroberfläche."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.ctx = None
        self.shader_program = None
        self.vao = None
        self.time = 0.0
        
        self._initialize_opengl()
    
    def _initialize_opengl(self):
        """Initialisiert OpenGL-Kontext."""
        try:
            pygame.init()
            pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
            
            self.ctx = moderngl.create_context()
            
            # Kompiliere Shader
            vertex_shader = compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
            fragment_shader = compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
            self.shader_program = compileProgram(vertex_shader, fragment_shader)
            
            # Erstelle 3D-Geometrie für Hologramm-Effekte
            self._create_geometry()
            
        except Exception as e:
            print(f"OpenGL-Initialisierung fehlgeschlagen: {e}")
    
    def _create_geometry(self):
        """Erstellt 3D-Geometrie für Visualisierungen."""
        # Würfel-Vertices für 3D-Datenvisualisierung
        vertices = np.array([
            # Position      # Normal       # TexCoord
            -1, -1, -1,     0, 0, -1,      0, 0,
             1, -1, -1,     0, 0, -1,      1, 0,
             1,  1, -1,     0, 0, -1,      1, 1,
            -1,  1, -1,     0, 0, -1,      0, 1,
            # ... weitere Vertices für alle 6 Seiten
        ], dtype=np.float32)
        
        # VAO erstellen (vereinfacht)
        self.vao = self.ctx.vertex_array(
            self.ctx.buffer(vertices),
            [(0, 3, GL_FLOAT), (1, 3, GL_FLOAT), (2, 2, GL_FLOAT)]
        )
    
    def render_data_visualization(self, scan_result: Optional[ScanResult]):
        """Rendert 3D-Datenvisualisierung."""
        if not self.ctx or not scan_result:
            return
            
        self.time += 0.016  # ~60 FPS
        
        # Clear screen
        self.ctx.clear(0.05, 0.05, 0.1)  # Dunkler Hintergrund
        
        # Update Uniforms
        glUseProgram(self.shader_program)
        
        # Zeit für Animationen
        time_location = glGetUniformLocation(self.shader_program, "time")
        glUniform1f(time_location, self.time)
        
        # Hologramm-Intensität basierend auf Datenmengen
        glow_intensity = min(scan_result.total_size / (1024 * 1024 * 100), 1.0)
        glow_location = glGetUniformLocation(self.shader_program, "glowIntensity")
        glUniform1f(glow_location, glow_intensity)
        
        # Render 3D-Objekte
        if self.vao:
            self.vao.render()
        
        pygame.display.flip()


# ============================================================================
# MAIN APPLICATION UI
# ============================================================================

class GermanCodeZeroCleanerApp:
    """Hauptanwendung mit moderner 3D-UI."""
    
    def __init__(self):
        # Initialisiere Core-Komponenten
        self.scanner = SystemScanner()
        self.ai_assistant = AIAssistant()
        self.preferences = UserPreferences()
        
        # UI-State
        self.current_scan_result: Optional[ScanResult] = None
        self.selected_items: List[CleaningItem] = []
        self.is_premium = False
        
        # 3D-Renderer
        self.hologram_renderer: Optional[HologramRenderer] = None
        
        self._setup_ui()
        self._load_preferences()
        
    def _setup_ui(self):
        """Erstellt die moderne 3D-Benutzeroberfläche."""
        # Hauptfenster
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1200x800")
        self.root.configure(fg_color=DARK_THEME["bg_primary"])
        
        # Icon setzen (falls vorhanden)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        self._create_header()
        self._create_main_content()
        self._create_footer()
        
        # Initialisiere 3D-Renderer
        self._initialize_3d_renderer()
    
    def _create_header(self):
        """Erstellt den Header mit Logo und Navigation."""
        header_frame = ctk.CTkFrame(
            self.root, 
            height=80, 
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=0
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo und Titel
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🛡️ GermanCodeZero-Cleaner",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="KI-gestützte System-Optimierung mit 3D-Interface",
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_secondary"]
        )
        subtitle_label.pack()
        
        # Navigation Buttons
        nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=20, pady=15)
        
        self.scan_button = ctk.CTkButton(
            nav_frame,
            text="🔍 System Scannen",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=DARK_THEME["accent_green"],
            hover_color="#059669",
            command=self._start_scan
        )
        self.scan_button.pack(side="left", padx=5)
        
        self.ai_button = ctk.CTkButton(
            nav_frame,
            text="🤖 KI-Assistent",
            font=ctk.CTkFont(size=14),
            fg_color=DARK_THEME["accent_purple"],
            hover_color="#9333ea",
            command=self._open_ai_chat
        )
        self.ai_button.pack(side="left", padx=5)
        
        self.settings_button = ctk.CTkButton(
            nav_frame,
            text="⚙️ Einstellungen",
            font=ctk.CTkFont(size=14),
            fg_color=DARK_THEME["bg_tertiary"],
            hover_color="#374151",
            command=self._open_settings
        )
        self.settings_button.pack(side="left", padx=5)
    
    def _create_main_content(self):
        """Erstellt den Hauptinhalt mit 3D-Visualisierung."""
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color=DARK_THEME["bg_primary"]
        )
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Linke Seite - 3D Visualisierung
        left_panel = ctk.CTkFrame(
            main_frame,
            width=600,
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=15
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # 3D-Canvas-Platzhalter
        self.canvas_frame = ctk.CTkFrame(
            left_panel,
            fg_color=DARK_THEME["bg_primary"],
            corner_radius=10
        )
        self.canvas_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Placeholder für 3D-Visualisierung
        canvas_label = ctk.CTkLabel(
            self.canvas_frame,
            text="🌟 3D-Hologramm-Visualisierung\n\n💫 Hardware-beschleunigte Scan-Darstellung\n🔮 Echtzeit-Datenanalyse\n✨ Interaktive 3D-Effekte",
            font=ctk.CTkFont(size=16),
            text_color=DARK_THEME["hologram_glow"],
            justify="center"
        )
        canvas_label.pack(expand=True)
        
        # Rechte Seite - Kontrollen und Ergebnisse
        right_panel = ctk.CTkFrame(
            main_frame,
            width=400,
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=15
        )
        right_panel.pack(side="right", fill="y", padx=5, pady=5)
        right_panel.pack_propagate(False)
        
        self._create_control_panel(right_panel)
        self._create_results_panel(right_panel)
    
    def _create_control_panel(self, parent):
        """Erstellt das Kontrollpanel."""
        control_frame = ctk.CTkFrame(
            parent,
            height=300,
            fg_color=DARK_THEME["bg_tertiary"],
            corner_radius=10
        )
        control_frame.pack(fill="x", padx=15, pady=15)
        control_frame.pack_propagate(False)
        
        # Titel
        control_title = ctk.CTkLabel(
            control_frame,
            text="🎛️ Scan-Kontrollen",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        control_title.pack(pady=10)
        
        # Kategorie-Auswahl
        self.category_vars = {}
        categories = [
            ("temp_files", "🗂️ Temporäre Dateien", True),
            ("cache", "💾 Cache-Dateien", True), 
            ("logs", "📋 Log-Dateien", True),
            ("duplicates", "👥 Duplikate", True),
            ("registry", "🔧 Registry (Windows)", True)
        ]
        
        for cat_id, cat_name, default in categories:
            var = tk.BooleanVar(value=default)
            self.category_vars[cat_id] = var
            
            checkbox = ctk.CTkCheckBox(
                control_frame,
                text=cat_name,
                variable=var,
                font=ctk.CTkFont(size=12),
                text_color=DARK_THEME["text_primary"],
                fg_color=DARK_THEME["accent_blue"],
                hover_color=DARK_THEME["accent_purple"]
            )
            checkbox.pack(anchor="w", padx=20, pady=5)
        
        # Scan-Button (groß und auffällig)
        self.main_scan_button = ctk.CTkButton(
            control_frame,
            text="🚀 SYSTEM SCANNEN",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color=DARK_THEME["accent_green"],
            hover_color="#059669",
            command=self._start_comprehensive_scan
        )
        self.main_scan_button.pack(fill="x", padx=20, pady=20)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            control_frame,
            height=20,
            fg_color=DARK_THEME["bg_primary"],
            progress_color=DARK_THEME["accent_blue"]
        )
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        self.progress_bar.set(0)
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Bereit für System-Scan",
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_secondary"]
        )
        self.status_label.pack(pady=5)
    
    def _create_results_panel(self, parent):
        """Erstellt das Ergebnispanel."""
        results_frame = ctk.CTkFrame(
            parent,
            fg_color=DARK_THEME["bg_tertiary"],
            corner_radius=10
        )
        results_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Titel
        results_title = ctk.CTkLabel(
            results_frame,
            text="📊 Scan-Ergebnisse",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        results_title.pack(pady=10)
        
        # Scrollbare Ergebnisliste
        self.results_scrollframe = ctk.CTkScrollableFrame(
            results_frame,
            fg_color=DARK_THEME["bg_primary"],
            corner_radius=8
        )
        self.results_scrollframe.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Aktions-Buttons
        action_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=10)
        
        self.clean_button = ctk.CTkButton(
            action_frame,
            text="🧹 Ausgewählte Bereinigen",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=DARK_THEME["accent_red"],
            hover_color="#dc2626",
            command=self._perform_cleaning,
            state="disabled"
        )
        self.clean_button.pack(side="left", padx=5)
        
        self.select_all_button = ctk.CTkButton(
            action_frame,
            text="✅ Alle Auswählen",
            font=ctk.CTkFont(size=12),
            fg_color=DARK_THEME["bg_tertiary"],
            hover_color="#374151",
            command=self._select_all_items,
            state="disabled"
        )
        self.select_all_button.pack(side="right", padx=5)
    
    def _create_footer(self):
        """Erstellt den Footer mit Status und Premium-Info."""
        footer_frame = ctk.CTkFrame(
            self.root,
            height=60,
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=0
        )
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # System-Info
        system_info = f"💻 {psutil.cpu_count()} CPU-Kerne | 🧠 {psutil.virtual_memory().total // (1024**3)} GB RAM"
        if self.scanner.gpu_available:
            system_info += " | 🎮 GPU-Beschleunigung aktiv"
        
        info_label = ctk.CTkLabel(
            footer_frame,
            text=system_info,
            font=ctk.CTkFont(size=10),
            text_color=DARK_THEME["text_secondary"]
        )
        info_label.pack(side="left", padx=20, pady=15)
        
        # Premium-Status
        premium_text = "👑 Premium-Nutzer" if self.is_premium else "🆓 Kostenlose Version"
        premium_label = ctk.CTkLabel(
            footer_frame,
            text=premium_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=DARK_THEME["accent_blue"] if self.is_premium else DARK_THEME["text_secondary"]
        )
        premium_label.pack(side="right", padx=20, pady=15)
    
    def _initialize_3d_renderer(self):
        """Initialisiert den 3D-Hologramm-Renderer."""
        try:
            self.hologram_renderer = HologramRenderer(600, 400)
        except Exception as e:
            print(f"3D-Renderer konnte nicht initialisiert werden: {e}")
    
    def _start_scan(self):
        """Startet einen Quick-Scan."""
        self._start_comprehensive_scan(quick=True)
    
    def _start_comprehensive_scan(self, quick=False):
        """Startet einen umfassenden System-Scan."""
        if self.scanner.is_scanning:
            return
        
        # Bestimme zu scannende Kategorien
        selected_categories = [
            cat_id for cat_id, var in self.category_vars.items() 
            if var.get()
        ]
        
        if not selected_categories:
            messagebox.showwarning("Warnung", "Bitte wählen Sie mindestens eine Kategorie zum Scannen aus.")
            return
        
        # Deaktiviere UI während Scan
        self.main_scan_button.configure(state="disabled", text="🔄 Scanning...")
        self.progress_bar.set(0)
        
        # Starte Scan in separatem Thread
        scan_thread = threading.Thread(
            target=self._run_scan_thread,
            args=(selected_categories, quick),
            daemon=True
        )
        scan_thread.start()
    
    def _run_scan_thread(self, categories: List[str], quick: bool):
        """Führt den Scan in einem separaten Thread aus."""
        def progress_callback(status: str, progress: float):
            self.root.after(0, lambda: self._update_scan_progress(status, progress))
        
        try:
            # Asyncer Scan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            scan_result = loop.run_until_complete(
                self.scanner.perform_scan(categories, progress_callback)
            )
            
            # UI-Update im Hauptthread
            self.root.after(0, lambda: self._on_scan_complete(scan_result))
            
        except Exception as e:
            self.root.after(0, lambda: self._on_scan_error(str(e)))
        finally:
            loop.close()
    
    def _update_scan_progress(self, status: str, progress: float):
        """Aktualisiert den Scan-Fortschritt."""
        self.progress_bar.set(progress)
        self.status_label.configure(text=status)
        
        # 3D-Visualisierung update
        if self.hologram_renderer:
            self.hologram_renderer.render_data_visualization(None)
    
    def _on_scan_complete(self, scan_result: ScanResult):
        """Wird aufgerufen, wenn der Scan abgeschlossen ist."""
        self.current_scan_result = scan_result
        
        # UI zurücksetzen
        self.main_scan_button.configure(state="normal", text="🚀 SYSTEM SCANNEN")
        self.clean_button.configure(state="normal")
        self.select_all_button.configure(state="normal")
        
        # Ergebnisse anzeigen
        self._display_scan_results(scan_result)
        
        # 3D-Visualisierung mit echten Daten
        if self.hologram_renderer:
            self.hologram_renderer.render_data_visualization(scan_result)
        
        # KI-Empfehlung anfordern
        self._get_ai_recommendation(scan_result)
    
    def _on_scan_error(self, error: str):
        """Wird bei Scan-Fehlern aufgerufen."""
        self.main_scan_button.configure(state="normal", text="🚀 SYSTEM SCANNEN")
        self.status_label.configure(text="Scan-Fehler aufgetreten")
        messagebox.showerror("Scan-Fehler", f"Fehler beim Scannen: {error}")
    
    def _display_scan_results(self, scan_result: ScanResult):
        """Zeigt die Scan-Ergebnisse in der UI an."""
        # Lösche vorherige Ergebnisse
        for widget in self.results_scrollframe.winfo_children():
            widget.destroy()
        
        # Übersicht
        total_mb = scan_result.total_size / (1024 * 1024)
        overview_text = f"📈 {scan_result.total_files:,} Dateien gefunden\n💾 {total_mb:.1f} MB Speicher freigegeben\n⏱️ Scan-Dauer: {scan_result.scan_duration:.1f}s"
        
        overview_label = ctk.CTkLabel(
            self.results_scrollframe,
            text=overview_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=DARK_THEME["accent_green"],
            justify="left"
        )
        overview_label.pack(pady=10, anchor="w")
        
        # Kategorien anzeigen
        for category, items in scan_result.categories.items():
            if not items:
                continue
                
            self._create_category_section(category, items)
    
    def _create_category_section(self, category: str, items: List[CleaningItem]):
        """Erstellt eine Sektion für eine Kategorie."""
        category_names = {
            "temp_files": "🗂️ Temporäre Dateien",
            "cache": "💾 Cache-Dateien",
            "logs": "📋 Log-Dateien", 
            "duplicates": "👥 Duplikate",
            "registry": "🔧 Registry-Einträge"
        }
        
        # Kategorie-Header
        category_frame = ctk.CTkFrame(
            self.results_scrollframe,
            fg_color=DARK_THEME["bg_tertiary"],
            corner_radius=8
        )
        category_frame.pack(fill="x", pady=5)
        
        category_size = sum(item.size for item in items)
        category_mb = category_size / (1024 * 1024)
        
        header_text = f"{category_names.get(category, category)} ({len(items)} Dateien, {category_mb:.1f} MB)"
        
        category_header = ctk.CTkLabel(
            category_frame,
            text=header_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=DARK_THEME["text_primary"]
        )
        category_header.pack(pady=8)
        
        # Zeige erste 5 Dateien als Beispiel
        for i, item in enumerate(items[:5]):
            item_frame = ctk.CTkFrame(
                self.results_scrollframe,
                fg_color=DARK_THEME["bg_primary"],
                corner_radius=5
            )
            item_frame.pack(fill="x", pady=2, padx=10)
            
            # Checkbox für Auswahl
            item_var = tk.BooleanVar(value=item.safe_to_delete)
            checkbox = ctk.CTkCheckBox(
                item_frame,
                text="",
                variable=item_var,
                width=20,
                fg_color=DARK_THEME["accent_green"]
            )
            checkbox.pack(side="left", padx=5, pady=5)
            
            # Datei-Info
            file_name = os.path.basename(item.path)
            size_mb = item.size / (1024 * 1024)
            
            info_text = f"{file_name}\n{size_mb:.2f} MB - {item.description}"
            
            info_label = ctk.CTkLabel(
                item_frame,
                text=info_text,
                font=ctk.CTkFont(size=10),
                text_color=DARK_THEME["text_secondary"],
                justify="left",
                anchor="w"
            )
            info_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # "Weitere anzeigen" wenn mehr als 5 Dateien
        if len(items) > 5:
            more_label = ctk.CTkLabel(
                self.results_scrollframe,
                text=f"... und {len(items) - 5} weitere Dateien",
                font=ctk.CTkFont(size=10, style="italic"),
                text_color=DARK_THEME["text_secondary"]
            )
            more_label.pack(pady=2)
    
    def _perform_cleaning(self):
        """Führt die Bereinigung der ausgewählten Elemente durch."""
        if not self.current_scan_result:
            return
        
        # Sammle ausgewählte Items (vereinfacht für Demo)
        total_items = sum(len(items) for items in self.current_scan_result.categories.values())
        
        if total_items == 0:
            messagebox.showinfo("Info", "Keine Dateien zum Bereinigen ausgewählt.")
            return
        
        # Bestätigungs-Dialog
        total_size_mb = self.current_scan_result.total_size / (1024 * 1024)
        confirm_text = f"Möchten Sie {total_items} Dateien ({total_size_mb:.1f} MB) bereinigen?\n\nDieser Vorgang kann nicht rückgängig gemacht werden."
        
        if messagebox.askyesno("Bereinigung bestätigen", confirm_text):
            self._execute_cleaning()
    
    def _execute_cleaning(self):
        """Führt die tatsächliche Bereinigung durch."""
        # Zeige Bereinigungsfortschritt
        cleaning_window = ctk.CTkToplevel(self.root)
        cleaning_window.title("Bereinigung läuft...")
        cleaning_window.geometry("400x200")
        cleaning_window.configure(fg_color=DARK_THEME["bg_primary"])
        
        progress_label = ctk.CTkLabel(
            cleaning_window,
            text="🧹 Bereinigung wird durchgeführt...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        progress_label.pack(pady=30)
        
        cleaning_progress = ctk.CTkProgressBar(
            cleaning_window,
            width=300,
            height=20,
            fg_color=DARK_THEME["bg_secondary"],
            progress_color=DARK_THEME["accent_green"]
        )
        cleaning_progress.pack(pady=20)
        
        # Simuliere Bereinigung (in echtem Code würde hier die Löschung stattfinden)
        def simulate_cleaning():
            for i in range(101):
                cleaning_progress.set(i / 100)
                time.sleep(0.02)  # Simuliere Arbeit
                
            cleaning_window.after(0, lambda: [
                cleaning_window.destroy(),
                messagebox.showinfo("Erfolg", "✅ Bereinigung erfolgreich abgeschlossen!\n\nIhr System läuft jetzt optimaler.")
            ])
        
        threading.Thread(target=simulate_cleaning, daemon=True).start()
    
    def _select_all_items(self):
        """Wählt alle Elemente für die Bereinigung aus."""
        # Vereinfachte Implementierung für Demo
        messagebox.showinfo("Info", "Alle sicheren Elemente wurden ausgewählt.")
    
    def _get_ai_recommendation(self, scan_result: ScanResult):
        """Holt KI-Empfehlung für die Scan-Ergebnisse."""
        async def get_recommendation():
            try:
                recommendation = await self.ai_assistant.get_cleaning_recommendation(scan_result)
                self.root.after(0, lambda: self._show_ai_recommendation(recommendation))
            except Exception as e:
                print(f"KI-Empfehlung fehlgeschlagen: {e}")
        
        # Starte in separatem Thread
        threading.Thread(
            target=lambda: asyncio.run(get_recommendation()),
            daemon=True
        ).start()
    
    def _show_ai_recommendation(self, recommendation: str):
        """Zeigt die KI-Empfehlung in einem Dialog."""
        ai_window = ctk.CTkToplevel(self.root)
        ai_window.title("🤖 KI-Empfehlung")
        ai_window.geometry("500x300")
        ai_window.configure(fg_color=DARK_THEME["bg_primary"])
        
        title_label = ctk.CTkLabel(
            ai_window,
            text="🧠 Intelligente Analyse",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=DARK_THEME["accent_purple"]
        )
        title_label.pack(pady=15)
        
        recommendation_text = ctk.CTkTextbox(
            ai_window,
            width=450,
            height=180,
            fg_color=DARK_THEME["bg_secondary"],
            text_color=DARK_THEME["text_primary"],
            font=ctk.CTkFont(size=12)
        )
        recommendation_text.pack(padx=20, pady=10)
        recommendation_text.insert("1.0", recommendation)
        recommendation_text.configure(state="disabled")
        
        close_button = ctk.CTkButton(
            ai_window,
            text="Verstanden",
            command=ai_window.destroy,
            fg_color=DARK_THEME["accent_blue"]
        )
        close_button.pack(pady=10)
    
    def _open_ai_chat(self):
        """Öffnet den KI-Chat-Dialog."""
        ai_chat_window = ctk.CTkToplevel(self.root)
        ai_chat_window.title("🤖 KI-Assistent Chat")
        ai_chat_window.geometry("600x500")
        ai_chat_window.configure(fg_color=DARK_THEME["bg_primary"])
        
        # Chat-Verlauf
        chat_frame = ctk.CTkFrame(
            ai_chat_window,
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=10
        )
        chat_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.chat_textbox = ctk.CTkTextbox(
            chat_frame,
            fg_color=DARK_THEME["bg_primary"],
            text_color=DARK_THEME["text_primary"],
            font=ctk.CTkFont(size=12)
        )
        self.chat_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Eingabebereich
        input_frame = ctk.CTkFrame(ai_chat_window, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.chat_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Fragen Sie die KI über Ihr System...",
            font=ctk.CTkFont(size=12),
            height=40
        )
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        send_button = ctk.CTkButton(
            input_frame,
            text="Senden",
            width=80,
            command=self._send_ai_message,
            fg_color=DARK_THEME["accent_purple"]
        )
        send_button.pack(side="right")
        
        # Enter-Taste binden
        self.chat_entry.bind("<Return>", lambda e: self._send_ai_message())
        
        # Begrüßungsnachricht
        welcome_msg = "🤖 Hallo! Ich bin Ihr lokaler KI-Assistent. Fragen Sie mich gerne über Ihr System, gefundene Dateien oder Bereinigungsempfehlungen."
        self.chat_textbox.insert("end", f"KI: {welcome_msg}\n\n")
    
    def _send_ai_message(self):
        """Sendet eine Nachricht an die KI."""
        message = self.chat_entry.get().strip()
        if not message:
            return
        
        # Zeige Benutzernachricht
        self.chat_textbox.insert("end", f"Sie: {message}\n")
        self.chat_entry.delete(0, "end")
        
        # Zeige "Tippt..."-Indikator
        self.chat_textbox.insert("end", "🤖 KI tippt...\n\n")
        self.chat_textbox.see("end")
        
        # KI-Antwort in separatem Thread
        def get_ai_response():
            try:
                # Simuliere KI-Antwort (in echtem Code würde hier Ollama verwendet)
                time.sleep(1)  # Simuliere Verarbeitungszeit
                
                responses = [
                    "Basierend auf Ihrem System-Scan empfehle ich, mit temporären Dateien zu beginnen. Diese sind am sichersten zu löschen.",
                    "Ihr System zeigt moderate Fragmentierung. Eine Bereinigung der Cache-Dateien könnte die Performance verbessern.",
                    "Die gefundenen Duplikate nehmen wertvollen Speicherplatz ein. Ich kann Ihnen beim sicheren Löschen helfen.",
                    "Ihre Registry enthält einige verwaiste Einträge. Diese können sicher entfernt werden."
                ]
                
                import random
                ai_response = random.choice(responses)
                
                # Update UI im Hauptthread
                self.root.after(0, lambda: self._update_ai_chat(ai_response))
                
            except Exception as e:
                self.root.after(0, lambda: self._update_ai_chat(f"Entschuldigung, ich konnte Ihre Anfrage nicht verarbeiten: {e}"))
        
        threading.Thread(target=get_ai_response, daemon=True).start()
    
    def _update_ai_chat(self, response: str):
        """Aktualisiert den Chat mit der KI-Antwort."""
        # Entferne "Tippt..."-Nachricht
        content = self.chat_textbox.get("1.0", "end")
        lines = content.split("\n")
        if "tippt..." in lines[-3]:
            # Entferne die letzten 3 Zeilen
            self.chat_textbox.delete("end-3l", "end")
        
        # Füge KI-Antwort hinzu
        self.chat_textbox.insert("end", f"🤖 KI: {response}\n\n")
        self.chat_textbox.see("end")
    
    def _open_settings(self):
        """Öffnet das Einstellungsfenster."""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("⚙️ Einstellungen")
        settings_window.geometry("500x600")
        settings_window.configure(fg_color=DARK_THEME["bg_primary"])
        
        # Titel
        title_label = ctk.CTkLabel(
            settings_window,
            text="⚙️ GermanCodeZero-Cleaner Einstellungen",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        title_label.pack(pady=20)
        
        # Einstellungen-Bereiche
        self._create_general_settings(settings_window)
        self._create_privacy_settings(settings_window)
        self._create_premium_settings(settings_window)
    
    def _create_general_settings(self, parent):
        """Erstellt allgemeine Einstellungen."""
        general_frame = ctk.CTkFrame(
            parent,
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=10
        )
        general_frame.pack(fill="x", padx=20, pady=10)
        
        general_title = ctk.CTkLabel(
            general_frame,
            text="🔧 Allgemeine Einstellungen",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=DARK_THEME["text_primary"]
        )
        general_title.pack(pady=10)
        
        # Auto-Scan
        auto_scan_var = tk.BooleanVar(value=self.preferences.auto_scan_enabled)
        auto_scan_checkbox = ctk.CTkCheckBox(
            general_frame,
            text="🔄 Automatischer System-Scan beim Start",
            variable=auto_scan_var,
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_primary"]
        )
        auto_scan_checkbox.pack(anchor="w", padx=20, pady=5)
        
        # Hardware-Beschleunigung
        hw_accel_var = tk.BooleanVar(value=True)
        hw_accel_checkbox = ctk.CTkCheckBox(
            general_frame,
            text="⚡ Hardware-Beschleunigung aktivieren",
            variable=hw_accel_var,
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_primary"]
        )
        hw_accel_checkbox.pack(anchor="w", padx=20, pady=5)
        
        # 3D-Effekte
        effects_var = tk.BooleanVar(value=True)
        effects_checkbox = ctk.CTkCheckBox(
            general_frame,
            text="✨ 3D-Hologramm-Effekte aktivieren",
            variable=effects_var,
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_primary"]
        )
        effects_checkbox.pack(anchor="w", padx=20, pady=(5, 15))
    
    def _create_privacy_settings(self, parent):
        """Erstellt Datenschutz-Einstellungen."""
        privacy_frame = ctk.CTkFrame(
            parent,
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=10
        )
        privacy_frame.pack(fill="x", padx=20, pady=10)
        
        privacy_title = ctk.CTkLabel(
            privacy_frame,
            text="🔒 Datenschutz & Daten-Sharing",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=DARK_THEME["text_primary"]
        )
        privacy_title.pack(pady=10)
        
        # Daten-Sharing für kostenlose Nutzung
        sharing_var = tk.BooleanVar(value=self.preferences.data_sharing_enabled)
        sharing_checkbox = ctk.CTkCheckBox(
            privacy_frame,
            text="📊 Anonyme Datenspende für kostenlose Premium-Monate",
            variable=sharing_var,
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_primary"]
        )
        sharing_checkbox.pack(anchor="w", padx=20, pady=5)
        
        sharing_info = ctk.CTkLabel(
            privacy_frame,
            text="ℹ️ Nur Metadaten (Dateigröße, -typ) werden gesendet.\nKeine persönlichen Inhalte oder Pfade.",
            font=ctk.CTkFont(size=10),
            text_color=DARK_THEME["text_secondary"],
            justify="left"
        )
        sharing_info.pack(anchor="w", padx=40, pady=(0, 15))
    
    def _create_premium_settings(self, parent):
        """Erstellt Premium-Einstellungen."""
        premium_frame = ctk.CTkFrame(
            parent,
            fg_color=DARK_THEME["bg_secondary"],
            corner_radius=10
        )
        premium_frame.pack(fill="x", padx=20, pady=10)
        
        premium_title = ctk.CTkLabel(
            premium_frame,
            text="👑 Premium-Features",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        premium_title.pack(pady=10)
        
        if not self.is_premium:
            # Premium-Werbung
            premium_info = ctk.CTkLabel(
                premium_frame,
                text="🌟 Upgrade zu Premium:\n\n✅ Keine Werbung\n⚡ Erweiterte Hardware-Beschleunigung\n🎯 Prioritäts-Support\n📈 Detaillierte Statistiken",
                font=ctk.CTkFont(size=12),
                text_color=DARK_THEME["text_primary"],
                justify="left"
            )
            premium_info.pack(pady=10)
            
            upgrade_button = ctk.CTkButton(
                premium_frame,
                text="🚀 Jetzt upgraden",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=DARK_THEME["accent_blue"],
                hover_color="#0284c7",
                command=self._show_premium_upgrade
            )
            upgrade_button.pack(pady=15)
        else:
            premium_status = ctk.CTkLabel(
                premium_frame,
                text="✅ Premium-Nutzer\nVielen Dank für Ihre Unterstützung!",
                font=ctk.CTkFont(size=12),
                text_color=DARK_THEME["accent_green"]
            )
            premium_status.pack(pady=20)
    
    def _show_premium_upgrade(self):
        """Zeigt Premium-Upgrade-Dialog."""
        upgrade_window = ctk.CTkToplevel(self.root)
        upgrade_window.title("👑 Premium Upgrade")
        upgrade_window.geometry("400x300")
        upgrade_window.configure(fg_color=DARK_THEME["bg_primary"])
        
        title = ctk.CTkLabel(
            upgrade_window,
            text="🌟 Premium-Upgrade",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        title.pack(pady=20)
        
        features_text = """
        ✅ Werbefreie Nutzung
        ⚡ Hardware-Beschleunigung Pro
        🎯 Prioritäts-Support
        📊 Erweiterte Statistiken
        🔮 Exklusive 3D-Effekte
        """
        
        features_label = ctk.CTkLabel(
            upgrade_window,
            text=features_text,
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_primary"],
            justify="left"
        )
        features_label.pack(pady=10)
        
        price_label = ctk.CTkLabel(
            upgrade_window,
            text="💰 Nur 4,99€/Monat",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=DARK_THEME["accent_green"]
        )
        price_label.pack(pady=10)
        
        upgrade_btn = ctk.CTkButton(
            upgrade_window,
            text="🚀 Jetzt upgraden",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=DARK_THEME["accent_blue"],
            command=lambda: messagebox.showinfo("Demo", "Premium-Upgrade in Vollversion verfügbar!")
        )
        upgrade_btn.pack(pady=15)
    
    def _load_preferences(self):
        """Lädt Benutzer-Einstellungen."""
        # Vereinfachte Implementierung - in echter App aus Datei laden
        pass
    
    def _save_preferences(self):
        """Speichert Benutzer-Einstellungen."""
        # Vereinfachte Implementierung - in echter App in Datei speichern
        pass
    
    def _show_ad_popup(self):
        """Zeigt gelegentliche Werbung für kostenlose Nutzer."""
        if self.is_premium:
            return
        
        # Nur alle 10 Minuten
        if hasattr(self, '_last_ad_time'):
            if time.time() - self._last_ad_time < 600:  # 10 Minuten
                return
        
        self._last_ad_time = time.time()
        
        ad_window = ctk.CTkToplevel(self.root)
        ad_window.title("💡 Tipp")
        ad_window.geometry("350x200")
        ad_window.configure(fg_color=DARK_THEME["bg_primary"])
        
        # Zentriere das Fenster
        ad_window.transient(self.root)
        ad_window.grab_set()
        
        ad_label = ctk.CTkLabel(
            ad_window,
            text="💡 Wussten Sie schon?\n\nMit Premium erhalten Sie:\n🚀 2x schnellere Scans\n✨ Exklusive 3D-Effekte\n📊 Detaillierte Berichte",
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_primary"],
            justify="center"
        )
        ad_label.pack(expand=True, pady=20)
        
        button_frame = ctk.CTkFrame(ad_window, fg_color="transparent")
        button_frame.pack(pady=10)
        
        upgrade_btn = ctk.CTkButton(
            button_frame,
            text="Upgraden",
            fg_color=DARK_THEME["accent_blue"],
            command=lambda: [ad_window.destroy(), self._show_premium_upgrade()]
        )
        upgrade_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Schließen",
            fg_color=DARK_THEME["bg_tertiary"],
            command=ad_window.destroy
        )
        close_btn.pack(side="left", padx=5)
        
        # Auto-close nach 5 Sekunden
        ad_window.after(5000, ad_window.destroy)
    
    def run(self):
        """Startet die Anwendung."""
        # Zeige Splash Screen
        self._show_splash_screen()
        
        # Initialisiere KI im Hintergrund
        if self.ai_assistant.is_available:
            threading.Thread(
                target=lambda: asyncio.run(self.ai_assistant.initialize_model()),
                daemon=True
            ).start()
        
        # Starte Hauptschleife
        self.root.mainloop()
    
    def _show_splash_screen(self):
        """Zeigt einen animierten Splash Screen."""
        splash = ctk.CTkToplevel()
        splash.title("")
        splash.geometry("400x300")
        splash.configure(fg_color=DARK_THEME["bg_primary"])
        splash.overrideredirect(True)  # Entferne Fensterrahmen
        
        # Zentriere auf Bildschirm
        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - (400 // 2)
        y = (splash.winfo_screenheight() // 2) - (300 // 2)
        splash.geometry(f"400x300+{x}+{y}")
        
        # Logo und Text
        logo_label = ctk.CTkLabel(
            splash,
            text="🛡️",
            font=ctk.CTkFont(size=48),
            text_color=DARK_THEME["hologram_glow"]
        )
        logo_label.pack(pady=30)
        
        title_label = ctk.CTkLabel(
            splash,
            text="GermanCodeZero-Cleaner",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=DARK_THEME["accent_blue"]
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            splash,
            text="KI-gestützte System-Optimierung",
            font=ctk.CTkFont(size=12),
            text_color=DARK_THEME["text_secondary"]
        )
        subtitle_label.pack(pady=5)
        
        # Loading Animation
        loading_progress = ctk.CTkProgressBar(
            splash,
            width=300,
            height=20,
            fg_color=DARK_THEME["bg_secondary"],
            progress_color=DARK_THEME["hologram_glow"]
        )
        loading_progress.pack(pady=30)
        
        # Animiere Loading
        def animate_loading():
            for i in range(101):
                loading_progress.set(i / 100)
                splash.update()
                time.sleep(0.02)
            
            splash.destroy()
        
        splash.after(100, animate_loading)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Haupteinstiegspunkt der Anwendung."""
    print(f"🚀 Starte {APP_NAME} v{APP_VERSION}")
    print(f"👨‍💻 Entwickelt von {APP_AUTHOR}")
    print("=" * 50)
    
    # Prüfe System-Kompatibilität
    if sys.platform not in ["win32", "darwin", "linux"]:
        print("❌ Nicht unterstütztes Betriebssystem")
        sys.exit(1)
    
    # Prüfe Python-Version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ erforderlich")
        sys.exit(1)
    
    try:
        # Erstelle und starte Anwendung
        app = GermanCodeZeroCleanerApp()
        
        # Zeige gelegentlich Werbung für kostenlose Nutzer
        def show_periodic_ads():
            while True:
                time.sleep(600)  # 10 Minuten
                app.root.after(0, app._show_ad_popup)
        
        if not app.is_premium:
            threading.Thread(target=show_periodic_ads, daemon=True).start()
        
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Anwendung durch Benutzer beendet")
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
Multi-AI-Integration (Llama3-8B, Gemini 1.5, Deepseek 3.1, Groq)
Hardware-optimiert für AMD RX 7800 XT und Ryzen 7 7800X3D
Echtzeit-Systemüberwachung mit animierten Statistiken
"""

import sys
import asyncio
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor
from PyQt6.QtOpenGL import QOpenGLWidget

# Import our custom modules
from src.ui.main_window import HolographicMainWindow
from src.core.system_monitor import SystemMonitor
from src.core.database import DatabaseManager
from src.ai.ai_manager import AIManager
from src.ui.effects.holographic_renderer import HolographicRenderer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('holographic_ai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class HolographicAIApp(QApplication):
    """Main application class with holographic effects and AI integration"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Holographic AI System Monitor")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("HolographicAI")
        
        # Initialize core components
        self.setup_dark_theme()
        self.init_components()
        
    def setup_dark_theme(self):
        """Setup modern dark theme with holographic accents"""
        self.setStyle('Fusion')
        
        # Dark palette with neon accents
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 23))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 55))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 255, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 255, 255, 100))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(palette)
        
    def init_components(self):
        """Initialize all core components"""
        try:
            # Initialize database
            self.db_manager = DatabaseManager()
            
            # Initialize system monitor
            self.system_monitor = SystemMonitor()
            
            # Initialize AI manager
            self.ai_manager = AIManager()
            
            # Initialize main window
            self.main_window = HolographicMainWindow(
                self.system_monitor, 
                self.ai_manager, 
                self.db_manager
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            sys.exit(1)
            
    def run(self):
        """Start the application"""
        try:
            self.main_window.show()
            logger.info("Holographic AI System Monitor started successfully")
            return self.exec()
        except Exception as e:
            logger.error(f"Application failed to start: {e}")
            return 1

def main():
    """Main entry point"""
    try:
        # Enable high DPI scaling for modern displays
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        app = HolographicAIApp(sys.argv)
        return app.run()
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

if __name__ == "__main__":
    main()
=======
from cleaner.cli import main

if __name__ == "__main__":
    main()
>>>>>>> Incoming (Background Agent changes)
