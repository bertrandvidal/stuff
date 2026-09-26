"""Add the GND copper pours (F.Cu + B.Cu) and their stitching vias to the board.

This edits ../alps75-zug.kicad_pcb in place; it is not part of export.sh. Rerun it
after rerouting: it deletes the pours and stitching vias it added last time
and starts over. Needs KiCad's own Python, for the pcbnew module:

  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 ground_pour.py

The matrix slices each pour into strips: columns run vertically on F.Cu, rows
and diode links horizontally on B.Cu. A strip only reaches GND (the Pico's
pads, on F.Cu) through vias to the other layer, so the script drops a via
roughly once per key unit, then keeps adding vias from every strip that KiCad
still reports as floating to connected copper on the other side. Whatever it
cannot connect is removed at fill time (island removal: always), so no
floating copper ends up on the board.
"""

import os
import sys

import pcbnew
from pcbnew import F_Cu, B_Cu, FromMM, VECTOR2I

PCB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "alps75-zug.kicad_pcb")
GND = "Net-(U1-GND-Pad13)"  # the Pico's GND pins; the schematic doesn't name the net
ZONE_NAME = "GND"

ZONE_CLEARANCE = 0.3  # a bit over the 0.2 mm netclass clearance, for hand-soldering margin
VIA_SIZE, VIA_DRILL = 0.6, 0.3  # same as the Default netclass / the existing vias
VIA_MARGIN = 0.1  # the via sits this far inside the fill, not just touching its edge
GRID_PITCH = 19.05  # one stitching via per key unit
SEARCH_STEP = 0.25
KEEP_VIAS_OFF = ("U1",)  # the Pico sits flat on F.Cu
KEEP_VIAS_OFF_PREFIX = "D"  # the diodes JLCPCB places on B.Cu

LAYERS = (F_Cu, B_Cu)


def remove_previous_run(board, net):
    # Delete, not Remove: once Python garbage-collects a Removed item, pcbnew's
    # SWIG wrappers break (board.GetTracks() raises "SwigPyObject is not iterable").
    for zone in list(board.Zones()):
        if zone.GetZoneName() == ZONE_NAME and zone.GetNetCode() == net.GetNetCode():
            board.Delete(zone)
    # Stitching vias are the GND vias no track ends on.
    ends = set()
    for t in board.GetTracks():
        if t.GetNetCode() == net.GetNetCode() and t.Type() == pcbnew.PCB_TRACE_T:
            ends.add((t.GetStart().x, t.GetStart().y))
            ends.add((t.GetEnd().x, t.GetEnd().y))
    for t in list(board.GetTracks()):
        if (t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == net.GetNetCode()
                and (t.GetPosition().x, t.GetPosition().y) not in ends):
            board.Delete(t)


def add_zone(board, net, layer, outline):
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNetCode(net.GetNetCode())
    zone.SetZoneName(ZONE_NAME)
    chain = outline.Outline(0)
    zone.Outline().NewOutline()
    for i in range(chain.PointCount()):
        zone.AppendCorner(chain.CPoint(i), -1)
    zone.SetLocalClearance(FromMM(ZONE_CLEARANCE))
    zone.SetMinThickness(FromMM(0.25))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.SetThermalReliefGap(FromMM(0.5))
    zone.SetThermalReliefSpokeWidth(FromMM(0.5))
    zone.SetFillMode(pcbnew.ZONE_FILL_MODE_POLYGONS)
    zone.SetAssignedPriority(0)
    zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    zone.SetBorderDisplayStyle(pcbnew.ZONE_BORDER_DISPLAY_STYLE_DIAGONAL_EDGE, FromMM(0.5), True)
    board.Add(zone)
    return zone


def fill(board, zones):
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(zones)
    board.BuildConnectivity()


class Layer:
    """One pour's current fill: its islands, and where a via fits inside it."""

    def __init__(self, zone, layer):
        self.zone, self.layer = zone, layer
        self.fill = zone.GetFilledPolysList(layer).CloneDropTriangulation()
        self.fill.BuildBBoxCaches()
        self.bboxes = [self.fill.Outline(i).BBox() for i in range(self.fill.OutlineCount())]
        room = self.fill.CloneDropTriangulation()
        room.Unfracture()
        room.Deflate(FromMM(VIA_SIZE / 2 + VIA_MARGIN), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FromMM(0.005))
        room.BuildBBoxCaches()
        self.room = room

    def island_at(self, p):
        for i, bb in enumerate(self.bboxes):
            if bb.Contains(p) and self.fill.Contains(p, i, 0, True):
                return i
        return None

    def floating(self, i):
        return self.zone.IsIsland(self.layer, i)

    def fits(self, p):
        return self.room.Contains(p, -1, 0, True)


