"""Page-relative line number helpers for LibreOffice Writer."""

from __future__ import annotations

from typing import Optional, Tuple

UNKNOWN_LABEL = "Pag - - Lin -"


def format_page_line(page: int, line: int) -> str:
    """Return status bar text for page and page-relative line."""
    return f"Pag {page} - Lin {line}"


def compute_page_and_line(document) -> Optional[Tuple[int, int]]:
    """
    Return (page, line_on_page) for the current view cursor.

    Line 1 is the first layout line of the current page. Returns None when the
    position cannot be determined safely.
    """
    try:
        controller = document.getCurrentController()
        view_cursor = controller.getViewCursor()
    except Exception:
        return None

    if view_cursor is None:
        return None

    try:
        page = int(view_cursor.getPage())
    except Exception:
        return None

    if page < 1:
        return None

    selection = None
    locked = False
    try:
        selection = document.getCurrentSelection()
        document.lockControllers()
        locked = True

        line = 1
        while view_cursor.goUp(1, False):
            try:
                current_page = int(view_cursor.getPage())
            except Exception:
                break
            if current_page != page:
                break
            line += 1

        return page, line
    except Exception:
        return None
    finally:
        if selection is not None:
            try:
                controller.select(selection)
            except Exception:
                pass
        if locked:
            try:
                document.unlockControllers()
            except Exception:
                pass


def status_text_for_document(document) -> str:
    """Build the status bar label for a Writer document."""
    result = compute_page_and_line(document)
    if result is None:
        return UNKNOWN_LABEL
    page, line = result
    return format_page_line(page, line)
