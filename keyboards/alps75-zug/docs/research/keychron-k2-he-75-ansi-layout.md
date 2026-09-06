# Research: Keychron K2 HE 75% ANSI layout as KLE source of truth

Resolves [issue #15](https://github.com/bertrandvidal/stuff/issues/15) (part of the
[Wayfinder map, #7](https://github.com/bertrandvidal/stuff/issues/7)).

## Primary source

Keychron does not publish a keyboard-layout-editor.com link for the K2 HE, and no
community KLE preset for it turned up on kle.klava.org's default gallery or in web
search. The highest-trust source is **Keychron's own open-source QMK firmware repo**,
which encodes the physical key layout as x/y/w/h coordinates (the same data model KLE
uses) per-key, keyed to the physical switch matrix:

- Physical layout (coordinates/sizes):
  [`keyboards/keychron/k2_he/ansi/keyboard.json`](https://github.com/Keychron/qmk_firmware/blob/2025q3/keyboards/keychron/k2_he/ansi/keyboard.json)
  (`LAYOUT_ansi_84`), repo `Keychron/qmk_firmware`, ref `2025q3`.
- Legends (which key is which): the `WIN_BASE` layer of
  [`keyboards/keychron/k2_he/ansi/keymaps/default/keymap.c`](https://github.com/Keychron/qmk_firmware/blob/2025q3/keyboards/keychron/k2_he/ansi/keymaps/default/keymap.c),
  mapped onto the matrix positions from the file above.
- Corroboration: Keychron's own firmware readme calls the K2 HE "*a customizable 84
  keys TKL hall effect keyboard*"
  ([readme.md](https://github.com/Keychron/qmk_firmware/blob/2025q3/keyboards/keychron/k2_he/readme.md)) —
  note the internal wording says "TKL" while the [product page](https://www.keychron.com/products/keychron-k2-he-wireless-magnetic-switch-keyboard)
  markets it as "75% Compact"; both describe the same 84-key board, this is just loose
  Keychron terminology, not a layout discrepancy.
- General "true 75%" convention background: [Deskthority Nav cluster wiki](https://deskthority.net/wiki/Nav_cluster)
  and community write-ups, used only to compare against, not as ground truth for the
  K2 HE itself.

A reconstructed KLE-importable JSON built directly from the QMK source data (coordinates
transcribed verbatim, legends filled in from the keymap) is checked in alongside this
file: [`keychron-k2-he-84-ansi.kle.json`](./keychron-k2-he-84-ansi.kle.json). Paste its
contents into keyboard-layout-editor.com ("Raw data" tab or upload as JSON) to visualize
or edit it.

## Confirmed facts

- **Total key count: 84**, ANSI physical layout, US QWERTY. Verified by summing the
  `LAYOUT_ansi_84` matrix entries (16+15+15+14+14+10 = 84) and cross-checked against
  Keychron's own "84 keys" wording in the firmware readme and product listings.
- **Row-by-row layout** (row := one `y` value in the source data; sizes in key units,
  `u`):

  | Row | Keys (left→right) | Notable sizes |
  |---|---|---|
  | 0 (top) | Esc, F1–F12, PrtSc, Del, **RGB** | all 1u, evenly spaced, **no gaps** |
  | 1 (number row) | `` ` ``,1–0,-,=, Backspace, PgUp | Backspace = 2u |
  | 2 (QWERTY row) | Tab, Q–P, [, ], \\, PgDn | Tab = 1.5u, \\ = 1.5u |
  | 3 (home row) | Caps, A–L, ;, ', Enter, Home | Caps = 1.75u, Enter = 2.25u |
  | 4 (bottom letter row) | Shift, Z–/, Shift, ↑, End | LShift = 2.25u, **RShift = 1.75u** |
  | 5 (bottom row) | Ctrl, Win, Alt, Space, Alt, Fn, Ctrl, ←, ↓, → | see ANSI bottom row spec below |

- **ANSI bottom row spec** (row 5, left→right, widths in `u`):
  `1.25 Ctrl · 1.25 Win · 1.25 Alt · 6.25 Space · 1 Alt · 1 Fn · 1 Ctrl · 1 Left · 1 Down · 1 Right`
  Total width = 3.75 + 6.25 + 6 = 16u, matching the 16u width of every other row.
  **This is not the generic full-size-ANSI bottom row** (which commonly uses
  1.25u for all six modifier positions plus a Menu key); the K2 HE compresses the
  three right-hand bottom-row keys (Alt/Fn/Ctrl) to 1u each and drops the Menu/context
  key entirely, using that saved space to fold the Left/Down/Right arrow keys directly
  into the same row with **zero gap** between Ctrl and Left.
- **Function row spacing**: evenly spaced, no physical gaps (no TKL-style break after
  F4/F8, no gap before PrtSc/Del). This matches the generic "true 75%" convention —
  75% layouts are defined by *not* having the TKL gaps, so no ambiguity here.
- **Arrow cluster treatment**: inverted-T, but *integrated* rather than visually
  separated — Up sits alone in row 4 (aligned above Down), Left/Down/Right sit in row 5.
  All three bottom-row arrow keys are flush (zero gap) against the Ctrl/Fn/Alt block to
  their left, and Up is flush against RShift. This matches the general 75%-convention
  "arrows fused into the main block" description, but the *zero-gap flush* fit is a
  specific choice — some 75% boards/community KLE templates leave a small visual gap
  between the main cluster and the nav column; the K2 HE's real coordinates have none.
- **Right-side navigation column**: a **single stacked column** at the rightmost
  position (x = 15u) — Del (row 0), PgUp (row 1), PgDn (row 2), Home (row 3), End
  (row 4) — one nav key per main-cluster row, 5 keys total, **not** a 2-column /
  2×3 Ins-Home-PgUp / Del-End-PgDn block. There is no dedicated Insert key. This
  matches the common 65%/75% single-column nav convention described on Deskthority,
  so it's consistent with "true 75%" — but it's worth flagging explicitly since some
  true-75% KLE templates do use the 2-column block instead, and that would change the
  PCB's key count/positions in that region if picked from a generic template instead
  of this K2 HE-specific data.

## Ambiguities to flag as decisions

1. **Top-right key (row 0, rightmost, matrix `[0,15]`) is a dedicated RGB/backlight
   toggle** on the K2 HE (mapped to `UG_NEXT` in both the Mac and Windows base layers —
   i.e. it's a fixed hardware function key, not remappable via layers). This build has
   no RGB (vintage Alps switches, no per-key LEDs), so this position needs a decision:
   repurpose as an ordinary keycode (e.g. a second Fn/media key), or keep as a spacer/
   non-functional key with a blank or custom-legend cap. Not a PCB-layout ambiguity
   (the physical footprint is unaffected either way) but affects keymap/legend choice.
2. **Zero-gap fit vs. generic templates with a small nav-column gap.** If the plate/PCB
   design is cross-checked against a generic "true 75%" KLE template pulled from the
   community rather than built from this file, double check it doesn't introduce a gap
   between the main block and the right-hand nav column / arrow cluster that the real
   K2 HE doesn't have — it would throw off stabilizer and switch-cutout positions by a
   few mm at the board's right edge.
3. **Bottom-row right-hand mod keys are 1u, not 1.25u.** If keycap sourcing assumes a
   "standard" bottom row, the right-hand Alt/Fn/Ctrl trio (and the fact there's no Menu
   key) needs explicit confirmation against this spec, since it deviates from common
   full-size-ANSI (and some generic-75%) bottom-row assumptions.

None of these block PCB/plate design — the KLE file's coordinates are unambiguous and
sufficient as source of truth for the physical footprint. Items 1 and 3 are keymap/
keycap-legend decisions, not physical-layout decisions, and can be resolved later
without reopening this ticket.

## Files

- Findings: `keyboards/alps75-zug/docs/research/keychron-k2-he-75-ansi-layout.md` (this file)
- KLE layout: `keyboards/alps75-zug/docs/research/keychron-k2-he-84-ansi.kle.json`
