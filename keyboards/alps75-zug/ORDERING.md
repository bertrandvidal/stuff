# alps75-zug v0.3 — ordering from JLC

Three orders, all under the same JLCPCB account, independent of each other (place them in parallel):

| What | Where | Upload |
| --- | --- | --- |
| PCB + 88 diodes assembled | [jlcpcb.com](https://jlcpcb.com) | `fab/alps75-zug-gerbers.zip`, then `fab/alps75-zug-bom-jlc.csv` + `fab/alps75-zug-cpl-jlc.csv` |
| Case: top frame + bottom case | [jlc3dp.com](https://jlc3dp.com) | `case/STL/case_top.stl`, `case/STL/case_bottom.stl` |
| Plate (1.2 mm sheet metal) | [jlccnc.com](https://jlccnc.com) — Sheet Metal | `case/STEP/plate.step` (+ `case/DXF/plate.dxf` as the 2D reference) |

v0.3 changes only the bottom case (3 mm of air under the PCB instead of 10). The PCB and the plate are the
v0.2 ones — the board's silkscreen says v0.2, which is correct.

## Before uploading — checked 2026-09-26

- **PCB:** `fab/export.sh` rerun on a copy of the board reproduces every committed gerber (only the
  creation-date lines differ), and the drill files, BOM and CPL byte for byte. DRC: 0 errors,
  0 unconnected, 0 schematic-parity issues, 4 cosmetic silkscreen warnings (see `fab/README.md`).
  If the board changes, rerun `fab/export.sh` first.
- **Case:** both STLs are one watertight solid each (0 non-manifold edges):
  top 349.96 × 169.17 × 8.20 mm, bottom 349.96 × 169.17 × 10.90 mm. After any change to
  `case/src/lib/case_geom.py`, rebuild with `case/src/export_stl.py` (see `case/src/README.md`).
- **Plate:** `plate.step` is one solid, 342.963 × 162.168 × 1.200 mm. Narrowest cutout: the 2.67 mm
  stabiliser slots (JLCCNC minimum: 1 mm); narrowest web: 1.88 mm, between the USB notch and the
  BOOTSEL cutout.

## 1. PCB + assembly — jlcpcb.com

1. **Order now → Add gerber file** → `fab/alps75-zug-gerbers.zip`. The viewer should show a
   328.01 × 147.22 mm board with the Pico tab top-left.
2. Base options: **2 layers, 1.6 mm, FR-4**. Colour and surface finish are free choices. Everything else
   as detected.
3. **PCB Assembly → on.** PCBA type **Economic** (limit 470 × 500 mm, the board fits),
   assembly side **Bottom**, quantity the minimum offered, **Confirm parts placement: yes**.
4. Upload **`fab/alps75-zug-bom-jlc.csv`** (BOM) and **`fab/alps75-zug-cpl-jlc.csv`** (CPL).
   Expect one line: 88 × 1N4148WL, LCSC C108804 (Extended part: one feeder fee).
   U1 (Pico) and the switches have no LCSC number, so they're left out — correct, you solder those.
5. In the placement preview, **check the diode polarity** on one of D1–D17 and one of D18–D88: the
   cathode band must sit on pad 1 (the bar on the B.Silk outline). Details in `fab/README.md`.
6. Approve the placement when JLCPCB asks (step 3's "confirm" option), before they solder.

## 2. Case — jlc3dp.com

1. **3D Printing → Upload** `case/STL/case_top.stl` and `case/STL/case_bottom.stl` (one part per file, mm).
2. **Process / material — recommended: MJF, PA12-HP nylon** (black if the dye option is offered).
   | Process | Fits 350 × 169 mm? | Heat-set inserts | Surface |
   | --- | --- | --- | --- |
   | **MJF PA12** | yes (max 370 × 276 mm) | yes, melt in well | fine grain, no support marks |
   | SLA resin | yes (max 780 × 780 mm) | **no** — resin doesn't melt; they'd have to be glued in | smoothest |
   | FDM ABS | yes (max 580 × 480 mm) | yes | visible layer lines; large flat parts warp |
   | SLS nylon | **no** — max 350 × 350 mm, 0.04 mm margin | — | — |
3. **Threaded-insert service: don't select it.** It needs ≥ 3 mm of wall around each insert and a flat
   ≥ 14 × 14 mm around it; the top-frame bosses have 2 mm (Ø8 around a Ø4 hole). Press the 10 inserts in
   yourself with a soldering iron (Ø4.0 × 5 mm holes, for M3 inserts ~4 mm long, OD 4.2–4.6).

## 3. Plate — jlccnc.com (Sheet Metal)

1. **Sheet Metal → Upload** `case/STEP/plate.step`; add `case/DXF/plate.dxf` as the 2D drawing if the
   form asks for one. Process: **laser cutting only**, no bends.
2. **Thickness 1.2 mm** (what `plate-88keys.jscad` is drawn for: Alps SKCM cutouts). Material — recommended: **stainless 304**,
   no finish needed and it won't rust. Alternatives: cold-rolled steel (SPCC) + powder coat, or
   aluminium 5052 (lighter, softer).
3. No kerf compensation is baked into the files — JLCCNC applies its own (cutting tolerance ± 0.1 mm).

## Risks to decide on before paying

- **Printed-case tolerance vs the metal plate.** JLC3DP quotes ± 0.4 % above 100 mm for nylon/FDM
  (± 0.3 % for resin): up to ± 1.4 mm over the case's 344 mm inner width. The plate has only 0.5 mm of
  clearance to the wall on each side, and its Ø3.2 holes (M3 screw, 335 mm apart) must line up with the
  printed bosses. Typical prints do better than the quoted limit, but it isn't guaranteed. Cheap
  insurance: enlarge the plate holes to Ø4.0 (plate-only change); or order the case first and measure
  it before ordering the plate.
- **"zug" engraving depth.** It's 0.6 mm deep; JLC3DP's minimum for engraved detail is 0.8 mm
  (resin/nylon) and 1.0 mm (FDM), so it may come out shallow or filled. `ENGRAVE_DEPTH = 1.0` in
  `case/src/lib/case_geom.py` fixes it (the panel is 3 mm thick).

## Not from JLC

Raspberry Pi Pico, 88 Alps SKCM / Matias switches, Alps AEK stabilisers, keycaps, 10 × M3 heat-set
inserts, 10 × M3 × 12 socket-head screws (ISO 4762), rubber feet, a micro-USB cable.

## Sources

[JLCPCB PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) ·
[JLC3DP design guidelines](https://jlc3dp.com/help/article/3d-printing-design-guideline) ·
[JLC3DP materials](https://jlc3dp.com/help/article/3d-printing-materials-choosing-guideline) ·
[JLC3DP threaded-insert service](https://jlc3dp.com/help/article/threaded-insert-service) ·
[JLCCNC sheet metal](https://jlccnc.com/sheet-metal-fabrication) ·
[JLCCNC sheet-metal ordering](https://jlccnc.com/help/article/how-to-place-a-sheet-metal-order)
