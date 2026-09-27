"""Write the printable STLs for the left third of the two case shells.

Same approach as `case/src/export_stl.py`, for the same reason: cadgen's `@stl` mesher leaves
open edges in these shells, and build123d's own exporter tessellates them watertight.

    python src/export_stl.py

It has no freshness gate: it always rebuilds, so re-run it after any change to
`case/src/lib/case_geom.py` or to `proto/left_third.py`.
"""
from pathlib import Path

from cadgen import build123d as bd

from proto.left_third import make_bottom_case_left, make_top_frame_left

OUT_DIR = Path(__file__).resolve().parent.parent / "STL"

# Same as case/src/export_stl.py: 0.01 mm chord deflection, 0.2 rad normal spread.
TOLERANCE = 0.01
ANGULAR_TOLERANCE = 0.2

PARTS = (("case_top_left", make_top_frame_left), ("case_bottom_left", make_bottom_case_left))


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
