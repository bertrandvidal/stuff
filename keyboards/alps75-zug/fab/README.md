# alps75-zug — fab outputs

Generated from `alps75-zug.kicad_pcb` (v0.2) with KiCad 10.0.6 (`kicad-cli`).
Regenerate with `./export.sh`.

Ordered from **JLCPCB**, which also assembles the 88 diodes on the back. The Pico
and the switches are soldered by hand.

## What to upload

1. **`alps75-zug-gerbers.zip`** — the PCB. 12 files, flat at the archive root:
   9 gerbers, 2 Excellon drill files, 1 gerber job file.
2. At the PCB Assembly step: **`alps75-zug-bom-jlc.csv`** (BOM) and
   **`alps75-zug-cpl-jlc.csv`** (CPL / pick-and-place). Both are written by
   `jlc_assembly.py`, which `export.sh` runs.

## Order parameters (task 2.1)

| | |
|---|---|
| Size | 328.01 × 147.22 mm |
| Layers | 2 |
| Thickness | 1.6 mm |
| Units | mm, absolute origin |
| Gerber format | X2, 4.6 precision |
| Drill | Excellon, metric, decimal, PTH and NPTH in separate files |

The outline is **not a plain rectangle** — the main body is 328.01 × 123 mm with a
61.8 × 24.2 mm tab on the top left carrying the Pico and the USB port. Corners are
1 mm rounded. The profile is a single closed contour.

Holes: 182 plated (176 × 1.5 mm switch pins, 6 × 0.3 mm vias) and 4 unplated
(2 × 1.85 mm, 2 × 2.2 mm).

Every gerber carries X2 `FileFunction` attributes, so JLCPCB / PCBWay / OSHPark
detect the layers automatically and the filename convention does not matter.

The board is checked against JLCPCB's 2-layer limits: `../alps75-zug.kicad_dru`
holds the ones Board Setup doesn't already cover (PTH annular ring, NPTH size,
hole-to-hole, silkscreen text), and KiCad applies it in every DRC.

## PCB Assembly (task 3.1)

| | |
|---|---|
| PCBA type | Economic |
| Assembly side | **Bottom** |
| PCBA qty | the minimum JLCPCB allows (the other boards stay bare) |
| Parts | 88 × 1N4148WL, SOD-123F, LCSC **C108804** (Extended: one $3 feeder fee) |
| Tooling holes / edge rails | shouldn't be needed — the closest diode is 5.4 mm from the edge |
| Confirm parts placement | **yes** — you approve the placement before JLCPCB solders anything |

Only symbols with an `LCSC` field are in the BOM/CPL: the Pico (U1) and the
switches have none. To swap the part (e.g. C108804 out of stock), change the
`LCSC` field on the 88 diodes in the schematic, update the PCB from the
schematic, and rerun `./export.sh`. C81598 (1N4148W, SOD-123, Basic) also
solders onto these SOD-123F pads.

**Check the diode polarity in JLCPCB's placement preview.** The cathode band
must sit on pad 1 — the pad on the ROW net, marked by the bar on the B.Silk
outline. Look at one of each: **D1–D17** (F-row, CPL rotation 0°) and
**D18–D88** (CPL rotation 90°). Bottom-side rotations are written as
180° − KiCad's rotation because JLCPCB does not mirror bottom parts;
`jlc_assembly.py` explains it, and the CPL has been checked against the B.Cu
gerber's pad attributes (every cathode on pin 1).

## Files not in the zip (review only)

- `drc.json` — DRC result: 0 errors, 0 unconnected, 0 schematic-parity issues,
  4 warnings. All four are the same cosmetic thing: the U1 (Pico) silkscreen
  outline sits 0.11 mm past the left board edge and gets clipped. Safe to fab.
- `drill-report.txt` — hole count per tool size.
- `*-drl_map.gbr` — human-readable drill maps. Deliberately kept out of the zip;
  some fab uploaders try to read them as an extra copper layer.
