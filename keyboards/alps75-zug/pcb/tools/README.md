# PCB adaptation scripts

Each script is a single, reproducible edit to `pcb/board/`, so the board can be
re-derived from the pristine upstream in `pcb/vendor/` rather than existing as
an unexplained pile of hand edits. They were run once, in this order, on top of
the initial Cherry MX → Alps footprint substitution:

| # | Script | What it does |
|---|---|---|
| 1 | `fix_alps_swap.py` | Moves each switch to its true key centre (KiCad's Cherry footprints put their origin on pad 1, ai03's Alps footprints on the key centre) and swaps the two pads' coordinates so each net stays on the hole its copper already reaches. Repoints the switches at `Alps_Solderable_MXPadOrder`. |
| 2 | `regen_lib_from_board.py` | Regenerates `pcb/footprints/Alps_Solderable_MXPadOrder.pretty` from the footprints as placed, so the library matches the board exactly and KiCad reports no `lib_footprint_mismatch`. |
| 3 | `add_row_stubs.py` | Adds the one ~2mm stub per switch that reconnects the row net to its new pad — 86 segments, all generated mechanically. |
| 4 | `fix_sw80_clearance.py` | Narrows two Row6 segments near SW80 from 0.25mm to 0.15mm, the only place an Alps pad lands inside the 0.2mm clearance rule. |

## Verifying

Always pass `--refill-zones`. Without it a stale GND pour reports several
hundred phantom `hole_clearance` and `solder_mask_bridge` violations against
switch pads:

```sh
kicad-cli pcb drc --refill-zones --severity-error --severity-warning \
  pcb/board/Quanta75_BareRP2040_JLCPCBAoptimized.kicad_pcb
```

Compare against the untouched upstream board, **not** against zero — Quanta75
ships with 302 violations of its own (199 of them `lib_footprint_issues`):

```sh
kicad-cli pcb drc --refill-zones --severity-error --severity-warning \
  pcb/vendor/quanta75-bare-rp2040/Quanta75_BareRP2040_JLCPCBAoptimized.kicad_pcb
```

Current state: **284 violations vs. upstream's 302**, with no new shorting
items and no new clearance violations. The one genuinely new item is a dangling
`Net-(D76-A)` track at SW76, the ISO Enter key, which the ANSI reshape removes.

Note that `kicad-cli pcb drc --schematic-parity` is **not** a useful check here:
it reports zero issues even on a board with a switch pad deliberately rewired to
GND, so it cannot catch net-to-pad mistakes.
