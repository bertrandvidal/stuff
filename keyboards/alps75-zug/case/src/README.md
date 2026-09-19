# alps75-zug case — model catalog

Top-mount (sandwich) case for the alps75-zug PCB and `plate-88keys.jscad`, for PC or ABS
(print service or injection moulding: each part is one piece, ~362 x 175 mm).

| Model | Output | What it is |
| --- | --- | --- |
| `case_top.py` | `STEP/case_top.step`, `STL/case_top.stl` | Top frame: key opening, solid bezel over the Pico, 10 insert bosses, 0.6 mm "zug" engraving |
| `case_bottom.py` | `STEP/case_bottom.step`, `STL/case_bottom.stl` | Bottom tray: 10 counterbored screw bosses, 10 mm air gap under the PCB, flat bottom |
| `plate.py` | `STEP/plate.step` | Reference copy of the plate (make the real one from the .jscad) |
| `pcb.py` | `STEP/pcb.step` | Reference PCB outline + Pico (from the .kicad_pcb) |
| `keycaps.py` | `STEP/keycaps.step` | Reference keycap envelope (assumed height) |
| `assembly.py` | `STEP/assembly.step` | Everything stacked, for fit checks |

All dimensions live in `lib/case_geom.py`. `lib/refs.py` is generated from the plate and PCB by
`tools/extract_refs.py` (run it with KiCad's Python after changing either), then rebuild:

```bash
PY=~/.venvs/cadgen/bin/python   # cadgen==0.6.4
$PY src/assembly.py              # builds every part it uses
```

## Stack (Z = 0 at the PCB top)

| z (mm) | |
| --- | --- |
| 11.5 | top of the frame |
| 8.5 – 11.5 | top panel (3 mm), 4 mm above the plate |
| 3.3 – 4.5 | plate (1.2 mm); the seam between the two shells is at 3.3 |
| -1.6 – 0 | PCB |
| -11.6 | floor top: 10 mm of air under the PCB |
| -14.6 | bottom of the case (26.1 mm total height) |

## Hardware and assembly

- 10 × M3 heat-set inserts, 4 mm long (hole Ø4.0 × 5 mm deep), pressed into the top frame bosses.
- 10 × M3 × 12 socket-head cap screws (ISO 4762), from underneath.
- Rubber feet of your choice (the bottom is flat, no recesses).

1. Solder switches to the plate + PCB as usual.
2. Set the plate + PCB into the bottom case: the plate rests on the 10 boss tops, the USB side to the left.
3. Place the top frame on top and drive the screws up through the bottom case and the plate into the inserts.
   The plate is clamped between the two sets of bosses and the shells close on the seam.

The bezel has no BOOTSEL hole: flash via the firmware's bootloader keycode (e.g. QMK `QK_BOOT` or Bootmagic).
If the Pico is ever unresponsive, open the case and press BOOTSEL through the plate's cutout.

The engraving uses macOS's system Arial Black (`/System/Library/Fonts/Supplemental/Arial Black.ttf`,
`ENGRAVE_FONT` in `lib/case_geom.py`). It is not in the repo because it can't be redistributed;
point `ENGRAVE_FONT` at a local copy to build on another machine.
