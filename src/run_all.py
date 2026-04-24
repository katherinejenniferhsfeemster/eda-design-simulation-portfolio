"""Run every EDA case generator in sequence."""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))

CASES = [
    "build_kicad_case",
    "build_librepcb_case",
    "build_ngspice_case",
    "build_qucs_case",
]


def main():
    t0 = time.time()
    for name in CASES:
        print(f"\n=== {name} ===")
        mod = importlib.import_module(name)
        mod.main()
    print(f"\nall done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
