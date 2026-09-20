# alps75-zug

A 75% Alps-mount keyboard built around a Raspberry Pi Pico, designed to be
rebuilt from an Apple Extended Keyboard II: AEK switches, AEK caps and AEK
plate-mount stabilisers on a new PCB, plate and 3D-printed case.

* Keyboard Maintainer: [bertrandvidal](https://github.com/bertrandvidal)
* Hardware Supported: alps75-zug PCB rev 0.1, Raspberry Pi Pico (RP2040), micro-USB
* Hardware Availability: self-built, see the project repository

88 keys on a 6 × 17 matrix. Columns `GP0`–`GP16`, rows `GP17`–`GP22`, `COL2ROW`.

Make example for this keyboard (after setting up your build environment):

    make alps75_zug:default

Flashing example for this keyboard:

    make alps75_zug:default:flash

See the [build environment setup](https://docs.qmk.fm/#/getting_started_build_tools)
and the [make instructions](https://docs.qmk.fm/#/getting_started_make_guide) for
more information. Brand new to QMK? Start with our
[Complete Newbs Guide](https://docs.qmk.fm/#/newbs).

## Bootloader

The case has no BOOTSEL hole, so there are three ways into the RP2040 bootloader,
in descending order of convenience:

* **Fn + Esc** — `QK_BOOT` on layer 1. `Fn` is the 1u key to the right of the
  right Option.
* **Hold Esc while plugging in** — Bootmagic. Works even if the keymap is broken.
* **The physical BOOTSEL button** — reachable through the plate cutout, but only
  with the case open.

Keep at least one of the first two in any keymap you flash.
