"""Default and persisted Foja parameters."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "font_notarial": "Liberation Serif",
    "size_notarial": 12,
    "font_intervencion": "Liberation Serif",
    "size_intervencion": 12,
    "font_auxiliar": "Liberation Serif",
    "size_auxiliar": 12,
    "font_a4": "Liberation Serif",
    "size_a4": 12,
    "font_legal": "Liberation Serif",
    "size_legal": 12,
    "font_copia_simple": "Liberation Serif",
    "size_copia_simple": 72,
    "texto_copia_simple": "Es Copia Simple",
    "reverso_copia_simple": True,
    "guion": True,
    "inicio_fin_documento": True,
    "comodin": "*",
    "margen_tm": 5.9,
    "margen_bm": 1.0,
    "margen_lm": 4.25,
    "margen_rm": 2.0,
    "interlineado": 25.3,
    "paginas_simetricas": False,
}


def config_path() -> str:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    folder = os.path.join(base, "foja-writer")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "params.json")


def load_params() -> Dict[str, Any]:
    path = config_path()
    data = deepcopy(DEFAULTS)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                stored = json.load(handle)
            if isinstance(stored, dict):
                data.update(stored)
        except Exception:
            pass
    return data


def save_params(params: Dict[str, Any]) -> None:
    merged = deepcopy(DEFAULTS)
    merged.update(params)
    path = config_path()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(merged, handle, indent=2, ensure_ascii=False)
