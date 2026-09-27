# alps75-zug case prototype — left third, for a home 3D printer

Test-fit pieces cut from the real case in `../case/`. The full shells (~350 x 169 mm) don't fit a
home printer; the left end does, and it holds most of what can go wrong: the Pico and its USB
cutout, the left wall, and 5 of the 10 screw points.

| Model | Output | What it is |
| --- | --- | --- |
| `case_top_left.py` | `STEP/case_top_left.step` | Top frame, x <= 104.07 (126.7 x 169.2 x 8.2 mm) |
| `case_bottom_left.py` | `STEP/case_bottom_left.step` | Bottom case, x <= 104.07 (126.7 x 169.2 x 10.9 mm) |
| `export_stl.py` | `STL/case_top_left.stl`, `STL/case_bottom_left.stl` | **Print files** for both (watertight, same exporter as the case's) |

Nothing is copied from the case: `proto/left_third.py` calls `make_top_frame()` and
`make_bottom_case()` from `case/src/lib/case_geom.py` and clips them at `CUT_X`, so the pieces
follow every change to the case. Nothing in `case/` is modified. The pieces stay in the case's
frame, so they line up with `case/STEP/plate.step` and `case/STEP/pcb.step`.

```bash
PY=~/.venvs/cadgen/bin/python   # cadgen==0.6.4, same as the case
$PY src/case_top_left.py
$PY src/case_bottom_left.py
$PY src/export_stl.py            # the STLs for the slicer; always rebuilds
```

## Why the cut is at x = 104.07, not at a third

An exact third (x = 94.07) runs through the two bosses at x = 96.57, the middle-left plate
holes at the back and the front. Half a boss can't take an insert or a screw, so the cut sits
2.5 mm past the widest part of those bosses (the Ø10 foot of the bottom boss). The piece is 36%
of the width instead of 33%, and keeps 5 whole screw points: 3 along the left wall and 2 at the
cut end. That checks the hole spacing in both X and Y against a real plate.

## Printing

- **Top frame upside down** (top face on the bed), like the real one: printed face-up, the
  whole top panel would need support. **Bottom case floor down.**
- Both pieces are 126.7 x 169.2 mm: they fit any bed of 180 x 180 mm or more.
- PLA or PETG is fine for a fit test; the M3 heat-set inserts go into PLA and PETG too.
- The slicer centres the pieces; their coordinates in the STL are the case's (x from -22.6).

## What a print does and doesn't tell you

FDM prints holes a little undersize and outer walls a little oversize, and it shrinks differently
from the final PC/ABS or resin part. Use this piece to check positions and clearances (screw holes
against the plate, the USB plug against its cutout, the Pico under the solid bezel, the plate edge
against the walls, the switch pins above the floor), not fine tolerances.
