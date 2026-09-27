"""Left third of the top frame, for a test-fit print at home (print upside down, top face on the bed)."""
from cadgen import srgb, step

from proto.left_third import make_top_frame_left


@step(out="../STEP/case_top_left.step")
def case_top_left():
    part = make_top_frame_left()
    part.color = srgb("#3A3F47")
    return part


if __name__ == "__main__":
    case_top_left()
