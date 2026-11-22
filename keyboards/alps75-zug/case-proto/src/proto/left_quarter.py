"""The left-most quarter of the two case shells, sized for a home 3D printer, for test fitting.

The geometry is the real case's: `make_top_frame()` and `make_bottom_case()` from
`case/src/lib/case_geom.py`, clipped at CUT_X. Nothing is copied, so a change to the case
shows up here on the next build, and nothing in `case/` is modified.

Same frame as the case (plate frame X/Y, Z = 0 at the PCB top), so the pieces line up with
`case/STEP/plate.step` and `case/STEP/pcb.step` for fit checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

# case-proto/src/proto/left_quarter.py -> case/src, where the real case's `lib` package lives
CASE_SRC = str(Path(__file__).resolve().parents[3] / "case" / "src")
if CASE_SRC not in sys.path:
    sys.path.append(CASE_SRC)

from cadgen import build123d as bd  # noqa: E402

from lib import refs  # noqa: E402
from lib.case_geom import (  # noqa: E402
    BOTTOM_BOSS_LOWER_D,
    CASE_BOTTOM_Z,
    PLATEAU_Z,
    OUTER_D,
    OUTER_W,
    OUTER_X0,
    OUTER_Y0,
    make_bottom_case,
    make_top_frame,
)

# An exact quarter. No boss is near the cut (the nearest plate holes are at x = -15.08 and 96.57),
# so the piece keeps the 3 screw points along the left wall -- the hole spacing in Y against a real
# plate -- plus the whole Pico / USB corner and the left end of the ramp and back plateau. It no
# longer checks the hole spacing in X: that needs the middle-left holes at x = 96.57.
CUT_X = OUTER_X0 + OUTER_W / 4                                  # 64.91: an 87.5 x 169.2 mm piece
# half a boss can't take an insert or a screw: keep the cut 2.5 mm clear of every boss's widest part
assert all(abs(x - CUT_X) > BOTTOM_BOSS_LOWER_D / 2 + 2.5 for x, _, _ in refs.PLATE_HOLES), "CUT_X runs through a boss"


def _left_of_cut(part):
    """`part` clipped to x <= CUT_X."""
    x0, y0, z0 = OUTER_X0 - 1, OUTER_Y0 - 1, CASE_BOTTOM_Z - 1
    keep = bd.Pos(x0, y0, z0) * bd.Box(
        CUT_X - x0, OUTER_D + 2, PLATEAU_Z - CASE_BOTTOM_Z + 2, align=bd.Align.MIN   # up past the back plateau
    )
    return part & keep


def make_top_frame_left():
    part = _left_of_cut(make_top_frame())
    part.label = "top_frame_left"
    return part


def make_bottom_case_left():
    part = _left_of_cut(make_bottom_case())
    part.label = "bottom_case_left"
    return part
