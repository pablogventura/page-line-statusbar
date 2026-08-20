"""Action router for Foja protocol commands."""

from __future__ import annotations

from foja import cuit as cuit_mod
from foja import dialogs
from foja import formats
from foja import insert
from foja import numbers
from foja import params as params_mod
from foja import print_ops
from foja import tts
from foja import uno_doc


def run_action(ctx, frame, action: str) -> None:
    doc = uno_doc.active_document(frame)
    needs_doc = action not in {"params", "simetricas"}
    if needs_doc and doc is None:
        uno_doc.msgbox(ctx, "No hay un documento Writer abierto.", "Foja")
        return

    if action == "protocolo":
        formats.apply_foja(doc, "protocolo")
    elif action == "protocolo_rev":
        formats.apply_foja(doc, "protocolo_rev")
    elif action == "intervencion":
        formats.apply_foja(doc, "intervencion")
    elif action == "intervencion_rev":
        formats.apply_foja(doc, "intervencion_rev")
    elif action == "a4":
        formats.apply_other(doc, "a4")
    elif action == "legal":
        formats.apply_other(doc, "legal")
    elif action == "boleto_a4":
        formats.apply_other(doc, "boleto_a4")
    elif action == "boleto_legal":
        formats.apply_other(doc, "boleto_legal")
    elif action == "simetricas":
        state = formats.toggle_simetricas()
        uno_doc.msgbox(
            ctx,
            "Paginas simetricas: " + ("activadas" if state else "desactivadas"),
            "Foja",
        )
    elif action == "entrelinear":
        formats.entrelinear(doc)
    elif action == "copia_simple":
        insert.insert_copia_simple(doc, ctx)
    elif action == "nro_letras":
        numbers.number_selection_to_words(doc)
    elif action == "cuit":
        result = dialogs.ask_cuit(ctx)
        if result is None:
            return
        doc_num, masculino = result
        value = cuit_mod.genera_clave(int(doc_num), masculino)
        cuit_mod.insert_cuit(doc, value)
    elif action == "params":
        current = params_mod.load_params()
        updated = dialogs.ask_params(ctx, current)
        if updated is not None:
            params_mod.save_params(updated)
            uno_doc.msgbox(ctx, "Parametros guardados.", "Foja")
    elif action == "buscar_comodin":
        p = params_mod.load_params()
        found = uno_doc.find_next(doc, p.get("comodin") or "*")
        if not found:
            uno_doc.msgbox(ctx, "No se encontro el comodin.", "Foja")
    elif action == "preview":
        print_ops.preview(frame)
    elif action == "print_current":
        print_ops.print_current(frame)
    elif action == "print_all":
        print_ops.print_all(frame)
    elif action == "print_odd":
        print_ops.print_odd_even(doc, frame, odd=True)
    elif action == "print_even":
        print_ops.print_odd_even(doc, frame, odd=False)
    elif action == "leer":
        err = tts.speak(tts.text_for_read(doc))
        if err:
            uno_doc.msgbox(ctx, err, "Foja")
    else:
        uno_doc.msgbox(ctx, f"Accion no implementada: {action}", "Foja")