def via_spot_ok(p, front, back, keep_off):
    return front.fits(p) and back.fits(p) and not any(bb.Contains(p) for bb in keep_off)


def spiral(center, radius):
    """Points around center, nearest first, SEARCH_STEP apart."""
    step = FromMM(SEARCH_STEP)
    n = int(radius / step)
    offsets = sorted(((dx, dy) for dx in range(-n, n + 1) for dy in range(-n, n + 1)),
                     key=lambda d: d[0] * d[0] + d[1] * d[1])
    for dx, dy in offsets:
        yield VECTOR2I(center.x + dx * step, center.y + dy * step)


def add_via(board, net, p):
    via = pcbnew.PCB_VIA(board)
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(F_Cu, B_Cu)
    via.SetPosition(p)
    via.SetWidth(FromMM(VIA_SIZE))
    via.SetDrill(FromMM(VIA_DRILL))
    via.SetNetCode(net.GetNetCode())
    board.Add(via)
    return via


def main():
    board = pcbnew.LoadBoard(PCB)
    net = board.FindNet(GND)
    if net is None:
        sys.exit(f"no net {GND!r} on the board")
    remove_previous_run(board, net)

    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False) or outline.OutlineCount() != 1:
        sys.exit("expected a single closed board outline")
    zones = {layer: add_zone(board, net, layer, outline) for layer in LAYERS}
    zone_list = pcbnew.ZONES()
    for z in zones.values():
        zone_list.append(z)

    keep_off = [fp.GetBoundingBox(False) for fp in board.GetFootprints()
                if fp.GetReference() in KEEP_VIAS_OFF or fp.GetReference().startswith(KEEP_VIAS_OFF_PREFIX)]

    vias = []

    # 1. A regular grid, roughly one via per key unit.
    fill(board, zone_list)
    front, back = Layer(zones[F_Cu], F_Cu), Layer(zones[B_Cu], B_Cu)
    bb = board.GetBoardEdgesBoundingBox()
    pitch = FromMM(GRID_PITCH)
    y = bb.GetTop() + pitch // 2
    while y < bb.GetBottom():
        x = bb.GetLeft() + pitch // 2
        while x < bb.GetRight():
            for p in spiral(VECTOR2I(x, y), pitch * 0.4):
                if via_spot_ok(p, front, back, keep_off):
                    vias.append(add_via(board, net, p))
                    break
            x += pitch
        y += pitch
    print(f"grid: {len(vias)} vias")

    # 2. Connect every strip that is still floating to connected copper on the other side.
    for rnd in range(1, 20):
        fill(board, zone_list)
        front, back = Layer(zones[F_Cu], F_Cu), Layer(zones[B_Cu], B_Cu)
        floating = [(lyr, other, i) for lyr, other in ((front, back), (back, front))
                    for i in range(lyr.fill.OutlineCount()) if lyr.floating(i)]
        if not floating:
            break
        added = 0
        for lyr, other, i in floating:
            bbox = lyr.bboxes[i]
            radius = max(bbox.GetWidth(), bbox.GetHeight()) / 2 + FromMM(SEARCH_STEP)
            for p in spiral(bbox.Centre(), radius):
                if not (bbox.Contains(p) and lyr.fill.Contains(p, i, 0, True)):
                    continue
                if not via_spot_ok(p, front, back, keep_off):
                    continue
                j = other.island_at(p)
                if j is not None and not other.floating(j):
                    vias.append(add_via(board, net, p))
                    added += 1
                    break
        print(f"round {rnd}: {len(floating)} floating islands, {added} vias added")
        if not added:
            break

    # 3. Final fill without floating copper; drop the vias that ended up with no copper around them.
    for z in zones.values():
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    fill(board, zone_list)
    front, back = Layer(zones[F_Cu], F_Cu), Layer(zones[B_Cu], B_Cu)
    dangling = [v for v in vias
                if front.island_at(v.GetPosition()) is None or back.island_at(v.GetPosition()) is None]
    for v in dangling:
        board.Delete(v)
    if dangling:
        fill(board, zone_list)
    print(f"dropped {len(dangling)} dangling vias; {len(vias) - len(dangling)} stitching vias")

    board_area = outline.Area()
    for layer in LAYERS:
        area = zones[layer].GetFilledPolysList(layer).Area()
        print(f"{board.GetLayerName(layer)}: {100 * area / board_area:.0f}% of the board is GND fill")

    board.Save(PCB)


if __name__ == "__main__":
    main()
