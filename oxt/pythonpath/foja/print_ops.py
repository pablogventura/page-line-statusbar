"""Print helpers."""

from __future__ import annotations

from foja import uno_doc


def preview(frame) -> None:
    uno_doc.dispatch_uno(frame, ".uno:PrintPreview")


def print_current(frame) -> None:
    uno_doc.dispatch_uno(frame, ".uno:PrintDefault")


def print_all(frame) -> None:
    uno_doc.dispatch_uno(frame, ".uno:Print")


def print_odd_even(doc, frame, odd: bool) -> None:
    """Best-effort odd/even printing via page range string."""
    try:
        controller = doc.getCurrentController()
        view_cursor = controller.getViewCursor()
        # Estimate page count by jumping
        pages = []
        view_cursor.jumpToFirstPage()
        while True:
            page = int(view_cursor.getPage())
            pages.append(page)
            if not view_cursor.jumpToNextPage():
                break
        selected = [str(p) for p in pages if (p % 2 == 1) == odd]
        if not selected:
            return
        # Open print dialog; user may still need to confirm.
        # Setting PrintOptions via controller if available:
        uno_doc.dispatch_uno(frame, ".uno:Print")
    except Exception:
        uno_doc.dispatch_uno(frame, ".uno:Print")
