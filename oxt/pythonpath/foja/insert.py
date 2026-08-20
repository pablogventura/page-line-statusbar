"""Copia simple watermark."""

from __future__ import annotations

from foja import params as params_mod
from foja import uno_doc


def insert_copia_simple(doc, ctx) -> None:
    p = params_mod.load_params()
    text = p.get("texto_copia_simple") or "Es Copia Simple"
    font = p.get("font_copia_simple") or "Liberation Serif"
    size = float(p.get("size_copia_simple") or 72)

    # Remove previous Foja watermarks from draw page
    _remove_foja_watermarks(doc)

    try:
        draw_page = doc.getDrawPage()
        shape = doc.createInstance("com.sun.star.drawing.TextShape")
        draw_page.add(shape)
        shape.setString(text)
        shape.setPropertyValue("CharFontName", font)
        shape.setPropertyValue("CharHeight", size)
        shape.setPropertyValue("CharColor", 0xC0C0C0)
        shape.setPropertyValue("RotateAngle", 31500)  # 1/100 degree
        # Center-ish on page
        style = uno_doc.get_page_style(doc)
        width = int(style.getPropertyValue("Width"))
        height = int(style.getPropertyValue("Height"))
        shape_w = int(width * 0.7)
        shape_h = int(height * 0.15)
        shape.setSize(_size(shape_w, shape_h))
        shape.setPosition(_point(int((width - shape_w) / 2), int((height - shape_h) / 2)))
        shape.setName("FojaWaterMark")
        shape.setPropertyValue("AnchorType", 1)  # AT_PAGE-ish; may vary
    except Exception:
        # Fallback: insert gray text at document start
        cursor = doc.getText().createTextCursor()
        cursor.gotoStart(False)
        cursor.setString(text + "\n")
        cursor.goLeft(len(text) + 1, True)
        cursor.setPropertyValue("CharColor", 0xC0C0C0)
        cursor.setPropertyValue("CharHeight", size)
        cursor.setPropertyValue("CharFontName", font)

    uno_doc.goto_start(doc)
    uno_doc.find_next(doc, p.get("comodin") or "*")


def _remove_foja_watermarks(doc) -> None:
    try:
        draw_page = doc.getDrawPage()
        for index in range(draw_page.getCount() - 1, -1, -1):
            shape = draw_page.getByIndex(index)
            try:
                name = shape.getName()
            except Exception:
                name = ""
            if name.startswith("FojaWaterMark") or name.startswith("PowerPlusWaterMark"):
                draw_page.remove(shape)
    except Exception:
        pass


def _size(width, height):
    from com.sun.star.awt import Size

    return Size(width, height)


def _point(x, y):
    from com.sun.star.awt import Point

    return Point(x, y)
