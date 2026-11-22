# alps75-zug case prototype — left quarter, for a home 3D printer

Test-fit pieces cut from the real case in `../case/`. The full shells (~350 x 169 mm) don't fit a
home printer; the left end does, and it holds most of what can go wrong: the Pico and its USB
cutout, the left wall and its 3 screw points, and the left end of the ramp and back plateau (the
top's fit against the real F-row and number-row keycaps).

| Model | Output | What it is |
| --- | --- | --- |
| `case_top_left.py` | `STEP/case_top_left.step` | Top frame, x <= 64.91 (87.5 x 169.2 x 17.5 mm: 11.0 mm at the front, 17.5 mm at the back plateau) |
| `case_bottom_left.py` | `STEP/case_bottom_left.step` | Bottom case, x <= 64.91 (87.5 x 169.2 x 10.9 mm) |
| `export_stl.py` | `STL/case_top_left.stl`, `STL/case_bottom_left.stl` | **Print files** for both (watertight, same exporter as the case's) |

Nothing is copied from the case: `proto/left_quarter.py` calls `make_top_frame()` and
`make_bottom_case()` from `case/src/lib/case_geom.py` and clips them at `CUT_X`, so the pieces
follow every change to the case. Nothing in `case/` is modified. The pieces stay in the case's
frame, so they line up with `case/STEP/plate.step` and `case/STEP/pcb.step`.

```bash
PY=~/.venvs/cadgen/bin/python   # cadgen==0.6.4, same as the case
$PY src/case_top_left.py
$PY src/case_bottom_left.py
$PY src/export_stl.py            # the STLs for the slicer; always rebuilds
```

## Where the cut is

At an exact quarter of the width, x = 64.91. No boss is near it: the nearest plate holes are
at x = -15.08 (the left wall) and x = 96.57 (middle-left), and `proto/left_quarter.py` asserts
the cut stays 2.5 mm clear of every boss, since half a boss can't take an insert or a screw.
The piece keeps 3 whole screw points along the left wall, which checks the hole spacing in Y
against a real plate. It does not check the spacing in X: that needs the middle-left holes, which
the earlier left-third piece (cut at x = 104.07) kept.

## Printing

- **Top frame upright** (wall rim on the bed), with tree supports inside the pocket. Its top is no
  longer flat (front bezel, ramp, back plateau), so upside down it would rest on the plateau only and
  need supports on the visible ramp and front bezel; upright, the supports stay on hidden faces (under
  the panel and the boss ends). **Bottom case floor down.**
- Both pieces are 87.5 x 169.2 mm: they fit any bed of 180 x 180 mm or more.
- PLA or PETG is fine for a fit test; the M3 heat-set inserts go into PLA and PETG too.
- The slicer centres the pieces; their coordinates in the STL are the case's (x from -22.6).

## What a print does and doesn't tell you

FDM prints holes a little undersize and outer walls a little oversize, and it shrinks differently
from the final PC/ABS or resin part. Use this piece to check positions and clearances (screw holes
against the plate, the USB plug against its cutout, the Pico under the solid bezel, the plate edge
against the walls, the switch pins above the floor), not fine tolerances.
