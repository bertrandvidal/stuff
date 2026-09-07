#!/usr/bin/env python3
"""Correct the Cherry MX -> Alps footprint swap on the Quanta75 board.

The first pass of the swap (commit 058b1e5) reused each Cherry footprint's
`(at ...)` verbatim and carried nets across by pad number. Both are wrong:

1. Position. KiCad's `Button_Switch_Keyboard:SW_Cherry_MX_*_PCB` footprints
   put their origin ON PAD 1, with the switch centre at local (-2.54, 5.08)
   -- the centre-post NPTH triple sits at (-7.62, 5.08) / (-2.54, 5.08) /
   (2.54, 5.08) in every size variant. ai03's Alps footprints put their
   origin ON THE KEY CENTRE. Reusing the `(at ...)` therefore shifted every
   switch by (+2.54, -5.08), 5.68mm off the keycap grid.

2. Pad numbering. Relative to the key centre the two libraries number their
   holes in opposite positions:

       Cherry MX   pad 1 = ( 2.54, -5.08)   pad 2 = (-3.81, -2.54)
       Alps (ai03) pad 1 = (-2.50, -4.00)   pad 2 = ( 2.50, -4.50)

   Cherry's pad 1 is the upper-RIGHT hole, ai03's is the upper-LEFT. Keeping
   each net on its old pad *number* therefore sent it to the hole on the far
   side of the switch -- a 5.1mm / 6.6mm jump that is what collided with
   Quanta75's row backbone. Matching them by POSITION instead leaves each net
   0.58mm and 1.96mm from the copper it already lands on.

This script fixes both, and repoints the switches at
`Alps_Solderable_MXPadOrder` -- ai03's footprints with the pad numbers
swapped, so the schematic's pin 1 / pin 2 land on the holes Quanta75's copper
already reaches. A keyswitch is a non-polar SPST contact, so renumbering its
pads changes nothing electrically; the diode carries the polarity.

Idempotent: run once on the output of the original swap.
"""
import re
import sys

CENTRE_OFFSET = (-2.54, 5.08)   # MX footprint origin -> key centre
OLD_LIB = "Alps_Solderable:"
NEW_LIB = "Alps_Solderable_MXPadOrder:"
REF_POS = (0.0, 3.175)          # ai03's reference-text position, clear of the pads


def fmt(v):
    """Full-precision coordinate, no exponent, no trailing zeros."""
    return f"{v:.6f}".rstrip("0").rstrip(".") or "0"


def fix_pcb(path):
    src = open(path).read()
    starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', src)] + [len(src)]
    pieces, cursor = [], 0
    n = 0

    for i in range(len(starts) - 1):
        s, e = starts[i], starts[i + 1]
        blk = src[s:e]
        if OLD_LIB not in blk[:80]:
            continue

        # --- 1. origin: old MX pad-1 position -> key centre ---
        at = re.search(r'(\n\t\t\(at )([-\d.]+) ([-\d.]+)(\)?)', blk)
        x, y = float(at.group(2)), float(at.group(3))
        blk = (blk[:at.start()]
               + f"{at.group(1)}{fmt(x + CENTRE_OFFSET[0])} {fmt(y + CENTRE_OFFSET[1])}{at.group(4)}"
               + blk[at.end():])

        # --- 2. swap the two pads' coordinates, leaving each net on its own
        #        pad number so schematic pin 1 / pin 2 stay consistent ---
        pad_ats = [m for m in re.finditer(r'(\(pad "[12]" thru_hole \w+\s*\n?\s*\(at )([-\d.]+) ([-\d.]+)', blk)]
        if len(pad_ats) != 2:
            pad_ats = [m for m in re.finditer(r'(\(pad "[12]"[\s\S]{0,60}?\(at )([-\d.]+) ([-\d.]+)', blk)]
        assert len(pad_ats) == 2, f"expected 2 switch pads, got {len(pad_ats)}"
        a, b = pad_ats
        blk = (blk[:a.start(2)] + f"{b.group(2)} {b.group(3)}" + blk[a.end(3):b.start(2)]
               + f"{a.group(2)} {a.group(3)}" + blk[b.end(3):])

        # --- 3. cosmetics inherited from the Cherry footprint ---
        blk = blk.replace(OLD_LIB, NEW_LIB, 1)
        blk = re.sub(r'\(descr "[^"]*"\)',
                     '(descr "Alps SKCM/SKCL solderable, ai03 MX_V2, pad numbering matched to KiCad Cherry MX")',
                     blk, count=1)
        blk = re.sub(r'\(tags "[^"]*"\)', '(tags "Alps SKCM SKCL keyswitch solderable")', blk, count=1)
        # reference designator sat over the new pad position
        blk = re.sub(r'(\(property "Reference" "SW\d+"\s*\n\s*\(at )[-\d.]+ [-\d.]+',
                     lambda m: f"{m.group(1)}{fmt(REF_POS[0])} {fmt(REF_POS[1])}", blk, count=1)

        pieces.append((s, e, blk))
        n += 1

    out = []
    for s, e, blk in pieces:
        out.append(src[cursor:s]); out.append(blk); cursor = e
    out.append(src[cursor:])
    open(path, "w").write("".join(out))
    return n


def fix_sch(path):
    s = open(path).read()
    s, n = re.subn(r'"' + re.escape(OLD_LIB.rstrip(":")) + r':(Alps-Solderable-[^"]+)"',
                   r'"' + NEW_LIB.rstrip(":") + r':\1"', s)
    open(path, "w").write(s)
    return n


if __name__ == "__main__":
    print(f"pcb: fixed {fix_pcb(sys.argv[1])} switch footprints")
    print(f"sch: repointed {fix_sch(sys.argv[2])} footprint properties")
