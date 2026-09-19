"""Bottom case of the alps75-zug case (print in PC or ABS, floor down)."""
from cadgen import srgb, step, stl

from lib.case_geom import make_bottom_case


@step(out="../STEP/case_bottom.step")
@stl(out="../STL/case_bottom.stl")
def case_bottom():
    part = make_bottom_case()
    part.color = srgb("#4A515C")
    return part


if __name__ == "__main__":
    case_bottom()
