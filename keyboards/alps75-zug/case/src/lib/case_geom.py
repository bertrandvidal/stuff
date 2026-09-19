"""Geometry factories for the alps75-zug top-mount case.

Frame (shared by every part, so the assembly needs no transforms):
  X/Y = the plate frame of plate-88keys.jscad (origin at the Esc switch centre,
        +X right, +Y towards the back), Z = 0 at the PCB TOP surface, +Z up.

Mounting (top mount, sandwich style): the plate is clamped between the top
frame's bosses (above) and the bottom case's bosses (below) at its 10 M3 holes.
M3x12 socket-head screws go up from underneath through the bottom case and the
plate into M3 heat-set inserts in the top frame. The two shells meet at the
plate's underside (SPLIT_Z), so tightening the screws closes the seam and
clamps the 1.2 mm plate at the same time. The PCB hangs from the plate by its
soldered switches and touches nothing else.
"""
from __future__ import annotations

from cadgen import build123d as bd
from cadgen import srgb

from lib import refs

# ---- Vertical stack (Z) -------------------------------------------------------
PCB_TOP_Z = 0.0
PCB_BOTTOM_Z = PCB_TOP_Z - refs.PCB_THICKNESS            # -1.6
PLATE_BOTTOM_Z = 3.3                                      # Alps: plate top 4.5 above PCB, 1.2 plate
PLATE_TOP_Z = PLATE_BOTTOM_Z + refs.PLATE_THICKNESS       # 4.5
SPLIT_Z = PLATE_BOTTOM_Z                                  # seam between top frame and bottom case

AIR_BELOW_PCB = 10.0      # "roomy": open cavity between PCB underside and floor
FLOOR_T = 3.0
FLOOR_TOP_Z = PCB_BOTTOM_Z - AIR_BELOW_PCB                # -11.6
CASE_BOTTOM_Z = FLOOR_TOP_Z - FLOOR_T                     # -14.6

FRAME_ABOVE_PLATE = 7.0   # top surface height above the plate top (keycap skirts sit about here)
TOP_PANEL_T = 3.0
CASE_TOP_Z = PLATE_TOP_Z + FRAME_ABOVE_PLATE              # 11.5
PANEL_BOTTOM_Z = CASE_TOP_Z - TOP_PANEL_T                 # 8.5 (4 mm air gap above the plate)

# ---- Plan view (XY) -------------------------------------------------------------
WALL_T = 3.0
PLATE_GAP = 0.5           # plate edge to inner wall, each side
PCX, PCY, PW, PD, PR = refs.PLATE_OUTLINE
INNER_W, INNER_D, INNER_R = PW + 2 * PLATE_GAP, PD + 2 * PLATE_GAP, PR + PLATE_GAP
OUTER_W, OUTER_D, OUTER_R = INNER_W + 2 * WALL_T, INNER_D + 2 * WALL_T, INNER_R + WALL_T
INNER_X0, INNER_X1 = PCX - INNER_W / 2, PCX + INNER_W / 2
INNER_Y0, INNER_Y1 = PCY - INNER_D / 2, PCY + INNER_D / 2
OUTER_X0, OUTER_Y0 = PCX - OUTER_W / 2, PCY - OUTER_D / 2

U = 19.05                 # key pitch
KEY_OPENING_MARGIN = 1.0  # key-area edge to frame opening (keycaps are ~0.45 mm inside the key area)
KEY_OPENING_R = 1.0

# ---- Fasteners --------------------------------------------------------------------
M3_CLEAR_D = 3.4
M3_HEAD_CBORE_D = 6.5     # ISO 4762 M3 head is 5.5 mm
CBORE_TOP_Z = -3.0        # screw head seat; M3x12 from here ends at z=9.0
INSERT_HOLE_D = 4.0       # M3 x 4 mm heat-set insert (e.g. OD 4.2-4.6 knurl)
INSERT_HOLE_DEPTH = 5.0   # from the plate top, leaves 2 mm skin under the top surface
TOP_BOSS_D = 8.0
BOTTOM_BOSS_UPPER_D = 6.0 # must stay 0.5 mm clear of the PCB edge (holes sit 3.5 mm outside it)
BOTTOM_BOSS_LOWER_D = 10.0
BOTTOM_BOSS_STEP_Z = -2.5 # wide section stays 0.9 mm under the PCB bottom
RIB_REACH = 6.0           # a hole closer than this to an inner wall gets a rib to that wall

# ---- Openings -----------------------------------------------------------------------
# Micro-USB plug overmold ~11 x 7 mm centred ~2.3 mm above the PCB top (Pico 1 mm + receptacle).
USB_CENTER_Z = 2.3
USB_CUT_W, USB_CUT_H, USB_CUT_R = 13.0, 9.0, 1.5
BOOTSEL_POKE_D = 3.0      # paperclip hole through the top panel above the plate's BOOTSEL cutout

