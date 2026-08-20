"""Document helpers for LibreOffice Writer."""

from __future__ import annotations

from typing import Optional


def active_document(frame) -> Optional[object]:
    if frame is None:
        return None
    try:
        controller = frame.getController()
        if controller is None:
            return None
        model = controller.getModel()
        if model is None:
            return None
        if not model.supportsService("com.sun.star.text.TextDocument"):
            return None
        return model
    except Exception:
        return None


def msgbox(ctx, message: str, title: str = "Foja") -> None:
    try:
        toolkit = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
        peer = toolkit.getDesktopWindow()
        box = toolkit.createMessageBox(peer, 1, 1, title, message)  # INFOBOX, BUTTONS_OK
        box.execute()
    except Exception:
        pass


def replace_selection_text(doc, new_text: str) -> None:
    selection = doc.getCurrentSelection()
    if selection is None or selection.getCount() < 1:
        return
    rang = selection.getByIndex(0)
    rang.setString(new_text)


def selected_text(doc) -> str:
    selection = doc.getCurrentSelection()
    if selection is None or selection.getCount() < 1:
        return ""
    return selection.getByIndex(0).getString()
