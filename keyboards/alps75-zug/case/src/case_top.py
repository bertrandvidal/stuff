"""Top frame of the alps75-zug case (print in PC or ABS, top face up is NOT recommended: print upside down)."""
from cadgen import srgb, step, stl

from lib.case_geom import make_top_frame


@step(out="../STEP/case_top.step")
@stl(out="../STL/case_top.stl")
def case_top():
    part = make_top_frame()
    part.color = srgb("#3A3F47")
    return part


if __name__ == "__main__":
    case_top()