# ---- Finishing ------------------------------------------------------------------------
TOP_EDGE_FILLET = 1.5
BOTTOM_EDGE_FILLET = 1.5
KEY_OPENING_FILLET = 0.8

# ---- Engraving -----------------------------------------------------------------------
# "zug" in Arial Black on the back bezel. The ink spans the last two key columns, ending flush
# with the right edge of the keys, and its bounding box is centred one third of the way from
# the back edge of the F-row keys to the back edge of the case.
ENGRAVE_TEXT = "zug"
ENGRAVE_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"   # macOS system font (not redistributable)
ENGRAVE_SPAN_KEYS = 2
ENGRAVE_FRACTION = 1 / 3   # 0 = back edge of the keys, 1 = back edge of the case
ENGRAVE_DEPTH = 0.6


def key_area():
    """(x0, y0, x1, y1) of the keycap grid, from the plate's switch list."""
    xs0 = [x - w * U / 2 for x, y, rot, w in refs.SWITCHES]
    xs1 = [x + w * U / 2 for x, y, rot, w in refs.SWITCHES]
    ys = [y for x, y, rot, w in refs.SWITCHES]
    return min(xs0), min(ys) - U / 2, max(xs1), max(ys) + U / 2


def _slab(w, d, r, z0, z1, cx=PCX, cy=PCY):
    return bd.Pos(cx, cy, z0) * bd.extrude(bd.RectangleRounded(w, d, r), amount=z1 - z0)


def _cyl(x, y, d, z0, z1):
    return bd.Pos(x, y, z0) * bd.Cylinder(d / 2, z1 - z0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))


def _box(x0, y0, x1, y1, z0, z1):
    return bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * bd.Box(
        x1 - x0, y1 - y0, z1 - z0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    )


def _ribs(x, y, width, z0, z1):
    """Webs from a boss at (x, y) to every inner wall closer than RIB_REACH (overlapping 1 mm into it)."""
    h = width / 2
    out = []
    if x - INNER_X0 < RIB_REACH:
        out.append(_box(INNER_X0 - 1, y - h, x, y + h, z0, z1))
    if INNER_X1 - x < RIB_REACH:
        out.append(_box(x, y - h, INNER_X1 + 1, y + h, z0, z1))
    if y - INNER_Y0 < RIB_REACH:
        out.append(_box(x - h, INNER_Y0 - 1, x + h, y, z0, z1))
    if INNER_Y1 - y < RIB_REACH:
        out.append(_box(x - h, y, x + h, INNER_Y1 + 1, z0, z1))
    return out


def _usb_cut():
    """Through-cut in the left wall for the Pico's micro-USB plug (spans the seam)."""
    nx, ny = refs.PICO_USB_NOTCH[0], refs.PICO_USB_NOTCH[1]
    profile = bd.Plane.YZ * bd.Pos(ny, USB_CENTER_Z) * bd.RectangleRounded(USB_CUT_W, USB_CUT_H, USB_CUT_R)
    cut = bd.extrude(profile, amount=WALL_T + 4)
    return bd.Pos(OUTER_X0 - 1, 0, 0) * cut


def _face_at(part, z):
    """The single planar face lying at height z (top or bottom face of a shell)."""
    faces = [f for f in part.faces().filter_by(bd.Plane.XY) if abs(f.center().Z - z) < 1e-6]
    return max(faces, key=lambda f: f.area)


def _fillet_edges(part, edges, radius):
    try:
        return bd.fillet(edges, radius)
    except Exception:  # keep the part valid if the kernel refuses a fillet
        return part


