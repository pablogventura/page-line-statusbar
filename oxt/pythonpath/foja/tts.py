"""Text-to-speech backends for Foja Leer."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Optional


def speak(text: str) -> str:
    """Speak text. Returns empty string on success, or error message."""
    text = (text or "").strip()
    if not text:
        return "No hay texto para leer."
    if os.name == "nt":
        return _speak_windows(text)
    return _speak_linux(text)


def _speak_linux(text: str) -> str:
    for cmd in (
        ["spd-say", "-l", "es", text],
        ["espeak-ng", "-v", "es", text],
        ["espeak", "-v", "es", text],
    ):
        if shutil.which(cmd[0]):
            try:
                subprocess.Popen(cmd)  # noqa: S603
                return ""
            except Exception as exc:
                return str(exc)
    return (
        "No se encontro motor de voz (spd-say / espeak-ng). "
        "Instalalo para usar Leer."
    )


def _speak_windows(text: str) -> str:
    # Escape for PowerShell single-quoted string
    safe = text.replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Speak('{safe}')"
    )
    try:
        subprocess.Popen(  # noqa: S603
            ["powershell", "-NoProfile", "-Command", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return ""
    except Exception as exc:
        return str(exc)


def text_for_read(doc) -> str:
    from foja import uno_doc

    selected = uno_doc.selected_text(doc).strip()
    if selected:
        return selected
    try:
        return doc.getText().getString()
    except Exception:
        return ""
