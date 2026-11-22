"""Geometry factories for the alps75-zug top-mount case.

Frame (shared by every part, so the assembly needs no transforms):
  X/Y = the plate frame of plate-88keys.jscad (origin at the Esc switch centre,
        +X right, +Y towards the back), Z = 0 at the PCB TOP surface, +Z up.

Mounting (top mount, sandwich style): the plate is clamped between the top
frame's bosses (above) and the bottom case's bosses (below) at its 10 M3 holes.
M3x12 socket-head screws go up from underneath through the bottom case and the
plate into M3 heat-set inserts in the top frame. The two shells meet below the
plate (SPLIT_Z): the plate sits in a pocket of the top frame, hidden behind its
wall, and the bottom case's bosses rise above their rim to reach it. Tightening
the screws closes the seam and clamps the 1.2 mm plate at the same time. The PCB
hangs from the plate by its soldered switches and touches nothing else.

Top shape: the AEK's F-row and number-row keycaps sit 2-7 mm higher than the rest
(their skirts are cut at an angle, back higher). So the top frame is flat at the
front and beside R2-R5, ramps up beside R1 and R0 to just under the F-row skirts,
and stays flat from there to the back wall, where "zug" is engraved. The 3 mm top
panel follows that profile, so the raised part is hollow.
"""
from __future__ import annotations

import math
import sys

from cadgen import build123d as bd
from cadgen import srgb

from lib import refs

# ---- Vertical stack (Z) -------------------------------------------------------
PCB_TOP_Z = 0.0
PCB_BOTTOM_Z = PCB_TOP_Z - refs.PCB_THICKNESS            # -1.6
PLATE_BOTTOM_Z = 3.3                                      # Alps: plate top 4.5 above PCB, 1.2 plate
PLATE_TOP_Z = PLATE_BOTTOM_Z + refs.PLATE_THICKNESS       # 4.5
SEAM_BELOW_PLATE = 1.8    # top frame wall runs this far past the plate's underside, so no seam gap shows the plate
SPLIT_Z = PLATE_BOTTOM_Z - SEAM_BELOW_PLATE               # 1.5, seam between top frame and bottom case

# PCB underside to floor. The tallest things under the PCB are the Alps switch pins (~1.7-2 mm
# through a 1.6 mm board, plus the solder cone) and the SOD-123F diodes (~1.1 mm): 3.0 mm leaves
# ~1 mm over untrimmed pins, so they need no trimming.
AIR_BELOW_PCB = 3.0
FLOOR_T = 3.0
FLOOR_TOP_Z = PCB_BOTTOM_Z - AIR_BELOW_PCB                # -4.6
CASE_BOTTOM_Z = FLOOR_TOP_Z - FLOOR_T                     # -7.6

# ---- AEK keycaps (measured) -----------------------------------------------------
# Heights above the plate TOP, read off side photos of the caps on the real plate (2026-11-21;
# no calipers, so +-0.5 mm). Scale checked four ways in the same photo: the plate edge (1.2 mm),
# a cap's bottom (18.2 mm), the row pitch (19.05 mm) and the printed frame wall (8.2 mm).
# R0 and R1 skirts are cut at an angle (back higher); the F-row caps rock a little on their
# stems, so R0's front edge reads 12.3-13.5 depending on the photo.
# Per layout row (0 = F-row at the back ... 5 = space-bar row at the front):
#   (skirt bottom at the back edge, at the front edge, top rim at the back edge, at the front edge)
AEK_ROWS = {
    0: (15.3, 12.3, 21.9, 21.5),
    1: (10.7, 8.3, 18.3, 18.0),
    2: (8.9, 8.3, 17.1, 17.3),
    3: (8.4, 8.4, 15.3, 16.1),
    4: (8.4, 8.4, 14.4, 15.9),
    5: (8.4, 8.4, 14.5, 17.7),
}

FRAME_ABOVE_PLATE = 8.0   # top surface at the front and beside R2-R5: 0.4 mm under their skirts (8.4)
TOP_PANEL_T = 3.0         # the panel keeps this thickness under the ramp and the back plateau too
CASE_TOP_Z = PLATE_TOP_Z + FRAME_ABOVE_PLATE              # 12.5
PANEL_BOTTOM_Z = CASE_TOP_Z - TOP_PANEL_T                 # 9.5 (5 mm air gap above the plate)

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

