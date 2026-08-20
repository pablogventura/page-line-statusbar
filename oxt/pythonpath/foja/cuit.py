"""CUIT generation (port of Genera_CLAVE)."""

from __future__ import annotations


def genera_clave(document_number: int, sexo_masculino: bool) -> str:
    """sexo_masculino True -> 20, False -> 27. Returns formatted CUIT."""
    aux1 = "5432765432"
    aux2 = ("20" if sexo_masculino else "27") + f"{int(document_number):08d}"

    while True:
        total = 0
        for pos in range(10):
            total += int(aux1[pos]) * int(aux2[pos])
        digito = (total * 10) % 11
        if digito == 11:
            digito = 0
        elif digito == 10:
            aux2 = "23" + aux2[2:]
            continue
        raw = aux2 + str(digito)
        # Format ##-########/#
        return f"{raw[0:2]}-{raw[2:10]}/{raw[10]}"


def insert_cuit(doc, cuit: str) -> None:
    from foja import uno_doc

    text = cuit + (" " if cuit else "")
    selection = doc.getCurrentSelection()
    if selection is None or selection.getCount() < 1:
        cursor = doc.getText().createTextCursor()
        cursor.gotoEnd(False)
        cursor.setString(text)
        return
    rang = selection.getByIndex(0)
    rang.setString(text)
