"""Number-to-words conversion (port of Convertir_Cifra_Texto)."""

from __future__ import annotations

import re


UNIDAD = {
    1: "un ",
    2: "dos ",
    3: "tres ",
    4: "cuatro ",
    5: "cinco ",
    6: "seis ",
    7: "siete ",
    8: "ocho ",
    9: "nueve ",
}
UNIDECENA = {
    1: "once ",
    2: "doce ",
    3: "trece ",
    4: "catorce ",
    5: "quince ",
    6: "dieciseis ",
    7: "diecisiete ",
    8: "dieciocho ",
    9: "diecinueve ",
}
DECENA = {
    1: "diez ",
    2: "veinte ",
    3: "treinta ",
    4: "cuarenta ",
    5: "cincuenta ",
    6: "sesenta ",
    7: "setenta ",
    8: "ochenta ",
    9: "noventa ",
}
CENTENA = {
    1: "ciento ",
    2: "doscientos ",
    3: "trescientos ",
    4: "cuatrocientos ",
    5: "quinientos ",
    6: "seiscientos ",
    7: "setecientos ",
    8: "ochocientos ",
    9: "novecientos ",
}


def _triplet(text: str, cifra1: int, cifra2: int, cifra3: int, senal: bool) -> str:
    if f"{cifra1}{cifra2}{cifra3}" == "100":
        return text + "cien "
    if cifra1:
        text += CENTENA[cifra1]
    if cifra2 == 1 and cifra3 == 0:
        return text + DECENA[1]
    if cifra2 == 1 and cifra3 != 0:
        return text + UNIDECENA[cifra3]
    if cifra2 > 1:
        text += DECENA[cifra2]
    if cifra2 == 2 and cifra3 != 0:
        text = text[:-2] + "i"
    if cifra2 > 2 and cifra3 != 0:
        text += "y "
    if cifra3 != 0:
        text += UNIDAD[cifra3]
    if cifra3 == 1 and senal:
        text = text[:-1] + "o "
    return text


def convertir_cifra_texto(valor: str) -> str:
    cleaned = valor.replace(".", "").replace(",", ".").strip()
    cleaned = re.sub(r"[^\d.]", "", cleaned)
    if not cleaned:
        return ""
    try:
        number = abs(float(cleaned))
    except ValueError:
        return ""
    if number == 0:
        return ""

    # Emulate fixed-width grouping for millions/thousands/units/cents.
    entero = int(number)
    cents = int(round((number - entero) * 1000))
    if cents >= 1000:
        entero += 1
        cents = 0

    millions = entero // 1_000_000
    rest = entero % 1_000_000
    thousands = rest // 1000
    units = rest % 1000

    text = ""
    if millions:
        c1, c2, c3 = millions // 100, (millions // 10) % 10, millions % 10
        text = _triplet(text, c1, c2, c3, False)
        text += "millon " if millions == 1 else "millones "
    if thousands:
        c1, c2, c3 = thousands // 100, (thousands // 10) % 10, thousands % 10
        text = _triplet(text, c1, c2, c3, False)
        text += "mil "
    if units:
        c1, c2, c3 = units // 100, (units // 10) % 10, units % 10
        text = _triplet(text, c1, c2, c3, True)
    if cents:
        if text:
            text += "con "
        c1, c2, c3 = cents // 100, (cents // 10) % 10, cents % 10
        text = _triplet(text, c1, c2, c3, False)

    text = text.strip()
    if not text:
        return ""
    return text[0] + text[1:]


def number_selection_to_words(doc) -> None:
    from foja import uno_doc

    raw = uno_doc.selected_text(doc).strip()
    if not raw:
        return
    # If single char selection, expand is hard in UNO; convert selection as-is.
    words = convertir_cifra_texto(raw)
    if words:
        uno_doc.replace_selection_text(doc, words)