# ---- Sloped top (side profile, in Y) -----------------------------------------------
# Flat at CASE_TOP_Z up to the R2/R1 boundary, a straight ramp beside R1 and R0 up to the back
# edge of the F-row keys, then a plateau at PLATEAU_Z to the back wall. The plateau sits
# PLATEAU_GAP under the back edge of the F-row skirts.
RAMP_ROWS = 2             # the ramp runs beside the last RAMP_ROWS rows (R1 and R0)
PLATEAU_GAP = 0.8
PLATEAU_ABOVE_PLATE = AEK_ROWS[0][0] - PLATEAU_GAP       # 14.5
PLATEAU_Z = PLATE_TOP_Z + PLATEAU_ABOVE_PLATE             # 19.0
RAMP_BEND_R = 20.0        # rounds the two bends of the profile (~1.7 mm either side of each)

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

# ---- Finishing ------------------------------------------------------------------------
TOP_EDGE_FILLET = 2.5
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
ENGRAVE_DEPTH = 1.0   # JLC3DP's minimum engraved detail: 0.8 mm resin/nylon, 1.0 mm FDM


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
    except Exception as exc:  # keep the part valid if the kernel refuses a fillet, but say so
        print(f"warning: {radius} mm fillet on {len(edges)} edges failed ({exc}); left sharp", file=sys.stderr)
        return part


def _ramp_ys():
    """(y0, y1): the ramp starts at the R2/R1 boundary and ends at the back edge of the F-row keys."""
    ky1 = key_area()[3]
    return ky1 - RAMP_ROWS * U, ky1


def top_z_at(y):
    """Height of the top surface at plan position y (straight segments; the bend rounding moves it < 0.1 mm)."""
    y0, y1 = _ramp_ys()
    if y <= y0:
        return CASE_TOP_Z
    if y >= y1:
        return PLATEAU_Z
    return CASE_TOP_Z + (PLATEAU_Z - CASE_TOP_Z) * (y - y0) / (y1 - y0)


def _under_top(drop):
    """Everything below the top surface lowered by `drop`: the side profile extruded across the case in X."""
    y0, y1 = _ramp_ys()
    ya, yb, z_low = OUTER_Y0 - 1, OUTER_Y0 + OUTER_D + 1, SPLIT_Z - 2
    zb, zp = CASE_TOP_Z - drop, PLATEAU_Z - drop
    profile = bd.Polygon((ya, z_low), (yb, z_low), (yb, zp), (y1, zp), (y0, zb), (ya, zb), align=None)
    bends = [v for v in profile.vertices()
             if any(abs(v.X - py) < 1e-6 and abs(v.Y - pz) < 1e-6 for py, pz in ((y0, zb), (y1, zp)))]
    profile = bd.fillet(bends, RAMP_BEND_R)
    # Plane.YZ maps the profile's (x, y) to (Y, Z)
    return bd.Pos(OUTER_X0 - 1, 0, 0) * bd.extrude(bd.Plane.YZ * profile, amount=OUTER_W + 2, dir=(1, 0, 0))


def _top_edges(part):
    """Edges where the top surface meets a wall, split into (outer edges, key-opening edges)."""
    faces = [f for f in part.faces() if f.center().Z > PANEL_BOTTOM_Z + 0.1 and f.normal_at().Z > 0.3]
    seen = {}
    for f in faces:
        for e in f.edges():
            seen[e] = seen.get(e, 0) + 1   # an edge shared by two top faces is a bend, not a boundary
    kx0, ky0, kx1, ky1 = key_area()
    m = KEY_OPENING_MARGIN + 0.5
    outer, opening = [], []
    for e, n in seen.items():
        if n == 1:
            p = e.position_at(0.5)
            inside = kx0 - m < p.X < kx1 + m and ky0 - m < p.Y < ky1 + m
            (opening if inside else outer).append(e)
    return outer, opening


