#!/usr/bin/env python3
"""Derive the alps75-zug key matrix from the KiCad schematic and the KLE layout.

This is the single source of truth for the firmware definition. `keyboard.json`
and the keymaps are generated from what this prints, and `check_definition.py`
re-runs it to prove they have not drifted from the schematic.

Two independent sources are read and cross-checked:

  * the schematic netlist (via `kicad-cli`) gives switch -> (row, col) and the
    GPIO behind every COL*/ROW* net;
  * `alps75-zug-layout-internal-kle.json` gives the physical geometry, and
    carries the matrix position again in each key's first legend.

They are built from the same design but by different hands, so agreeing is a
real check rather than a tautology.

Usage:  python3 firmware/tools/extract_matrix.py [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCH = REPO / "alps75-zug.kicad_sch"
KLE = REPO / "alps75-zug-layout-internal-kle.json"

NODE_RE = re.compile(
    r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)\s+\(pinfunction "([^"]*)"\)'
)
NET_RE = re.compile(
    r'\(net\s+\(code "[^"]*"\)\s+\(name "([^"]*)"\)(.*?)(?=\(net\s+\(code|\Z)', re.S
)
GPIO_RE = re.compile(r"^GPIO(\d+)_\d+$")


def _kicad_cli() -> str:
    exe = shutil.which("kicad-cli")
    if not exe:
        sys.exit("kicad-cli not found on PATH (install KiCad 7+ or `brew install kicad`)")
    return exe


def _netlist() -> str:
    """Export the schematic to a KiCad s-expression netlist and return its text."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "net.net"
        subprocess.run(
            [_kicad_cli(), "sch", "export", "netlist", "--format", "kicadsexpr",
             "-o", str(out), str(SCH)],
            check=True, capture_output=True,
        )
        return out.read_text()


def from_schematic() -> dict:
    """switch -> (row, col), plus the GPIO number driving each row and column."""
    nets = NET_RE.findall(_netlist())

    sw_col: dict[str, int] = {}     # SW ref  -> column index
    diode_row: dict[str, int] = {}  # D ref   -> row index
    sw_diode: dict[str, str] = {}   # SW ref  -> the diode on its far pin
    col_gpio: dict[int, int] = {}
    row_gpio: dict[int, int] = {}

    for name, body in nets:
        nodes = NODE_RE.findall(body)

        if m := re.fullmatch(r"COL(\d+)", name):
            idx = int(m.group(1))
            for ref, _pin, func in nodes:
                if ref.startswith("SW"):
                    sw_col[ref] = idx
                elif g := GPIO_RE.fullmatch(func):
                    col_gpio[idx] = int(g.group(1))

        elif m := re.fullmatch(r"ROW(\d+)", name):
            idx = int(m.group(1))
            for ref, _pin, func in nodes:
                if ref.startswith("D"):
                    diode_row[ref] = idx
                elif g := GPIO_RE.fullmatch(func):
                    row_gpio[idx] = int(g.group(1))

        else:
            # An unnamed net joining exactly one switch to exactly one diode is
            # the switch's far leg. Anything else is power, USB or a stray.
            switches = [r for r, _p, _f in nodes if r.startswith("SW")]
            diodes = [r for r, _p, _f in nodes if r.startswith("D")]
            if len(switches) == 1 and len(diodes) == 1:
                sw_diode[switches[0]] = diodes[0]

    matrix = {}
    for sw, col in sw_col.items():
        diode = sw_diode.get(sw)
        if diode is None:
            sys.exit(f"{sw} has no diode on its far leg")
        row = diode_row.get(diode)
        if row is None:
            sys.exit(f"{sw} -> {diode} but {diode} is not on any ROW net")
        matrix[sw] = (row, col)

    return {"matrix": matrix, "col_gpio": col_gpio, "row_gpio": row_gpio}


def from_kle() -> dict:
    """(row, col) -> physical geometry and legend, from the KLE export."""
    keys = json.loads(KLE.read_text())["keys"]
    out = {}
    for k in keys:
        row, col = (int(v) for v in k["labels"][0].split(","))
        legend = next((l for l in k["labels"][1:] if l.strip()), "")
        # Legends carry a size prefix for the wide keys ("1.5u tab"); drop it.
        legend = re.sub(r"^[\d.]+u\s+", "", legend).strip()
        if (row, col) in out:
            sys.exit(f"KLE lists matrix position {row},{col} twice")
        out[(row, col)] = {
            "x": k["x"], "y": k["y"], "w": k["width"], "h": k["height"],
            "legend": legend,
        }
    return out


def build() -> dict:
    sch = from_schematic()
    kle = from_kle()

    sch_positions = set(sch["matrix"].values())
    if len(sch_positions) != len(sch["matrix"]):
        sys.exit("two switches share a matrix position in the schematic")
    if sch_positions != set(kle):
        only_sch = sorted(sch_positions - set(kle))
        only_kle = sorted(set(kle) - sch_positions)
        sys.exit(f"schematic and KLE disagree; only in schematic: {only_sch}; "
                 f"only in KLE: {only_kle}")

    cols = sch["col_gpio"]
    rows = sch["row_gpio"]
    if sorted(cols) != list(range(len(cols))):
        sys.exit(f"column indices are not contiguous from 0: {sorted(cols)}")
    if sorted(rows) != list(range(len(rows))):
        sys.exit(f"row indices are not contiguous from 0: {sorted(rows)}")

    # Physical reading order: top to bottom, then left to right. This is the
    # order of the LAYOUT macro and of every keymap row.
    order = sorted(kle, key=lambda rc: (kle[rc]["y"], kle[rc]["x"]))

    return {
        "cols": [f"GP{cols[i]}" for i in range(len(cols))],
        "rows": [f"GP{rows[i]}" for i in range(len(rows))],
        "key_count": len(order),
        "keys": [
            {"matrix": [r, c], **{k: kle[(r, c)][k] for k in ("x", "y", "w", "legend")}}
            for (r, c) in order
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit the raw data as JSON")
    args = ap.parse_args()

    data = build()
    if args.json:
        print(json.dumps(data, indent=2))
        return

    print(f"cols ({len(data['cols'])}): {' '.join(data['cols'])}")
    print(f"rows ({len(data['rows'])}): {' '.join(data['rows'])}")
    print(f"keys: {data['key_count']}")
    by_row: dict[int, int] = {}
    for k in data["keys"]:
        by_row[k["matrix"][0]] = by_row.get(k["matrix"][0], 0) + 1
    print("keys per matrix row: " + ", ".join(f"{r}:{n}" for r, n in sorted(by_row.items())))


if __name__ == "__main__":
    main()
