# Manual reroute checklist (post Alps footprint swap)

Context: [Task: fork Quanta75 bare-RP2040 PCB and adapt to Alps 75% ANSI layout](https://github.com/bertrandvidal/stuff/issues/24).

## Why this exists

All 81 non-ISO switch footprints have been swapped from Cherry MX to
`Alps_Solderable` (matching size, correct nets carried over to the new
pads by pad number). That part is electrically correct — verified with
`kicad-cli sch erc` (no regressions vs. the unmodified baseline).

The physical swap is **not** a drop-in replacement, though. Alps
switches have different real-world pin spacing than Cherry MX (pad "2"
in particular lands ~8.85mm / -7.04mm from where the Cherry MX pad
used to sit — see `pcb/vendor/ai03-alps-solderable/Alps_Solderable.pretty/Alps-Solderable-1U.kicad_mod`
vs. one of the original Cherry MX footprint instances for the exact
numbers). Quanta75 routes its row-signal backbone tightly past each
switch's pad 2, sized for Cherry MX's geometry. Confirmed with
`kicad-cli pcb drc` that the new Alps pad position now physically
overlaps that pre-existing row/diode/column copper at **37 of 81
switches (46%)** — this is true even before touching a single trace,
i.e. it's a real spatial collision, not a routing artifact I introduced.

I tried two automated fixes for the traces that used to reach the old
pad positions (translate the touching endpoint; delete the stub and
leave it unrouted) — see git history on this branch for both attempts,
not merged. Translating made things worse (created *new* shorts, since
a straight-line move can walk a trace through unrelated copper — no
pathfinding). Deleting is honest (no false shorts) but doesn't fix the
underlying 37 collisions either way, and both require visual judgment
to route around obstacles that a text edit can't safely automate.

**What's committed**: the footprint swap only. Original copper is left
untouched — traces still point at the old Cherry MX pad positions, now
disconnected from any pad (166 unconnected/ratsnest items in DRC,
mostly these). This is the least-invasive state to start manual routing
from.

## To do, in KiCad's GUI

1. Open `Quanta75_BareRP2040_JLCPCBAoptimized.kicad_pcb`, load the
   ratsnest (View > Show Ratsnest), and re-route each switch's two
   pads to their nets. Most are a short local hop back to the same
   row/column backbone that was already there.
2. Pay particular attention to the 37 switches below — their new pad
   position physically overlaps existing copper, so simply drawing a
   new trace to the pad isn't enough; the pre-existing trace segment
   it collides with needs to be nudged/rerouted too:
   `SW1, SW2, SW5, SW7, SW8, SW9, SW10, SW13, SW18, SW24, SW30, SW31,
   SW32, SW33, SW34, SW35, SW36, SW37, SW38, SW39, SW40, SW46, SW47,
   SW48, SW49, SW50, SW51, SW52, SW53, SW54, SW55, SW56, SW75, SW77,
   SW78, SW79, SW80`
3. Run `kicad-cli pcb drc` after routing and compare against
   `pcb/vendor/quanta75-bare-rp2040/` (the pristine upstream) as a
   baseline — the goal is to get back to (or below) the pre-swap error
   count (59 errors / 238 warnings), not to zero, since some of that
   baseline is pre-existing Quanta75 issues unrelated to this ticket.

## Not yet done (separate work, tracked elsewhere in this ticket)

- ISO Enter / backslash-row reshape to the K2 HE ANSI layout — needs
  new switches added/removed from the matrix (schematic + routing),
  not a same-position swap. Not started.
- Reset/flash-access mechanism (BOOTSEL/RESET buttons -> bare test
  pads). Not started.
- Spacebar stabilizer footprint: already stripped (separate commit,
  zero net impact) pending [Decision: stabilizers](https://github.com/bertrandvidal/stuff/issues/12).