def make_top_frame():
    top = PLATEAU_Z + 1
    frame = _slab(OUTER_W, OUTER_D, OUTER_R, SPLIT_Z, top) & _under_top(0)
    frame -= _slab(INNER_W, INNER_D, INNER_R, SPLIT_Z - 1, top) & _under_top(TOP_PANEL_T)   # hollow under the panel

    kx0, ky0, kx1, ky1 = key_area()
    m = KEY_OPENING_MARGIN
    opening = _slab(kx1 - kx0 + 2 * m, ky1 - ky0 + 2 * m, KEY_OPENING_R, PANEL_BOTTOM_Z - 1, top + 1,
                    cx=(kx0 + kx1) / 2, cy=(ky0 + ky1) / 2)
    frame -= opening

    bosses = []
    for x, y, _ in refs.PLATE_HOLES:
        # up into the panel at the boss's highest point (the panel rises towards the back)
        z1 = top_z_at(y + TOP_BOSS_D / 2) - TOP_PANEL_T + 0.5
        bosses.append(_cyl(x, y, TOP_BOSS_D, PLATE_TOP_Z, z1))
        bosses += _ribs(x, y, TOP_BOSS_D, PLATE_TOP_Z, z1)
    frame += bosses
    frame -= [_cyl(x, y, INSERT_HOLE_D, PLATE_TOP_Z - 1, PLATE_TOP_Z + INSERT_HOLE_DEPTH) for x, y, _ in refs.PLATE_HOLES]

    frame -= _usb_cut()

    frame = _fillet_edges(frame, _top_edges(frame)[0], TOP_EDGE_FILLET)
    # the engraving is cut after the fillets
    frame = _fillet_edges(frame, _top_edges(frame)[1], KEY_OPENING_FILLET)
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
    text = bd.Pos(kx1 - bb.max.X, cy - (bb.min.Y + bb.max.Y) / 2, top_z_at(cy) - ENGRAVE_DEPTH) * text   # on the plateau
    return bd.extrude(text, amount=ENGRAVE_DEPTH + 1)


def make_bottom_case():
    case = _slab(OUTER_W, OUTER_D, OUTER_R, CASE_BOTTOM_Z, SPLIT_Z)
    case -= _slab(INNER_W, INNER_D, INNER_R, FLOOR_TOP_Z, SPLIT_Z + 1)

    bosses = []
    for x, y, _ in refs.PLATE_HOLES:
        bosses.append(_cyl(x, y, BOTTOM_BOSS_LOWER_D, FLOOR_TOP_Z - 0.5, BOTTOM_BOSS_STEP_Z))
        bosses.append(_cyl(x, y, BOTTOM_BOSS_UPPER_D, BOTTOM_BOSS_STEP_Z - 0.5, PLATE_BOTTOM_Z))
        # ribs stop at the seam: above it the top frame's wall comes down past the boss
        bosses += _ribs(x, y, BOTTOM_BOSS_UPPER_D, FLOOR_TOP_Z - 0.5, SPLIT_Z)
    case += bosses
    case -= [_cyl(x, y, M3_CLEAR_D, CASE_BOTTOM_Z - 1, PLATE_BOTTOM_Z + 1) for x, y, _ in refs.PLATE_HOLES]
    case -= [_cyl(x, y, M3_HEAD_CBORE_D, CASE_BOTTOM_Z - 1, CBORE_TOP_Z) for x, y, _ in refs.PLATE_HOLES]
    case -= _usb_cut()


    outer_bottom = _face_at(case, CASE_BOTTOM_Z).outer_wire().edges()
    case = _fillet_edges(case, outer_bottom, BOTTOM_EDGE_FILLET)
    case.label = "bottom_case"
    return case


# ---- Insert practice coupon ------------------------------------------------------------
# A straight strip of the top frame's edge carrying COUPON_BOSSES copies of its insert boss: the
# same panel, wall, boss, rib and hole, the same distance from the wall and the same Z, so it prints
# in the top frame's orientation and the iron meets the same 3 mm recess below the rim. Printed with
# the case to practise pressing inserts in. It sits at the origin and is not part of the assembly.
COUPON_BOSSES = 5
COUPON_PITCH = 16.0
COUPON_DEPTH = 15.0       # wall's outer face to the panel's free edge
HOLE_TO_WALL = min(x - INNER_X0 for x, _, _ in refs.PLATE_HOLES)   # 4.5, as in the case


