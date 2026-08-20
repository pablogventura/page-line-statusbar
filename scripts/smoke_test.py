#!/usr/bin/env python3
"""Unit checks that do not require LibreOffice."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "oxt" / "pythonpath"))

from foja.numbers import convertir_cifra_texto
from foja.page_line_calc import format_page_line


def main() -> int:
    assert format_page_line(3, 12) == "Pag 3 - Lin 12"
    assert convertir_cifra_texto("125") != ""
    assert "veinte" in convertir_cifra_texto("25") or "veinti" in convertir_cifra_texto("25")
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