def make_top_frame():
    frame = _slab(OUTER_W, OUTER_D, OUTER_R, SPLIT_Z, CASE_TOP_Z)
    frame -= _slab(INNER_W, INNER_D, INNER_R, SPLIT_Z - 1, PANEL_BOTTOM_Z)

    kx0, ky0, kx1, ky1 = key_area()
    m = KEY_OPENING_MARGIN
    opening = _slab(kx1 - kx0 + 2 * m, ky1 - ky0 + 2 * m, KEY_OPENING_R, PANEL_BOTTOM_Z - 1, CASE_TOP_Z + 1,
                    cx=(kx0 + kx1) / 2, cy=(ky0 + ky1) / 2)
    frame -= opening

    bosses = []
    for x, y, _ in refs.PLATE_HOLES:
        bosses.append(_cyl(x, y, TOP_BOSS_D, PLATE_TOP_Z, PANEL_BOTTOM_Z + 0.5))
        bosses += _ribs(x, y, TOP_BOSS_D, PLATE_TOP_Z, PANEL_BOTTOM_Z + 0.5)
    frame += bosses
    frame -= [_cyl(x, y, INSERT_HOLE_D, PLATE_TOP_Z - 1, PLATE_TOP_Z + INSERT_HOLE_DEPTH) for x, y, _ in refs.PLATE_HOLES]

    bx, by = refs.PICO_BOOTSEL[0], refs.PICO_BOOTSEL[1]
    frame -= _cyl(bx, by, BOOTSEL_POKE_D, PANEL_BOTTOM_Z - 1, CASE_TOP_Z + 1)
    frame -= _usb_cut()

    frame = _fillet_edges(frame, _face_at(frame, CASE_TOP_Z).outer_wire().edges(), TOP_EDGE_FILLET)
    # the key opening is the longest hole in the top face (the other is the BOOTSEL poke hole)
    opening_wire = max(_face_at(frame, CASE_TOP_Z).inner_wires(), key=lambda w: w.length)
    frame = _fillet_edges(frame, opening_wire.edges(), KEY_OPENING_FILLET)
    frame -= _engraving()
    frame.label = "top_frame"
    return frame


def _engraving():
    """Text cutter: ink scaled to ENGRAVE_SPAN_KEYS key widths, right-aligned to the keys."""
    kx0, ky0, kx1, ky1 = key_area()
    ref = bd.Text(ENGRAVE_TEXT, font_size=10, font_path=ENGRAVE_FONT, align=None)
    size = 10 * ENGRAVE_SPAN_KEYS * U / ref.bounding_box().size.X
    text = bd.Text(ENGRAVE_TEXT, font_size=size, font_path=ENGRAVE_FONT, align=None)
    bb = text.bounding_box()
    cy = ky1 + ENGRAVE_FRACTION * ((OUTER_Y0 + OUTER_D) - ky1)
    text = bd.Pos(kx1 - bb.max.X, cy - (bb.min.Y + bb.max.Y) / 2, CASE_TOP_Z - ENGRAVE_DEPTH) * text
    return bd.extrude(text, amount=ENGRAVE_DEPTH + 1)


def make_bottom_case():
    case = _slab(OUTER_W, OUTER_D, OUTER_R, CASE_BOTTOM_Z, SPLIT_Z)
    case -= _slab(INNER_W, INNER_D, INNER_R, FLOOR_TOP_Z, SPLIT_Z + 1)

    bosses = []
    for x, y, _ in refs.PLATE_HOLES:
        bosses.append(_cyl(x, y, BOTTOM_BOSS_LOWER_D, FLOOR_TOP_Z - 0.5, BOTTOM_BOSS_STEP_Z))
        bosses.append(_cyl(x, y, BOTTOM_BOSS_UPPER_D, BOTTOM_BOSS_STEP_Z - 0.5, SPLIT_Z))
        bosses += _ribs(x, y, BOTTOM_BOSS_UPPER_D, FLOOR_TOP_Z - 0.5, SPLIT_Z)
    case += bosses
    case -= [_cyl(x, y, M3_CLEAR_D, CASE_BOTTOM_Z - 1, SPLIT_Z + 1) for x, y, _ in refs.PLATE_HOLES]
    case -= [_cyl(x, y, M3_HEAD_CBORE_D, CASE_BOTTOM_Z - 1, CBORE_TOP_Z) for x, y, _ in refs.PLATE_HOLES]
    case -= _usb_cut()


    outer_bottom = _face_at(case, CASE_BOTTOM_Z).outer_wire().edges()
    case = _fillet_edges(case, outer_bottom, BOTTOM_EDGE_FILLET)
    case.label = "bottom_case"
    return case


# ---- Reference parts (not manufactured here; for fit checks and snapshots) ------------

def make_plate():
    plate = _slab(PW, PD, PR, PLATE_BOTTOM_Z, PLATE_TOP_Z)
    sx, sy = refs.SWITCH_CUTOUT
    cuts = []
    for x, y, rot, _ in refs.SWITCHES:
        w, d = (sy, sx) if rot else (sx, sy)
        cuts.append(_slab(w, d, 0.5, PLATE_BOTTOM_Z - 1, PLATE_TOP_Z + 1, cx=x, cy=y))
    tw, td = refs.STAB_CUTOUT
    cuts += [_slab(tw, td, 0.5, PLATE_BOTTOM_Z - 1, PLATE_TOP_Z + 1, cx=x, cy=y) for x, y in refs.STABS]
    cuts += [_cyl(x, y, 2 * r, PLATE_BOTTOM_Z - 1, PLATE_TOP_Z + 1) for x, y, r in refs.PLATE_HOLES]
    for cx, cy, w, d, r in (refs.PICO_USB_NOTCH, refs.PICO_BOOTSEL):
        cuts.append(_slab(w, d, r, PLATE_BOTTOM_Z - 1, PLATE_TOP_Z + 1, cx=cx, cy=cy))
    plate -= cuts
    plate.label = "plate"
    return plate


