#!/usr/bin/env python3
"""Reconnect each switch's row-net pad after the corrected Alps swap.

Alps pad 1 sits 1.96mm from where the old Cherry MX row pad was
(delta (+1.31, -1.46) from key centre). Every switch has the same
delta, so each needs the same short stub: a straight segment from the
old pad centre to the new one, on whatever layer the existing row
track already arrives on.
"""
import math
import re
import sys
import uuid

OLD_ROW_PAD = (-3.81, -2.54)   # Cherry MX row-net hole, relative to key centre
NEW_ROW_PAD = (-2.50, -4.00)   # Alps row-net hole, relative to key centre
TOL = 0.15

path = sys.argv[1]
src = open(path).read()

# --- switch key centres + their pad-1 net, from the corrected board ---
starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', src)] + [len(src)]
switches = []
for i in range(len(starts) - 1):
    blk = src[starts[i]:starts[i + 1]]
    if 'Alps_Solderable_MXPadOrder:' not in blk[:80]:
        continue
    ref = re.search(r'"Reference" "(SW\d+)"', blk)
    at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)', blk)
    pm = re.search(r'\(pad "2" thru_hole[\s\S]{0,900}?\(net (\d+) "([^"]*)"\)', blk)
    if ref and at and pm:
        switches.append((ref.group(1), float(at.group(1)), float(at.group(2)),
                         int(pm.group(1)), pm.group(2)))

# --- existing tracks, so we can learn each stub's layer + width ---
tracks = [(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)),
           float(m.group(5)), m.group(6), int(m.group(7)))
          for m in re.finditer(
              r'\(segment\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\)'
              r'\s*\(width ([\d.]+)\)\s*\(layer "([^"]+)"\)\s*\(net (\d+)\)', src)]

new_segments = []
skipped = []
for ref, cx, cy, net, netname in switches:
    ox, oy = cx + OLD_ROW_PAD[0], cy + OLD_ROW_PAD[1]
    nx, ny = cx + NEW_ROW_PAD[0], cy + NEW_ROW_PAD[1]
    hits = [t for t in tracks
            if t[6] == net and (math.hypot(t[0] - ox, t[1] - oy) < TOL
                                or math.hypot(t[2] - ox, t[3] - oy) < TOL)]
    if not hits:
        skipped.append(ref)
        continue
    for layer in sorted({t[5] for t in hits}):
        width = max(t[4] for t in hits if t[5] == layer)
        new_segments.append(
            f'\t(segment\n\t\t(start {ox:g} {oy:g})\n\t\t(end {nx:g} {ny:g})\n'
            f'\t\t(width {width:g})\n\t\t(layer "{layer}")\n\t\t(net {net})\n'
            f'\t\t(uuid "{uuid.uuid4()}")\n\t)\n')

# splice in just before the closing paren of the board
cut = src.rstrip().rfind('\n)')
open(path, 'w').write(src[:cut] + '\n' + ''.join(new_segments) + src[cut:])
print(f"added {len(new_segments)} stubs for {len(switches) - len(skipped)} switches; "
      f"no arriving row track found for: {skipped or 'none'}")
