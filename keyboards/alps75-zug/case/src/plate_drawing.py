"""Cut file for the plate: the flat pattern of plate.py, i.e. of plate-88keys.jscad.

One CUT layer, 1:1 in mm, no kerf compensation -- cutting services apply their own.
"""
from cadgen import build123d as bd
from cadgen import dxf, flatten

from lib import refs
from lib.case_geom import PLATE_TOP_Z
from plate import plate


@dxf(out="../DXF/plate.dxf")
def plate_drawing():
    flat = flatten.flat_pattern(plate(), coordinate=PLATE_TOP_Z)
    # flatten_face re-bases the face on its own plane origin; put it back on the plate
    # frame so the DXF coordinates are the ones in plate-88keys.jscad / lib/refs.py.
    cx, cy = refs.PLATE_OUTLINE[0], refs.PLATE_OUTLINE[1]
    centre = flat.bounding_box().center()
    return bd.Pos(cx - centre.X, cy - centre.Y) * flat


if __name__ == "__main__":
    plate_drawing()
