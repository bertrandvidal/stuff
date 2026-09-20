# alps75-zug firmware

QMK keyboard definition for the alps75-zug, with VIA support.

```
firmware/
├── keyboards/alps75_zug/
│   ├── keyboard.json                     matrix, pins, USB IDs, layout geometry
│   ├── readme.md                          QMK's per-keyboard readme
│   └── keymaps/
│       ├── default/keymap.c              base + Fn, plain QMK
│       └── zug/{keymap.c,rules.mk}       same keymap, VIA_ENABLE = yes
├── via/alps75-zug.json                   VIA v3 definition (sideload into usevia.app)
└── tools/
    ├── extract_matrix.py                 derives the matrix from the KiCad schematic
    ├── check_definition.py               asserts the definition still matches it
    └── link_into_qmk.sh                  symlinks this keyboard into your QMK clone
```

## Hardware summary

| | |
|---|---|
| MCU | Raspberry Pi Pico (RP2040), micro-USB, non-H |
| Matrix | 6 rows × 17 columns, 88 keys |
| Columns | `GP0`–`GP16` |
| Rows | `GP17`–`GP22` |
| Diodes | `COL2ROW` — column → switch → diode anode, cathode → row |
| USB | VID `0xFEED`, PID `0x5A47` |

The VID/PID pair is self-assigned. There is no registry for hobby boards; it
only has to be unique among the boards you own, and VIA uses it to match this
definition to the connected keyboard.

## Setup

QMK finds keyboards only under `$QMK_HOME/keyboards` — an *external userspace*
holds keymaps, not new keyboard definitions. So the definition lives here and is
symlinked into the QMK clone:

```sh
qmk setup                                  # clones qmk_firmware, installs the toolchain
sh tools/link_into_qmk.sh                  # symlink + lint
```

Everything the build produces — `.build/`, the `.uf2` — stays inside
`$QMK_HOME`. Nothing is written back into this repository.

## Build

```sh
qmk compile -kb alps75_zug -km zug         # VIA-enabled; or -km default
```

The keymap is called `zug` rather than `via` on purpose: `qmk lint` rejects any
keymap literally named `via` or `vial` (`lib/python/qmk/cli/lint.py`, upstream
keeps those out of the main tree). The name has no effect on the build — what
turns VIA on is `VIA_ENABLE = yes` in `keymaps/zug/rules.mk`.

## Flash

The case has **no BOOTSEL hole**, so there are two ways into the bootloader:

- **Fn + Esc** — `QK_BOOT` on layer 1. `Fn` is the 1u key right of the right
  Option, between it and the left arrow.
- **Hold Esc while plugging in** — Bootmagic, works even if the keymap is broken.

Either one mounts the Pico as `RPI-RP2`; copy the `.uf2` onto it.

Before the case is closed you can also press the physical BOOTSEL button through
the plate cutout. Once it is closed, you cannot — so if you flash a keymap that
removes both escape hatches above, getting back in means taking the case apart.

## VIA

`via/alps75-zug.json` is not part of the QMK build. To use it:

1. Flash the `zug` keymap.
2. Open <https://usevia.app>, go to Settings and enable **Show Design tab**.
3. In the **Design** tab, load `via/alps75-zug.json`.
4. The board appears under **Configure** and is remappable live.

The definition is sideloaded per browser profile; it is not uploaded anywhere.
Submitting it to [the-via/keyboards](https://github.com/the-via/keyboards) would
make it load automatically, but that is only worth doing if you share the design.

## Keeping it honest

`keyboard.json` and the VIA definition were generated from the schematic, not
typed by hand. To prove they still agree with it:

```sh
python3 tools/check_definition.py
```

It re-exports the netlist from `alps75-zug.kicad_sch` with `kicad-cli`, rebuilds
the matrix from scratch, and compares pins, diode direction, all 88 layout
entries, the VIA positions, and the keycode count in every layer. Run it after
any change to the schematic, the KLE layout or the definition. Requires
`kicad-cli` on `PATH` (KiCad 7+).

To see the derived matrix on its own:

```sh
python3 tools/extract_matrix.py [--json]
```

## Note on the F row

The 17 F-row keys carry `rotation_angle: -90` in the KLE layout: the *switches*
are rotated, as they are on the AEK/AEK II donor boards, so the plate cutouts and
PCB footprints are turned 90°. Each is still a 1u key rotated about its own
centre, so its position and size are unchanged and the firmware layout needs no
rotation of its own.

## Not yet verified

`qmk lint --strict` passes and both keymaps compile, but none of this has run on
hardware. Task 3.3 in `../tasks.md` is the first point where the pin mapping is
tested against a real board.
