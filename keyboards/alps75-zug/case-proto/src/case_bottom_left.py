"""Left third of the bottom case, for a test-fit print at home (print floor down)."""
from cadgen import srgb, step

from proto.left_third import make_bottom_case_left


@step(out="../STEP/case_bottom_left.step")
def case_bottom_left():
    part = make_bottom_case_left()
    part.color = srgb("#4A515C")
    return part


if __name__ == "__main__":
    case_bottom_left()
