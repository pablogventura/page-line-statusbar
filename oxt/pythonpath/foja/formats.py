"""Sheet format operations (Protocolo / Intervencion / Otros / Entrelinear)."""

from __future__ import annotations

from foja import params as params_mod
from foja import uno_doc


def apply_foja(doc, kind: str) -> None:
    """kind: protocolo, protocolo_rev, intervencion, intervencion_rev."""
    p = params_mod.load_params()
    reverse = kind.endswith("_rev")
    notarial = kind.startswith("protocolo")
    font = p["font_notarial"] if notarial else p["font_intervencion"]
    size = p["size_notarial"] if notarial else p["size_intervencion"]
    left = p["margen_lm"] if not reverse else p["margen_rm"]
    right = p["margen_rm"] if not reverse else p["margen_lm"]

    uno_doc.select_all(doc)
    uno_doc.apply_font_to_selection(doc, font, size)
    uno_doc.set_page_geometry(
        doc,
        width_cm=21.0,
        height_cm=29.7,
        top_cm=p["margen_tm"],
        bottom_cm=p["margen_bm"],
        left_cm=left,
        right_cm=right,
        mirror=False,
    )
    uno_doc.apply_paragraph_spacing(doc, exact_pt=float(p["interlineado"]))
    uno_doc.clear_headers_footers(doc)
    try:
        doc.CharLocale = _es_locale()
    except Exception:
        pass
    uno_doc.goto_start(doc)


def apply_other(doc, kind: str) -> None:
    """kind: a4, legal, boleto_a4, boleto_legal."""
    p = params_mod.load_params()
    mirror = bool(p.get("paginas_simetricas"))
    if kind == "a4":
        font, size = p["font_a4"], p["size_a4"]
        w, h = 21.0, 29.7
        spacing_prop = 1.5
        exact = None
    elif kind == "legal":
        font, size = p["font_legal"], p["size_legal"]
        w, h = 21.59, 35.56
        spacing_prop = 1.5
        exact = None
    elif kind == "boleto_a4":
        font, size = p["font_auxiliar"], p["size_auxiliar"]
        w, h = 21.0, 29.7
        spacing_prop = 1.0
        exact = None
    else:  # boleto_legal
        font, size = p["font_auxiliar"], p["size_auxiliar"]
        w, h = 21.59, 35.56
        spacing_prop = 1.0
        exact = None

    uno_doc.select_all(doc)
    uno_doc.apply_font_to_selection(doc, font, size)
    uno_doc.set_page_geometry(
        doc,
        width_cm=w,
        height_cm=h,
        top_cm=5.2,
        bottom_cm=4.5,
        left_cm=4.8,
        right_cm=2.0,
        mirror=mirror,
    )
    if exact is not None:
        uno_doc.apply_paragraph_spacing(doc, exact_pt=exact)
    else:
        uno_doc.apply_paragraph_spacing(doc, exact_pt=None, single_or_15=spacing_prop)
    uno_doc.goto_start(doc)


def entrelinear(doc) -> None:
    p = params_mod.load_params()
    style = uno_doc.get_page_style(doc)
    left_hmm = int(style.getPropertyValue("LeftMargin"))
    left_cm = left_hmm / 1000.0
    top = float(p["margen_tm"]) - 0.4
    bottom = float(p["margen_bm"])
    if left_cm > 3:
        left, right = float(p["margen_lm"]), float(p["margen_rm"])
    else:
        left, right = float(p["margen_rm"]), float(p["margen_lm"])
    uno_doc.set_page_geometry(
        doc,
        width_cm=21.0,
        height_cm=29.7,
        top_cm=top,
        bottom_cm=bottom,
        left_cm=left,
        right_cm=right,
        mirror=False,
    )


def toggle_simetricas() -> bool:
    p = params_mod.load_params()
    p["paginas_simetricas"] = not bool(p.get("paginas_simetricas"))
    params_mod.save_params(p)
    return p["paginas_simetricas"]


def _es_locale():
    from com.sun.star.lang import Locale

    loc = Locale()
    loc.Language = "es"
    loc.Country = "AR"
    return loc
