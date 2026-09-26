#!/usr/bin/env python3
"""Write the JLCPCB assembly files: BOM and CPL (pick-and-place) for the parts the fab places.

A part is assembled by JLCPCB iff its schematic symbol has an `LCSC` field -- today the 88
matrix diodes. The Pico (U1) and the switches have none: they are soldered by hand.

The BOM comes from the schematic, the positions from the board (`kicad-cli`, absolute origin,
the same frame as the gerbers). JLCPCB does not mirror bottom-side parts the way KiCad does,
so a bottom part's rotation is written as 180 - (KiCad rotation); top parts are unchanged.
No per-package offset is needed for D_SOD-123F: KiCad and JLCPCB both put the cathode (pad 1)
on the left at 0 deg. Still check the diodes' polarity in JLCPCB's placement preview.

Usage:  python3 fab/jlc_assembly.py        (run by fab/export.sh)
Exit:   0 on success, 1 if the BOM and the positions disagree.
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

FAB = Path(__file__).resolve().parent
SCH = FAB.parent / "alps75-zug.kicad_sch"
PCB = FAB.parent / "alps75-zug.kicad_pcb"
BOM_OUT = FAB / "alps75-zug-bom-jlc.csv"
CPL_OUT = FAB / "alps75-zug-cpl-jlc.csv"


def natural(ref: str) -> tuple:
    prefix, num = re.match(r"([A-Za-z_]+)(\d*)", ref).groups()
    return prefix, int(num or 0)


def kicad_csv(args: list[str], out: Path) -> list[dict]:
    subprocess.run(["kicad-cli", *args, "--output", str(out)], check=True, capture_output=True)
    with out.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        symbols = kicad_csv(
            ["sch", "export", "bom", "--fields", "Reference,Value,Footprint,LCSC,DNP",
             "--labels", "Reference,Value,Footprint,LCSC,DNP", "--ref-range-delimiter", "",
             "--exclude-dnp", str(SCH)],
            Path(tmp) / "bom.csv",
        )
        positions = kicad_csv(
            ["pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", str(PCB)],
            Path(tmp) / "pos.csv",
        )

    assembled = [s for s in symbols if s["LCSC"].strip()]
    pos = {p["Ref"]: p for p in positions}
    errors = [f"{s['Reference']}: has an LCSC part but no position on the board"
              for s in assembled if s["Reference"] not in pos]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    groups: dict[tuple, list[str]] = defaultdict(list)
    for s in assembled:
        footprint = s["Footprint"].split(":")[-1]
        groups[(s["Value"], footprint, s["LCSC"].strip())].append(s["Reference"])
    with BOM_OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (value, footprint, lcsc), refs in sorted(groups.items()):
            w.writerow([value, ",".join(sorted(refs, key=natural)), footprint, lcsc])

    sides: dict[str, int] = defaultdict(int)
    with CPL_OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for ref in sorted((s["Reference"] for s in assembled), key=natural):
            p = pos[ref]
            rot = float(p["Rot"])
            if p["Side"] == "bottom":
                rot = 180.0 - rot
            sides[p["Side"]] += 1
            w.writerow([ref, f"{float(p['PosX']):.4f}", f"{float(p['PosY']):.4f}",
                        p["Side"].capitalize(), f"{rot % 360:g}"])

    print(f"Wrote {BOM_OUT.name}: {len(groups)} line(s), {len(assembled)} part(s)")
    print(f"Wrote {CPL_OUT.name}: " + ", ".join(f"{n} {side}" for side, n in sorted(sides.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
