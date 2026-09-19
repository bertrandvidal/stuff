"""Reference model of plate-88keys.jscad (for fit checks; the plate itself is made from the .jscad)."""
from cadgen import srgb, step

from lib.case_geom import make_plate


@step(out="../STEP/plate.step")
def plate():
    part = make_plate()
    part.color = srgb("#B8BCC2")
    return part


if __name__ == "__main__":
    plate()
