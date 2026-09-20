#!/usr/bin/env python3
"""Assert the firmware definition still matches the KiCad schematic.

`extract_matrix.py` re-derives the matrix from `alps75-zug.kicad_sch` and the
KLE layout; this compares that against the committed `keyboard.json`, the VIA
definition and the keymaps. Run it after touching the schematic, the layout or
the definition -- it is the regression test for task 1.4.

Usage:  python3 firmware/tools/check_definition.py
Exit:   0 if everything agrees, 1 with a report of the differences otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the repository
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_matrix import build  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
KB = REPO / "firmware/keyboards/alps75_zug/keyboard.json"
VIA = REPO / "firmware/via/alps75-zug.json"
KEYMAPS = [
    REPO / "firmware/keyboards/alps75_zug/keymaps/default/keymap.c",
    REPO / "firmware/keyboards/alps75_zug/keymaps/zug/keymap.c",
]

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    truth = build()
    kb = json.loads(KB.read_text())
    via = json.loads(VIA.read_text())

    # --- pins -----------------------------------------------------------------
    check(kb["matrix_pins"]["cols"] == truth["cols"],
          f'keyboard.json cols {kb["matrix_pins"]["cols"]} != schematic {truth["cols"]}')
    check(kb["matrix_pins"]["rows"] == truth["rows"],
          f'keyboard.json rows {kb["matrix_pins"]["rows"]} != schematic {truth["rows"]}')
    check(kb["diode_direction"] == "COL2ROW",
          "diode_direction must stay COL2ROW: the schematic wires col -> switch -> "
          "diode anode, cathode -> row")

    # --- layout ---------------------------------------------------------------
    layout = kb["layouts"]["LAYOUT"]["layout"]
    check(len(layout) == truth["key_count"],
          f'keyboard.json has {len(layout)} keys, schematic has {truth["key_count"]}')

    want = [(k["matrix"][0], k["matrix"][1], k["x"], k["y"], k["w"]) for k in truth["keys"]]
    got = [(e["matrix"][0], e["matrix"][1], e["x"], e["y"], e.get("w", 1)) for e in layout]
    for i, (w, g) in enumerate(zip(want, got)):
        check(w == g, f"keyboard.json layout entry {i}: {g} != expected {w}")

    # --- VIA ------------------------------------------------------------------
    check(via["matrix"] == {"rows": len(truth["rows"]), "cols": len(truth["cols"])},
          f'via matrix {via["matrix"]} != {len(truth["rows"])}x{len(truth["cols"])}')
    check(via["vendorId"].lower() == kb["usb"]["vid"].lower()
          and via["productId"].lower() == kb["usb"]["pid"].lower(),
          "VIA vendorId/productId must match keyboard.json usb.vid/pid, or VIA will "
          "not recognise the board")
    via_positions = [e for row in via["layouts"]["keymap"] for e in row if isinstance(e, str)]
    check(sorted(via_positions) == sorted(f'{r},{c}' for r, c, *_ in want),
          "VIA keymap covers different matrix positions than the schematic")

    # --- keymaps --------------------------------------------------------------
    for path in KEYMAPS:
        src = path.read_text()
        name = path.relative_to(REPO)
        for block in re.findall(r"LAYOUT\((.*?)\n    \)", src, re.S):
            codes = [c.strip() for c in block.replace("\n", " ").split(",") if c.strip()]
            check(len(codes) == truth["key_count"],
                  f"{name}: a LAYOUT block has {len(codes)} keycodes, "
                  f'expected {truth["key_count"]}')
        check("QK_BOOT" in src or "BOOTMAGIC" in src,
              f"{name}: no QK_BOOT -- the case has no BOOTSEL hole, keep a way in")

    # keyboard.json omits dynamic_keymap.layer_count because 4 is QMK's default
    # and `qmk lint --strict` rejects restating a default.
    layer_count = kb.get("dynamic_keymap", {}).get("layer_count", 4)
    for path in KEYMAPS:
        blocks = len(re.findall(r"LAYOUT\(", path.read_text()))
        check(blocks == layer_count,
              f"{path.relative_to(REPO)}: {blocks} layers defined but VIA exposes "
              f"{layer_count}")

    if failures:
        print(f"FAIL ({len(failures)} problem(s)):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f'OK: {truth["key_count"]} keys, '
          f'{len(truth["rows"])} rows x {len(truth["cols"])} cols, '
          f'cols {truth["cols"][0]}..{truth["cols"][-1]}, '
          f'rows {truth["rows"][0]}..{truth["rows"][-1]}, COL2ROW')
    print("keyboard.json, via/alps75-zug.json and both keymaps agree with the schematic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
