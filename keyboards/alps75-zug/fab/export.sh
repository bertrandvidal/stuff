#!/bin/bash
# Regenerate the fab outputs from alps75-zug.kicad_pcb. See README.md.
set -euo pipefail

cd "$(dirname "$0")"
PCB="../alps75-zug.kicad_pcb"
OUT="gerbers"
ZIP="alps75-zug-gerbers.zip"

rm -rf "$OUT" "$ZIP" ./*-drl_map.gbr
mkdir -p "$OUT"

kicad-cli pcb export gerbers \
  --output "$OUT" \
  --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --no-protel-ext \
  --check-zones \
  "$PCB"

kicad-cli pcb export drill \
  --output "$OUT" \
  --format excellon \
  --drill-origin absolute \
  --excellon-units mm \
  --excellon-zeros-format decimal \
  --excellon-separate-th \
  --generate-map --map-format gerberx2 \
  --generate-report --report-path drill-report.txt \
  "$PCB"

kicad-cli pcb drc --severity-error --severity-warning \
  --format json --output drc.json "$PCB"

# Drill maps are for humans, not for the fab: keep them out of the zip.
mv "$OUT"/*-drl_map.gbr .

# Flat archive root — that is what the fabs expect.
( cd "$OUT" && zip -X -r "../$ZIP" . -x '.*' )

echo
echo "Wrote $ZIP:"
unzip -l "$ZIP"
