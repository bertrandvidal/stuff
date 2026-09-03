# `Alps_Solderable_MXPadOrder.pretty` — derived footprint library

Derived from ai03's `Alps_Solderable.pretty` (MIT, vendored unmodified at
`pcb/vendor/ai03-alps-solderable/`). **The only change is that pad 1 and
pad 2 are numbered the other way round.** No coordinate, drill, pad size,
silkscreen line, or courtyard differs from upstream.

## Why

Quanta75 was laid out for Cherry MX, using KiCad's
`Button_Switch_Keyboard:SW_Cherry_MX_*_PCB` footprints. Relative to the key
centre, the two libraries put their numbered pads on opposite sides:

| | pad 1 | pad 2 |
|---|---|---|
| KiCad Cherry MX | `( 2.54, -5.08)` — upper right | `(-3.81, -2.54)` — lower left |
| ai03 Alps (upstream) | `(-2.50, -4.00)` — upper left | `( 2.50, -4.50)` — upper right |

Quanta75's schematic connects switch pin 1 to the diode anode and pin 2 to the
row, and its copper delivers those nets to the upper-right and lower-left of
each key respectively. Dropping upstream's numbering in unchanged therefore
sends each net to the hole on the *far side* of the switch — a 5.1mm and 6.6mm
jump that collides with the row backbone at nearly half the switches. That is
what produced the (since-deleted) `REROUTE-CHECKLIST.md`.

With the numbering swapped, each net lands **0.58mm** and **1.96mm** from the
copper it already reaches, and the board comes out with no new shorts at all.

A keyswitch is a non-polar SPST contact — the diode carries the polarity — so
which hole is called "1" is arbitrary, and swapping the labels changes nothing
electrically or physically. Pad numbering conventions genuinely differ between
keyboard footprint libraries; this is bookkeeping, not a modification of ai03's
design.

## How it was generated

The six sizes actually placed on the board (1U, 1.25U, 1.5U, 1.75U, 2U, 6.25U)
were extracted from the board itself by `pcb/tools/regen_lib_from_board.py`, so
they are a byte-level match for what is placed and KiCad reports no
`lib_footprint_mismatch`. The remaining sizes (2.25U, 2.75U, 3U, 6.5U, 7U, ISO)
are ai03's files with the pad numbers swapped, carried over so they are
available if the ANSI reshape needs them; none is currently placed.

If you ever re-import from upstream ai03, remember to re-apply the swap —
otherwise every switch's two nets silently trade places.
