#!/usr/bin/env python3
"""Clear the one real clearance violation left by the Alps swap (SW80).

SW80's diode-anode pad ends up 0.1593mm from two Row6 segments, 0.0407mm
short of the board's 0.2mm rule -- the only place on the board where the
Alps pad position lands too close to pre-existing copper.

Narrowing those two segments from 0.25mm to 0.15mm buys 0.05mm of clearance,
which clears the rule. A matrix row carries microamps, so trace width is
irrelevant here electrically, and 0.15mm is comfortably above JLCPCB's
0.127mm minimum for 1oz copper. The board sets no min_track_width rule.
"""
import re
import sys

SEGMENTS = [  # (start, end) of the two offending Row6 segments, on F.Cu
    ((308.41183, 214.672293), (312.264357, 214.672293)),
    ((312.264357, 214.672293), (312.857064, 215.265)),
]
NEW_WIDTH = "0.15"

path = sys.argv[1]
src = open(path).read()
n = 0


def repl(m):
    global n
    x1, y1, x2, y2 = (float(m.group(i)) for i in range(1, 5))
    for (ax, ay), (bx, by) in SEGMENTS:
        if {(round(x1, 6), round(y1, 6)), (round(x2, 6), round(y2, 6))} == \
           {(round(ax, 6), round(ay, 6)), (round(bx, 6), round(by, 6))}:
            n += 1
            return m.group(0).replace(f"(width {m.group(5)})", f"(width {NEW_WIDTH})")
    return m.group(0)


src = re.sub(
    r'\(segment\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\)'
    r'\s*\(width ([\d.]+)\)\s*\(layer "F\.Cu"\)',
    repl, src)

open(path, "w").write(src)
print(f"narrowed {n} segment(s) to {NEW_WIDTH}mm")
