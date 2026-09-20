# alps75-zug — fab outputs

Generated from `alps75-zug.kicad_pcb` with KiCad 10.0.6 (`kicad-cli`).
Regenerate with `./export.sh`.

## What to upload

**`alps75-zug-gerbers.zip`** — that one file is the whole order. 12 files, flat at
the archive root: 9 gerbers, 2 Excellon drill files, 1 gerber job file.

## Order parameters (task 2.1)

| | |
|---|---|
| Size | 340.35 × 152.76 mm |
| Layers | 2 |
| Thickness | 1.6 mm |
| Units | mm, absolute origin |
| Gerber format | X2, 4.6 precision |
| Drill | Excellon, metric, decimal, PTH and NPTH in separate files |

The outline is **not a plain rectangle** — the main body is 340.35 × 126 mm with a
61.8 × 26.7 mm tab on the top left carrying the Pico and the USB port. Corners are
1 mm rounded. The profile is a single closed contour.

Holes: 182 plated (176 × 1.5 mm switch pins, 6 × 0.3 mm vias) and 4 unplated
(2 × 1.85 mm, 2 × 2.2 mm).

Every gerber carries X2 `FileFunction` attributes, so JLCPCB / PCBWay / OSHPark
detect the layers automatically and the filename convention does not matter.

## Files not in the zip (review only)

- `drc.json` — DRC result: 0 errors, 0 unconnected, 0 schematic-parity issues,
  4 warnings. All four are the same cosmetic thing: the U1 (Pico) silkscreen
  outline sits 0.11 mm past the left board edge and gets clipped. Safe to fab.
- `drill-report.txt` — hole count per tool size.
- `*-drl_map.gbr` — human-readable drill maps. Deliberately kept out of the zip;
  some fab uploaders try to read them as an extra copper layer.
