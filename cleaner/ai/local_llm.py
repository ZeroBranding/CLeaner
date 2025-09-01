"""Schnittstelle zu lokalen LLM-Instanzen (Ollama, GPT-OSS)"""

import os
from rich import print

DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deutsch-8b")
DEFAULT_GPT_OSS_MODEL = os.getenv("GPT_OSS_MODEL_PATH", "/models/gpt-oss-20b")

def ensure_models():
    """Prüft, ob Modelle verfügbar sind, und lädt sie andernfalls nach."""
    print(f"[blue]Verifiziere Ollama-Modell: {DEFAULT_OLLAMA_MODEL} …[/blue]")
    print(f"[blue]Verifiziere GPT-OSS-Modell: {DEFAULT_GPT_OSS_MODEL} …[/blue]")
    # TODO: Implementieren