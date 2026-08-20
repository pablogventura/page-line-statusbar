"""Document helpers for LibreOffice Writer (cm <-> UNO units)."""

from __future__ import annotations

from typing import Optional


def cm_to_hmm(cm: float) -> int:
    """Convert centimeters to 1/100 mm (LibreOffice internal)."""
    return int(round(float(cm) * 1000))


def pt_to_hmm(points: float) -> int:
    """Convert typographic points to 1/100 mm."""
    return int(round(float(points) * 35.2777778))


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


def get_page_style(doc):
    family = doc.getStyleFamilies().getByName("PageStyles")
    # Prefer the style used by the current cursor page if possible.
    try:
        controller = doc.getCurrentController()
        view_cursor = controller.getViewCursor()
        name = view_cursor.getPropertyValue("PageStyleName")
        if name and family.hasByName(name):
            return family.getByName(name)
    except Exception:
        pass
    if family.hasByName("Default Page Style"):
        return family.getByName("Default Page Style")
    if family.hasByName("Standard"):
        return family.getByName("Standard")
    names = family.getElementNames()
    return family.getByName(names[0])


def select_all(doc) -> None:
    text = doc.getText()
    cursor = text.createTextCursor()
    cursor.gotoStart(False)
    cursor.gotoEnd(True)
    doc.getCurrentController().select(cursor)


def apply_font_to_selection(doc, font_name: str, size_pt: float) -> None:
    selection = doc.getCurrentSelection()
    if selection is None:
        return
    count = selection.getCount()
    for index in range(count):
        rang = selection.getByIndex(index)
        cursor = rang.getText().createTextCursorByRange(rang)
        cursor.setPropertyValue("CharFontName", font_name)
        cursor.setPropertyValue("CharFontNameAsian", font_name)
        cursor.setPropertyValue("CharFontNameComplex", font_name)
        cursor.setPropertyValue("CharHeight", float(size_pt))
        cursor.setPropertyValue("CharHeightAsian", float(size_pt))
        cursor.setPropertyValue("CharHeightComplex", float(size_pt))
        cursor.setPropertyValue("CharColor", 0)
        cursor.setPropertyValue("CharBackColor", -1)


def apply_paragraph_spacing(doc, exact_pt: Optional[float], single_or_15: Optional[float] = None) -> None:
    from com.sun.star.style import LineSpacing

    # LineSpacingMode: PROP=0, MINIMUM=1, LEADING=2, SINGLE=3; FIX=4 in LO.
    selection = doc.getCurrentSelection()
    if selection is None:
        return
    for index in range(selection.getCount()):
        rang = selection.getByIndex(index)
        cursor = rang.getText().createTextCursorByRange(rang)
        spacing = LineSpacing()
        if exact_pt is not None:
            spacing.Mode = 4
            spacing.Height = pt_to_hmm(exact_pt)
        elif single_or_15 is not None:
            spacing.Mode = 0
            spacing.Height = int(round(single_or_15 * 100))
        else:
            continue
        cursor.setPropertyValue("ParaLineSpacing", spacing)


def set_page_geometry(
    doc,
    width_cm: float,
    height_cm: float,
    top_cm: float,
    bottom_cm: float,
    left_cm: float,
    right_cm: float,
    mirror: bool = False,
) -> None:
    style = get_page_style(doc)
    style.setPropertyValue("Width", cm_to_hmm(width_cm))
    style.setPropertyValue("Height", cm_to_hmm(height_cm))
    style.setPropertyValue("IsLandscape", False)
    style.setPropertyValue("TopMargin", cm_to_hmm(top_cm))
    style.setPropertyValue("BottomMargin", cm_to_hmm(bottom_cm))
    style.setPropertyValue("LeftMargin", cm_to_hmm(left_cm))
    style.setPropertyValue("RightMargin", cm_to_hmm(right_cm))
    try:
        # 0=LeftRight, 1=Mirrored
        style.setPropertyValue("PageStyleLayout", 1 if mirror else 0)
    except Exception:
        pass


def clear_headers_footers(doc) -> None:
    style = get_page_style(doc)
    for prop in (
        "HeaderIsOn",
        "FooterIsOn",
        "HeaderIsShared",
        "FooterIsShared",
    ):
        try:
            if prop.endswith("IsOn"):
                style.setPropertyValue(prop, False)
        except Exception:
            pass


def goto_start(doc) -> None:
    text = doc.getText()
    cursor = text.createTextCursor()
    cursor.gotoStart(False)
    doc.getCurrentController().select(cursor)


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


def find_next(doc, needle: str) -> bool:
    if not needle:
        return False
    search = doc.createSearchDescriptor()
    search.setSearchString(needle)
    search.SearchCaseSensitive = False
    search.SearchWords = False
    found = doc.findFirst(search)
    if found is None:
        return False
    doc.getCurrentController().select(found)
    return True


def dispatch_uno(frame, command: str) -> None:
    if frame is None:
        return
    try:
        ctx = frame
        # Prefer desktop dispatcher via controller frame
        controller = frame.getController()
        dispatcher = frame.queryDispatch(
            _url(command),
            "_self",
            0,
        )
        if dispatcher is not None:
            dispatcher.dispatch(_url(command), ())
    except Exception:
        pass


def _url(complete: str):
    from com.sun.star.util import URL

    url = URL()
    url.Complete = complete
    return url
