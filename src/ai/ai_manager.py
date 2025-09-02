"""
AI Manager für GermanCodeZero-Cleaner
=====================================

Zentrale KI-Verwaltung mit lokalen und Cloud-basierten Modellen.
"""

import os
import sys
import asyncio
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import hashlib
from pathlib import Path

# Lokale LLM-Integration
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Alternative: llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

# Claude API Integration
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from config import AI_CONFIG, get_app_data_dir
from ..core.database import get_database


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class AIProvider(Enum):
    """Verfügbare AI-Provider."""
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    CLAUDE = "claude"
    OPENAI = "openai"
    LOCAL_ONLY = "local_only"


@dataclass
class AIModel:
    """AI-Modell-Definition."""
    name: str
    provider: AIProvider
    size_gb: float
    context_length: int
    capabilities: List[str]
    language_support: List[str]
    hardware_requirements: Dict[str, Any]
    is_available: bool = False
    is_loaded: bool = False


@dataclass
class AIRequest:
    """AI-Anfrage."""
    request_id: str
    timestamp: datetime
    prompt: str
    context: Optional[str] = None
    max_tokens: int = 500
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class AIResponse:
    """AI-Antwort."""
    request_id: str
    timestamp: datetime
    response_text: str
    model_used: str
    tokens_used: int
    response_time_ms: float
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = None


# ============================================================================
# AI MANAGER
# ============================================================================

