# Provenance / attribution

This PCB is a derivative work built from two upstream sources, vendored
unmodified under `pcb/vendor/` and adapted under `pcb/board/`.

## Quanta75 (Bare RP2040, JLCPCBA-optimized variant)

- Source: https://github.com/obsilab/Quanta75
- Variant: `Quanta75_BareRP2040_JLCPCBAoptimized`
- Snapshot: commit `fe45630787dce4ec154e6826bf268d4de40ce11b` (2024-05-28)
- License: CERN Open Hardware Licence v2 - Permissive (CERN-OHL-P-2.0),
  full text at `pcb/vendor/quanta75-bare-rp2040/LICENSE`
- Chosen per [Decision: PCB base approach](https://github.com/bertrandvidal/stuff/issues/10)

Kept intact from upstream: the RP2040 chip-down subsystem (QFN-56 RP2040,
external QSPI flash, 12MHz crystal, 3.3V LDO) and its LCSC/JLCPCB part
sourcing. Adapted: switch footprints (Alps, see below), the ISO-specific
rows reshaped to 75% ANSI, and the reset/flash-access circuit. See
[Task: fork Quanta75 bare-RP2040 PCB and adapt to Alps 75% ANSI layout](https://github.com/bertrandvidal/stuff/issues/24)
for the full change set.

## ai03 MX_V2 — Alps_Solderable.pretty

- Source: https://github.com/ai03-2725/MX_V2
- Library: `Alps_Solderable.pretty`
- License: MIT, full text at `pcb/vendor/ai03-alps-solderable/LICENSE`
- Confirmed as the correct footprint family for SKCM Alps switches by
  [Manta75 + ai03 Alps footprints + onboard RP2040 feasibility](https://github.com/bertrandvidal/stuff/issues/14)

Used solder-in (no Alps hotswap footprint exists in this or any ai03
library) — matches the plan to hand-solder salvaged vintage SKCM switches.
