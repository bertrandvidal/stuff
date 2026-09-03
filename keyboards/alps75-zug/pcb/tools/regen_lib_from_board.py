#!/usr/bin/env python3
"""Regenerate Alps_Solderable_MXPadOrder from the footprints as placed on the board.

The board's embedded switch footprints are ai03's geometry, but written in
KiCad's current file format and with this project's own descr/tags/reference
placement. Hand-writing library files that differ from them in any of those
respects makes KiCad report `lib_footprint_mismatch` on all 81 switches.

Rather than keep two hand-edited copies in sync, take one representative
footprint per size straight off the board and strip the instance-specific
parts (placement, nets, uuids, schematic path, designator) to produce the
library. The library is then a byte-level match for what is on the board.
"""
import os
import re
import sys

BOARD, OUTDIR = sys.argv[1], sys.argv[2]
LIB = "Alps_Solderable_MXPadOrder"

src = open(BOARD).read()
starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', src)] + [len(src)]

seen = {}
for i in range(len(starts) - 1):
    blk = src[starts[i]:starts[i + 1]]
    m = re.match(r'\n\t\(footprint "' + LIB + r':([^"]+)"', blk)
    if not m or m.group(1) in seen:
        continue
    seen[m.group(1)] = blk

for name, blk in sorted(seen.items()):
    b = blk.strip("\n")
    b = re.sub(r'^\t', '', b, flags=re.M)                       # de-indent one level
    b = b.replace(f'(footprint "{LIB}:{name}"', f'(footprint "{name}"', 1)
    b = re.sub(r'\n\t\(at [-\d.]+ [-\d.]+\)\n', '\n', b, count=1)   # placement
    b = re.sub(r'\n\t\(uuid "[^"]*"\)\n', '\n', b, count=1)         # footprint uuid
    b = re.sub(r'\n\t\(path "[^"]*"\)', '', b)                      # schematic link
    b = re.sub(r'\n\t\(sheetfile "[^"]*"\)', '', b)
    b = re.sub(r'\n\t*\(net \d+ "[^"]*"\)', '', b)                  # per-pad nets
    b = re.sub(r'\n\s*\(uuid "[^"]*"\)', '', b)                     # all remaining uuids
    b = re.sub(r'\(property "Reference" "SW\d+"', '(property "Reference" "REF**"', b, count=1)
    b = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{name}"', b, count=1)
    b = ('(footprint' + b[len('(footprint'):]).rstrip()
    open(os.path.join(OUTDIR, f"{name}.kicad_mod"), "w").write(b + "\n")
    print(f"wrote {name}.kicad_mod")