class AIManager:
    """Hauptklasse für AI-Management."""
    
    def __init__(self):
        """Initialisiert den AI Manager."""
        self.logger = logging.getLogger(__name__)
        
        # Modell-Registry
        self.available_models: Dict[str, AIModel] = {}
        self.active_model: Optional[AIModel] = None
        
        # Provider
        self.ollama_client = None
        self.llama_cpp_model = None
        self.claude_client = None
        
        # Cache
        self.response_cache: Dict[str, AIResponse] = {}
        self.max_cache_size = 1000
        
        # Statistiken
        self.total_requests = 0
        self.total_tokens = 0
        self.average_response_time = 0.0
        
        # Threading
        self.executor = threading.ThreadPoolExecutor(max_workers=2)
        
        # Initialisierung
        self._initialize_providers()
        self._discover_models()
    
    def _initialize_providers(self):
        """Initialisiert verfügbare AI-Provider."""
        # Ollama
        if OLLAMA_AVAILABLE:
            try:
                self.ollama_client = ollama.Client()
                self.logger.info("Ollama provider initialized")
            except Exception as e:
                self.logger.warning(f"Ollama initialization failed: {e}")
        
        # Llama.cpp
        if LLAMA_CPP_AVAILABLE:
            try:
                model_path = self._get_local_model_path()
                if model_path and model_path.exists():
                    self.llama_cpp_model = Llama(
                        model_path=str(model_path),
                        n_ctx=AI_CONFIG["max_context_length"],
                        n_threads=os.cpu_count() // 2
                    )
                    self.logger.info("Llama.cpp provider initialized")
            except Exception as e:
                self.logger.warning(f"Llama.cpp initialization failed: {e}")
        
        # Claude API
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.claude_client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                self.logger.info("Claude provider initialized")
            except Exception as e:
                self.logger.warning(f"Claude initialization failed: {e}")
    
    def _get_local_model_path(self) -> Optional[Path]:
        """Gibt Pfad zu lokalem Modell zurück."""
        models_dir = get_app_data_dir() / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Suche nach .gguf Dateien
        for model_file in models_dir.glob("*.gguf"):
            return model_file
        
        return None
    
    def _discover_models(self):
        """Entdeckt verfügbare Modelle."""
        # Vordefinierte Modelle
        models = [
            AIModel(
                name="llama2:7b",
                provider=AIProvider.OLLAMA,
                size_gb=3.8,
                context_length=4096,
                capabilities=["text_generation", "summarization", "explanation"],
                language_support=["de", "en", "es", "fr"],
                hardware_requirements={"ram_gb": 8, "vram_gb": 0}
            ),
            AIModel(
                name="mistral:7b",
                provider=AIProvider.OLLAMA,
                size_gb=4.1,
                context_length=8192,
                capabilities=["text_generation", "code", "analysis"],
                language_support=["de", "en"],
                hardware_requirements={"ram_gb": 8, "vram_gb": 0}
            ),
            AIModel(
                name="tinyllama:1.1b",
                provider=AIProvider.OLLAMA,
                size_gb=0.6,
                context_length=2048,
                capabilities=["text_generation", "simple_tasks"],
                language_support=["de", "en"],
                hardware_requirements={"ram_gb": 2, "vram_gb": 0}
            ),
            AIModel(
                name="claude-3-opus",
                provider=AIProvider.CLAUDE,
                size_gb=0,  # Cloud-basiert
                context_length=200000,
                capabilities=["text_generation", "code", "analysis", "vision"],
                language_support=["de", "en", "es", "fr", "it", "pt", "ru", "ja", "zh"],
                hardware_requirements={"ram_gb": 0, "vram_gb": 0}
            )
        ]
        
        for model in models:
            self.available_models[model.name] = model
            model.is_available = self._check_model_availability(model)
        
        # Entdecke Ollama-Modelle
        if self.ollama_client:
            try:
                installed_models = self.ollama_client.list()
                for model_info in installed_models.get("models", []):
                    name = model_info["name"]
                    if name not in self.available_models:
                        self.available_models[name] = AIModel(
                            name=name,
                            provider=AIProvider.OLLAMA,
                            size_gb=model_info.get("size", 0) / (1024**3),
                            context_length=4096,
                            capabilities=["text_generation"],
                            language_support=["de", "en"],
                            hardware_requirements={"ram_gb": 8, "vram_gb": 0},
                            is_available=True
                        )
            except Exception as e:
                self.logger.debug(f"Failed to list Ollama models: {e}")
    
    def _check_model_availability(self, model: AIModel) -> bool:
        """Prüft ob Modell verfügbar ist."""
        if model.provider == AIProvider.OLLAMA and self.ollama_client:
            try:
                models = self.ollama_client.list()
                return any(m["name"] == model.name for m in models.get("models", []))
            except:
                return False
        
        elif model.provider == AIProvider.LLAMA_CPP and self.llama_cpp_model:
            return True
        
        elif model.provider == AIProvider.CLAUDE and self.claude_client:
            return True
        
        return False
    
    # ========================================================================
    # MODEL MANAGEMENT
    # ========================================================================
    
    async def load_model(self, model_name: str) -> bool:
        """Lädt ein AI-Modell."""
        if model_name not in self.available_models:
            self.logger.error(f"Model {model_name} not found")
            return False
        
        model = self.available_models[model_name]
        
        if not model.is_available:
            # Versuche Modell zu installieren
            if not await self.install_model(model_name):
                return False
        
        self.active_model = model
        model.is_loaded = True
        
        self.logger.info(f"Loaded model: {model_name}")
        return True
    
    async def install_model(self, model_name: str) -> bool:
        """Installiert ein AI-Modell."""
        if model_name not in self.available_models:
            return False
        
        model = self.available_models[model_name]
        
        if model.provider == AIProvider.OLLAMA and self.ollama_client:
            try:
                self.logger.info(f"Installing model {model_name}...")
                await self.ollama_client.pull(model_name)
                model.is_available = True
                return True
            except Exception as e:
                self.logger.error(f"Failed to install model: {e}")
                return False
        
        return False
    
    def unload_model(self):
        """Entlädt das aktuelle Modell."""
        if self.active_model:
            self.active_model.is_loaded = False
            self.active_model = None
    
    # ========================================================================
    # INFERENCE
    # ========================================================================
    
    async def generate(self, prompt: str, context: Optional[str] = None,
                       max_tokens: int = 500, temperature: float = 0.7,
                       system_prompt: Optional[str] = None) -> AIResponse:
        """Generiert eine AI-Antwort."""
        # Erstelle Request
        request = AIRequest(
            request_id=self._generate_request_id(prompt),
            timestamp=datetime.now(),
            prompt=prompt,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt
        )
        
        # Cache-Check
        cache_key = self._get_cache_key(request)
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            self.logger.debug(f"Returning cached response for request {request.request_id}")
            return cached
        
        # Wähle Modell
        if not self.active_model:
            # Lade Fallback-Modell
            await self.load_model(AI_CONFIG["fallback_model"])
        
        if not self.active_model:
            return self._create_fallback_response(request)
        
        # Generiere Antwort
        start_time = datetime.now()
        
        try:
            if self.active_model.provider == AIProvider.OLLAMA:
                response_text = await self._generate_ollama(request)
            elif self.active_model.provider == AIProvider.LLAMA_CPP:
                response_text = await self._generate_llama_cpp(request)
            elif self.active_model.provider == AIProvider.CLAUDE:
                response_text = await self._generate_claude(request)
            else:
                response_text = self._generate_fallback(request)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            response = AIResponse(
                request_id=request.request_id,
                timestamp=datetime.now(),
                response_text=response_text,
                model_used=self.active_model.name,
                tokens_used=len(response_text.split()),  # Vereinfacht
                response_time_ms=response_time,
                confidence_score=0.8
            )
            
            # Cache speichern
            self.response_cache[cache_key] = response
            self._cleanup_cache()
            
            # Statistiken aktualisieren
            self.total_requests += 1
            self.total_tokens += response.tokens_used
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
            
            # In Datenbank speichern
            self._save_to_database(request, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return self._create_error_response(request, str(e))
    
    async def _generate_ollama(self, request: AIRequest) -> str:
        """Generiert mit Ollama."""
        if not self.ollama_client:
            raise RuntimeError("Ollama not available")
        
        messages = []
        
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        if request.context:
            messages.append({"role": "user", "content": f"Kontext: {request.context}"})
        
        messages.append({"role": "user", "content": request.prompt})
        
        response = await self.ollama_client.chat(
            model=self.active_model.name,
            messages=messages,
            options={
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        )
        
        return response["message"]["content"]
    
    async def _generate_llama_cpp(self, request: AIRequest) -> str:
        """Generiert mit Llama.cpp."""
        if not self.llama_cpp_model:
            raise RuntimeError("Llama.cpp not available")
        
        # Erstelle Prompt
        full_prompt = ""
        
        if request.system_prompt:
            full_prompt += f"System: {request.system_prompt}\n\n"
        
        if request.context:
            full_prompt += f"Kontext: {request.context}\n\n"
        
        full_prompt += f"Benutzer: {request.prompt}\n\nAssistent:"
        
        # Generiere
        output = self.llama_cpp_model(
            full_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            echo=False
        )
        
        return output["choices"][0]["text"].strip()
    
    async def _generate_claude(self, request: AIRequest) -> str:
        """Generiert mit Claude."""
        if not self.claude_client:
            raise RuntimeError("Claude not available")
        
        messages = []
        
        if request.context:
            messages.append({
                "role": "user",
                "content": f"Kontext: {request.context}\n\n{request.prompt}"
            })
        else:
            messages.append({
                "role": "user",
                "content": request.prompt
            })
        
        response = self.claude_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=request.system_prompt or AI_CONFIG["system_prompts"]["general_assistant"],
            messages=messages
        )
        
        return response.content[0].text
    
    def _generate_fallback(self, request: AIRequest) -> str:
        """Fallback-Generierung ohne AI."""
        # Einfache Template-basierte Antworten
        if "was ist" in request.prompt.lower():
            return "Dies ist eine Datei oder ein Prozess auf Ihrem System. Weitere Details benötigen eine AI-Analyse."
        elif "warum" in request.prompt.lower():
            return "Die genauen Gründe können variieren. Eine AI-Analyse würde detailliertere Informationen liefern."
        elif "empfehlung" in request.prompt.lower():
            return "Basierend auf den Daten empfehle ich eine vorsichtige Bereinigung. Starten Sie mit temporären Dateien."
        else:
            return "Für eine detaillierte Analyse wird eine AI-Verbindung benötigt."
    
    # ========================================================================
    # SPECIALIZED FUNCTIONS
    # ========================================================================
    
    async def explain_file(self, file_path: str, file_size: int, 
                          file_type: str, category: str) -> str:
        """Erklärt eine Datei."""
        prompt = f"""
        Erkläre diese Datei kurz und verständlich:
        Pfad: {file_path}
        Größe: {file_size} Bytes
        Typ: {file_type}
        Kategorie: {category}
        
        Gib eine kurze Erklärung in 1-2 Sätzen, was diese Datei ist und ob sie sicher gelöscht werden kann.
        """
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=AI_CONFIG["system_prompts"]["file_explanation"],
            max_tokens=100,
            temperature=0.3
        )
        
        return response.response_text
    
    async def get_cleaning_recommendation(self, scan_stats: Dict[str, Any]) -> str:
        """Gibt Bereinigungsempfehlung."""
        prompt = f"""
        Analysiere diese Scan-Ergebnisse und gib eine Empfehlung:
        
        Gefundene Dateien: {scan_stats.get('total_files', 0)}
        Gesamtgröße: {scan_stats.get('total_size_mb', 0):.1f} MB
        Kategorien: {', '.join(scan_stats.get('categories', []))}
        
        Temporäre Dateien: {scan_stats.get('temp_files', 0)}
        Cache-Dateien: {scan_stats.get('cache_files', 0)}
        Duplikate: {scan_stats.get('duplicates', 0)}
        
        Gib eine konkrete Empfehlung, welche Bereiche zuerst bereinigt werden sollten.
        """
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=AI_CONFIG["system_prompts"]["cleaning_recommendation"],
            max_tokens=200,
            temperature=0.5
        )
        
        return response.response_text
    
    async def chat(self, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Chat-Funktion für Benutzerinteraktion."""
        # Erstelle Kontext aus Historie
        context = ""
        if conversation_history:
            for entry in conversation_history[-5:]:  # Letzte 5 Nachrichten
                context += f"{entry['role']}: {entry['content']}\n"
        
        response = await self.generate(
            prompt=message,
            context=context,
            system_prompt=AI_CONFIG["system_prompts"]["general_assistant"],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.response_text
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _generate_request_id(self, prompt: str) -> str:
        """Generiert eindeutige Request-ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}:{prompt[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _get_cache_key(self, request: AIRequest) -> str:
        """Generiert Cache-Key für Request."""
        key_parts = [
            request.prompt[:200],
            str(request.temperature),
            str(request.max_tokens),
            request.system_prompt or ""
        ]
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _cleanup_cache(self):
        """Bereinigt Cache wenn zu groß."""
        if len(self.response_cache) > self.max_cache_size:
            # Entferne älteste Einträge
            sorted_cache = sorted(
                self.response_cache.items(),
                key=lambda x: x[1].timestamp
            )
            
            to_remove = len(self.response_cache) - self.max_cache_size + 100
            for key, _ in sorted_cache[:to_remove]:
                del self.response_cache[key]
    
    def _create_fallback_response(self, request: AIRequest) -> AIResponse:
        """Erstellt Fallback-Antwort."""
        return AIResponse(
            request_id=request.request_id,
            timestamp=datetime.now(),
            response_text=self._generate_fallback(request),
            model_used="fallback",
            tokens_used=50,
            response_time_ms=10,
            confidence_score=0.3
        )
    
    def _create_error_response(self, request: AIRequest, error: str) -> AIResponse:
        """Erstellt Fehler-Antwort."""
        return AIResponse(
            request_id=request.request_id,
            timestamp=datetime.now(),
            response_text=f"Ein Fehler ist aufgetreten: {error}",
            model_used="error",
            tokens_used=0,
            response_time_ms=0,
            confidence_score=0.0,
            metadata={"error": error}
        )
    
    def _save_to_database(self, request: AIRequest, response: AIResponse):
        """Speichert Request/Response in Datenbank."""
        try:
            db = get_database()
            
            # Vereinfachte Speicherung als AI-Erklärung
            if "file" in request.prompt.lower():
                # Extrahiere Dateipfad aus Prompt (vereinfacht)
                file_pattern = request.prompt[:50]
                db.save_ai_explanation(
                    file_pattern=file_pattern,
                    explanation=response.response_text,
                    category="general",
                    safety_score=response.confidence_score
                )
        except Exception as e:
            self.logger.debug(f"Failed to save to database: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt AI-Nutzungsstatistiken zurück."""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "average_response_time_ms": self.average_response_time,
            "cache_size": len(self.response_cache),
            "active_model": self.active_model.name if self.active_model else None,
            "available_models": list(self.available_models.keys())
        }
    
    def cleanup(self):
        """Bereinigt Ressourcen."""
        self.unload_model()
        self.executor.shutdown(wait=False)


# ============================================================================
# AI MANAGER SINGLETON
# ============================================================================

_ai_manager_instance: Optional[AIManager] = None
_ai_manager_lock = threading.Lock()


def get_ai_manager() -> AIManager:
    """Gibt die Singleton AI-Manager-Instanz zurück."""
    global _ai_manager_instance
    
    if _ai_manager_instance is None:
        with _ai_manager_lock:
            if _ai_manager_instance is None:
                _ai_manager_instance = AIManager()
    
    return _ai_manager_instance