"""The left-most third of the two case shells, sized for a home 3D printer, for test fitting.

The geometry is the real case's: `make_top_frame()` and `make_bottom_case()` from
`case/src/lib/case_geom.py`, clipped at CUT_X. Nothing is copied, so a change to the case
shows up here on the next build, and nothing in `case/` is modified.

Same frame as the case (plate frame X/Y, Z = 0 at the PCB top), so the pieces line up with
`case/STEP/plate.step` and `case/STEP/pcb.step` for fit checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

# case-proto/src/proto/left_third.py -> case/src, where the real case's `lib` package lives
CASE_SRC = str(Path(__file__).resolve().parents[3] / "case" / "src")
if CASE_SRC not in sys.path:
    sys.path.append(CASE_SRC)

from cadgen import build123d as bd  # noqa: E402

from lib import refs  # noqa: E402
from lib.case_geom import (  # noqa: E402
    BOTTOM_BOSS_LOWER_D,
    CASE_BOTTOM_Z,
    CASE_TOP_Z,
    OUTER_D,
    OUTER_W,
    OUTER_X0,
    OUTER_Y0,
    make_bottom_case,
    make_top_frame,
)

# An exact third ends at x = OUTER_X0 + OUTER_W / 3 = 94.07, which would halve the two bosses at
# x = 96.57 (the middle-left plate holes, back and front). Cut 2.5 mm past their widest part, the
# Ø10 foot of the bottom boss, so the piece keeps 5 of the 10 screw points -- enough to check the
# hole spacing in X and Y against a real plate -- plus the whole Pico / USB corner.
MID_HOLE_X = min(x for x, _, _ in refs.PLATE_HOLES if x > 0)    # 96.573
CUT_X = MID_HOLE_X + BOTTOM_BOSS_LOWER_D / 2 + 2.5              # 104.07: a 126.7 x 169.2 mm piece


def _left_of_cut(part):
    """`part` clipped to x <= CUT_X."""
    x0, y0, z0 = OUTER_X0 - 1, OUTER_Y0 - 1, CASE_BOTTOM_Z - 1
    keep = bd.Pos(x0, y0, z0) * bd.Box(
        CUT_X - x0, OUTER_D + 2, CASE_TOP_Z - CASE_BOTTOM_Z + 2, align=bd.Align.MIN
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