def make_insert_coupon():
    length = COUPON_BOSSES * COUPON_PITCH
    wall_y = COUPON_DEPTH - WALL_T                           # inner face of the wall
    coupon = _box(0, 0, length, COUPON_DEPTH, SPLIT_Z, CASE_TOP_Z)
    coupon -= _box(-1, -1, length + 1, wall_y, SPLIT_Z - 1, PANEL_BOTTOM_Z)

    y = wall_y - HOLE_TO_WALL
    xs = [COUPON_PITCH / 2 + i * COUPON_PITCH for i in range(COUPON_BOSSES)]
    h = TOP_BOSS_D / 2
    coupon += [_cyl(x, y, TOP_BOSS_D, PLATE_TOP_Z, PANEL_BOTTOM_Z + 0.5) for x in xs]
    coupon += [_box(x - h, y, x + h, wall_y + 1, PLATE_TOP_Z, PANEL_BOTTOM_Z + 0.5) for x in xs]
    coupon -= [_cyl(x, y, INSERT_HOLE_D, PLATE_TOP_Z - 1, PLATE_TOP_Z + INSERT_HOLE_DEPTH) for x in xs]
    coupon.label = "insert_coupon"
    return coupon


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
# Row heights and tilts come from AEK_ROWS (measured, at the top of this file).
KEYCAP_TOP_INSET_X = 5.5  # skirt-to-top taper, total across the width
KEYCAP_TOP_DEPTH = 14.0   # top surface depth (front to back), every row (photos: 13.4-15.6)
KEYCAP_DISH_DEPTH = 0.8   # cylindrical dish sag across the width (1u-2u keys)
KEYCAP_DISH_DEPTH_WIDE = 0.5   # 2.25u-2.75u keys; the space bar (>= 6u) is left flat
AEK_ALPHA = "#D9D3C5"     # platinum alphas
AEK_MOD = "#A9A396"       # darker modifiers / F-row / nav column


def _tilted_plane(x, y, back, front, depth):
    """Plane through heights `back`/`front` (above the plate top) at y +- depth/2; tilted about X."""
    tilt = math.degrees(math.atan2(back - front, depth))   # + = back higher
    return bd.Plane(origin=(x, y, PLATE_TOP_Z + (back + front) / 2), x_dir=(1, 0, 0), z_dir=(0, 0, 1)).rotated((tilt, 0, 0))


def _keycap(x, y, w, row):
    skirt_back, skirt_front, top_back, top_front = AEK_ROWS[row]
    bw, bdp = w * U - KEYCAP_GAP, U - KEYCAP_GAP
    tw, tdp = bw - KEYCAP_TOP_INSET_X, KEYCAP_TOP_DEPTH
    bottom_plane = _tilted_plane(x, y, skirt_back, skirt_front, bdp)
    top_plane = _tilted_plane(x, y, top_back, top_front, tdp)
    cap = bd.loft([bottom_plane * bd.Rectangle(bw, bdp), top_plane * bd.Rectangle(tw, tdp)])
    depth = 0.0 if w >= 6 else (KEYCAP_DISH_DEPTH if w <= 2 else KEYCAP_DISH_DEPTH_WIDE)
    if depth:
        radius = tw ** 2 / (8 * depth) + depth / 2      # cylinder through the top's side edges
        dish = top_plane * bd.Pos(0, 0, radius - depth) * bd.Rot(90, 0, 0) * bd.Cylinder(radius, tdp + 10)
        cap = cap - dish
    return cap


def make_keycaps():
    """AEK-profile keycaps from the photo measurements, one labelled solid per key (visual/clearance reference)."""
    caps = []
    for i, (x, y, rot, w) in enumerate(refs.SWITCHES):
        row = round(-y / U)
        cap = _keycap(x, y, w, row)
        cap.label = f"keycap_r{row}_{i}"
        is_mod = row == 0 or w > 1.0 or x > 280
        cap.color = srgb(AEK_MOD if is_mod else AEK_ALPHA)
        caps.append(cap)
    return bd.Compound(children=caps, label="keycaps")
