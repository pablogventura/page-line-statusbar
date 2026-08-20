"""Simple UNO dialogs for CUIT and parameters."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def ask_cuit(ctx) -> Optional[Tuple[str, bool]]:
    """Return (document_number, sexo_masculino) or None if cancelled."""
    try:
        toolkit = ctx.getServiceManager().createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
    except Exception:
        toolkit = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )

    # Minimal fallback using InputBox-like message flow is awkward;
    # build a tiny dialog model.
    dialog_model = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialogModel", ctx
    )
    dialog_model.PositionX = 100
    dialog_model.PositionY = 80
    dialog_model.Width = 160
    dialog_model.Height = 90
    dialog_model.Title = "Generar CUIT"

    def add(name, service, props):
        model = dialog_model.createInstance(service)
        for key, value in props.items():
            setattr(model, key, value)
        dialog_model.insertByName(name, model)

    add(
        "lblDoc",
        "com.sun.star.awt.UnoControlFixedTextModel",
        {"PositionX": 10, "PositionY": 10, "Width": 40, "Height": 12, "Label": "Documento:"},
    )
    add(
        "txtDoc",
        "com.sun.star.awt.UnoControlEditModel",
        {"PositionX": 55, "PositionY": 8, "Width": 90, "Height": 14, "Text": ""},
    )
    add(
        "chkMasc",
        "com.sun.star.awt.UnoControlCheckBoxModel",
        {
            "PositionX": 10,
            "PositionY": 30,
            "Width": 120,
            "Height": 12,
            "Label": "Masculino (20). Si no, femenino (27)",
            "State": 1,
        },
    )
    add(
        "btnOk",
        "com.sun.star.awt.UnoControlButtonModel",
        {
            "PositionX": 40,
            "PositionY": 55,
            "Width": 35,
            "Height": 14,
            "Label": "Insertar",
            "PushButtonType": 1,
            "DefaultButton": True,
        },
    )
    add(
        "btnCancel",
        "com.sun.star.awt.UnoControlButtonModel",
        {
            "PositionX": 85,
            "PositionY": 55,
            "Width": 35,
            "Height": 14,
            "Label": "Cancelar",
            "PushButtonType": 2,
        },
    )

    dialog = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialog", ctx
    )
    dialog.setModel(dialog_model)
    dialog.setVisible(False)
    dialog.createPeer(toolkit, None)
    result = dialog.execute()
    if result != 1:
        dialog.dispose()
        return None
    doc_num = dialog.getControl("txtDoc").getText().strip().replace(".", "").replace(",", "")
    masculino = dialog.getControl("chkMasc").getState() == 1
    dialog.dispose()
    if not doc_num.isdigit():
        return None
    return doc_num, masculino


def ask_params(ctx, current: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Edit key numeric/string params. Returns updated dict or None."""
    toolkit = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.awt.Toolkit", ctx
    )
    dialog_model = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialogModel", ctx
    )
    dialog_model.PositionX = 60
    dialog_model.PositionY = 40
    dialog_model.Width = 220
    dialog_model.Height = 200
    dialog_model.Title = "Foja - Parametros"

    fields = [
        ("margen_tm", "Margen superior (cm)", str(current.get("margen_tm", ""))),
        ("margen_bm", "Margen inferior (cm)", str(current.get("margen_bm", ""))),
        ("margen_lm", "Margen izquierdo (cm)", str(current.get("margen_lm", ""))),
        ("margen_rm", "Margen derecho (cm)", str(current.get("margen_rm", ""))),
        ("interlineado", "Interlineado (pt)", str(current.get("interlineado", ""))),
        ("font_notarial", "Fuente protocolo", str(current.get("font_notarial", ""))),
        ("size_notarial", "Tamano protocolo", str(current.get("size_notarial", ""))),
        ("comodin", "Comodin busqueda", str(current.get("comodin", "*"))),
        ("texto_copia_simple", "Texto copia simple", str(current.get("texto_copia_simple", ""))),
    ]

    def add(name, service, props):
        model = dialog_model.createInstance(service)
        for key, value in props.items():
            setattr(model, key, value)
        dialog_model.insertByName(name, model)

    y = 8
    for key, label, value in fields:
        add(
            f"lbl_{key}",
            "com.sun.star.awt.UnoControlFixedTextModel",
            {"PositionX": 8, "PositionY": y, "Width": 70, "Height": 10, "Label": label},
        )
        add(
            f"txt_{key}",
            "com.sun.star.awt.UnoControlEditModel",
            {"PositionX": 85, "PositionY": y - 1, "Width": 120, "Height": 12, "Text": value},
        )
        y += 14

    add(
        "btnOk",
        "com.sun.star.awt.UnoControlButtonModel",
        {
            "PositionX": 70,
            "PositionY": y + 6,
            "Width": 35,
            "Height": 14,
            "Label": "Guardar",
            "PushButtonType": 1,
            "DefaultButton": True,
        },
    )
    add(
        "btnCancel",
        "com.sun.star.awt.UnoControlButtonModel",
        {
            "PositionX": 115,
            "PositionY": y + 6,
            "Width": 35,
            "Height": 14,
            "Label": "Cancelar",
            "PushButtonType": 2,
        },
    )

    dialog = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.awt.UnoControlDialog", ctx
    )
    dialog.setModel(dialog_model)
    dialog.createPeer(toolkit, None)
    if dialog.execute() != 1:
        dialog.dispose()
        return None

    updated = dict(current)
    float_keys = {"margen_tm", "margen_bm", "margen_lm", "margen_rm", "interlineado"}
    int_keys = {"size_notarial"}
    for key, _label, _value in fields:
        text = dialog.getControl(f"txt_{key}").getText().strip()
        if key in float_keys:
            try:
                updated[key] = float(text.replace(",", "."))
            except ValueError:
                pass
        elif key in int_keys:
            try:
                updated[key] = int(float(text))
            except ValueError:
                pass
        else:
            updated[key] = text
    dialog.dispose()
    return updated
