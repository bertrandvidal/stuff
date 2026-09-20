"""Write the printable STLs for the two case shells.

Deliberately NOT the `@stl` door: cadgen's mesher leaves a handful of open edges in
both shells (4 in the top frame, 6 in the bottom case) at every chord/angle tolerance,
which print services flag as a non-watertight mesh. build123d's own exporter tessellates
the same solids watertight, so the fab STLs come from here instead.

    python src/export_stl.py

Geometry comes from `lib.case_geom`, the same place `case_top.py` and `case_bottom.py`
take it from, so the STLs cannot drift from the STEP files.
"""
from pathlib import Path

from cadgen import build123d as bd

from lib.case_geom import make_bottom_case, make_top_frame

OUT_DIR = Path(__file__).resolve().parent.parent / "STL"

# Chord deflection in mm and normal spread in radians. 0.01 mm is far below any
# printing process's resolution; 0.2 rad puts ~31 facets around the Ø6 bosses.
TOLERANCE = 0.01
ANGULAR_TOLERANCE = 0.2

PARTS = (("case_top", make_top_frame), ("case_bottom", make_bottom_case))


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for name, build in PARTS:
        part = build()
        out = OUT_DIR / f"{name}.stl"
        bd.export_stl(part, str(out), tolerance=TOLERANCE, angular_tolerance=ANGULAR_TOLERANCE)
        bb = part.bounding_box()
        print(f"wrote {out.relative_to(OUT_DIR.parent)}  "
              f"{bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")


if __name__ == "__main__":
    main()