def make_pcb():
    board = bd.extrude(bd.Polygon(*refs.PCB_OUTLINE, align=None), amount=refs.PCB_THICKNESS, dir=(0, 0, 1))
    board = bd.Pos(0, 0, PCB_BOTTOM_Z) * board
    board.label = "pcb"
    px, py = refs.PICO_CENTER
    pico = _box(px - 25.5, py - 10.5, px + 25.5, py + 10.5, PCB_TOP_Z, PCB_TOP_Z + 1.0)
    # micro-USB receptacle: overhangs the Pico's -X edge by ~1.3 mm, top ~3.7 mm above the PCB
    usb = _box(px - 25.5 - 1.3, py - 3.75, px - 25.5 + 4.1, py + 3.75, PCB_TOP_Z + 1.0, PCB_TOP_Z + 3.7)
    pico = pico + usb
    pico.label = "pico"
    return bd.Compound(children=[board, pico], label="pcb_assembly")


KEYCAP_GAP = 0.9          # 19.05 pitch minus ~18.15 keycap footprint
KEYCAP_BOTTOM_Z = PLATE_TOP_Z + 6.0   # assumed resting skirt height for Alps-mount caps

# APPROXIMATE Apple Extended Keyboard (AEK) sculpted profile -- NOT measured from real caps.
# Built from published qualitative descriptions: rows sit a step lower than the standard Alps
# profile, heights differ strongly between rows, the home row still tilts towards the typist
# and the bottom row is nearly flat. Replace these numbers with caliper measurements to make it real.
# Per layout row (0 = F-row at the back ... 5 = space-bar row at the front):
#   (top-centre height above the plate top at rest, top tilt in degrees; + = top faces the typist)
AEK_ROWS = {
    0: (18.2, 10.0),
    1: (18.6, 9.0),
    2: (16.6, 4.0),
    3: (15.4, 2.0),
    4: (15.0, -3.0),
    5: (15.2, -1.5),
}
KEYCAP_TOP_INSET_X = 5.5  # skirt-to-top taper, total across the width
KEYCAP_TOP_DEPTH = 13.5   # top surface depth (front to back) for every row
KEYCAP_DISH_DEPTH = 0.8   # cylindrical dish sag across the width (1u-2u keys)
KEYCAP_DISH_DEPTH_WIDE = 0.5   # 2.25u-2.75u keys; the space bar (>= 6u) is left flat
AEK_ALPHA = "#D9D3C5"     # platinum alphas
AEK_MOD = "#A9A396"       # darker modifiers / F-row / nav column


def _keycap(x, y, w, row):
    top_h, tilt = AEK_ROWS[row]
    bw, bdp = w * U - KEYCAP_GAP, U - KEYCAP_GAP
    tw, tdp = bw - KEYCAP_TOP_INSET_X, KEYCAP_TOP_DEPTH
    top_plane = bd.Plane(origin=(x, y, PLATE_TOP_Z + top_h), x_dir=(1, 0, 0), z_dir=(0, 0, 1)).rotated((tilt, 0, 0))
    cap = bd.loft([bd.Plane.XY.offset(KEYCAP_BOTTOM_Z) * bd.Pos(x, y) * bd.Rectangle(bw, bdp),
                   top_plane * bd.Rectangle(tw, tdp)])
    depth = 0.0 if w >= 6 else (KEYCAP_DISH_DEPTH if w <= 2 else KEYCAP_DISH_DEPTH_WIDE)
    if depth:
        radius = tw ** 2 / (8 * depth) + depth / 2      # cylinder through the top's side edges
        dish = top_plane * bd.Pos(0, 0, radius - depth) * bd.Rot(90, 0, 0) * bd.Cylinder(radius, tdp + 10)
        cap = cap - dish
    return cap


def make_keycaps():
    """Approximate AEK-profile keycaps, one labelled solid per key (visual/clearance reference only)."""
    caps = []
    for i, (x, y, rot, w) in enumerate(refs.SWITCHES):
        row = round(-y / U)
        cap = _keycap(x, y, w, row)
        cap.label = f"keycap_r{row}_{i}"
        is_mod = row == 0 or w > 1.0 or x > 280
        cap.color = srgb(AEK_MOD if is_mod else AEK_ALPHA)
        caps.append(cap)
    return bd.Compound(children=caps, label="keycaps")
