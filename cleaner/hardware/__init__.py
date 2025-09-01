"""Subpackage für hardware-spezifische Reinigungsmodule"""

from importlib import import_module

def run_all_cleaners():
    """Lädt dynamisch alle Module im Package und ruft deren clean() auf."""
    from pathlib import Path, PurePath
    for file in Path(__file__).parent.glob("*.py"):
        if file.stem.startswith("__"):
            continue
        mod = import_module(f"cleaner.hardware.{file.stem}")
        if hasattr(mod, "clean"):
            mod.clean()