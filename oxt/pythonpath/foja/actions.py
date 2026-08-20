"""Action router for Foja protocol commands."""

from __future__ import annotations

from foja import numbers
from foja import uno_doc


def run_action(ctx, frame, action: str) -> None:
    doc = uno_doc.active_document(frame)
    if doc is None:
        uno_doc.msgbox(ctx, "No hay un documento Writer abierto.", "Foja")
        return

    if action == "nro_letras":
        numbers.number_selection_to_words(doc)
    else:
        uno_doc.msgbox(ctx, f"Accion no implementada: {action}", "Foja")
