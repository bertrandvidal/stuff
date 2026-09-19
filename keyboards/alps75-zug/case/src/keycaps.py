"""APPROXIMATE AEK-profile keycaps (not measured), for looks and frame-opening clearance checks."""
from cadgen import step

from lib.case_geom import make_keycaps


@step(out="../STEP/keycaps.step")
def keycaps():
    return make_keycaps()


if __name__ == "__main__":
    keycaps()
