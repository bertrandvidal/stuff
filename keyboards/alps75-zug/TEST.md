# Pico multimeter checks

Use this when the Pico doesn't show up on the computer (no `RPI-RP2` drive, nothing in System Information → USB).
Run it on **both** boards:

- **Loose board:** the Pico that isn't soldered to anything. It is your reference.
- **Soldered board:** the Pico soldered to the PCB.

If a check fails on the loose board, the Pico itself is bad. If it passes on the loose board but fails on the soldered one, the problem is the soldering.

## Try this first: cable, port and BOOTSEL

On this project the cause was never the Pico or the soldering. The USB-C clone Picos (Shutao RP2040, USB-C) have no CC resistors, and it took a cable and port change to get them to enumerate. Before you pick up the meter:

1. **Use a USB-A to USB-C cable**, not C-to-C. Without CC resistors on the Pico, a C-to-C cable gets 0 V on VBUS.
2. **Make sure the cable carries data.** Some cables are charge-only. Check the whole chain (laptop, hub, cable) with a phone: unlock it, set USB to "File transfer", and look for it in System Information (hold Option, click the Apple menu, System Information → USB). If the phone is listed, the chain carries data.
3. **Try different hub ports.** On this setup the Pico only appeared in a hub's USB 3 port. If it doesn't show up, try the other ports.
4. **Hold BOOTSEL while plugging in** (the white button), keep holding for about 2 seconds, then release. "RP2 Boot" should appear in System Information → USB and an `RPI-RP2` drive in Finder.

If the Pico still doesn't appear, continue with the meter checks below.

## Before you start

Meter settings:
- **Continuity** is the mode that beeps. **Resistance** is the Ω mode. **DC volts** is V with a straight line.
- Black probe on a GND pin, red probe on the pin you test.

Pin numbers (Pico seen from above, USB connector at the top):

```
          USB
  1  GP0       VBUS 40
  2  GP1       VSYS 39
  3  GND       GND  38
  4  GP2       3V3_EN 37
  5  GP3       3V3  36
  6  GP4       ADC_VREF 35
  7  GP5       GP28 34
  8  GND       AGND 33
  9  GP6       GP27 32
 10  GP7       GP26 31
 11  GP8       RUN  30
 12  GP9       GP22 29
 13  GND       GND  28
 14  GP10      GP21 27
 15  GP11      GP20 26
 16  GP12      GP19 25
 17  GP13      GP18 24
 18  GND       GND  23
 19  GP14      GP17 22
 20  GP15      GP16 21
```

Pin 1 is top left. Count down the left side, then up the right side. GND pins are 3, 8, 13, 18, 23, 28 and 38. Use any of them as your GND.

If the Pico is soldered to the PCB, probe the pad or pin at the Pico's edge, not the board's traces.

## Part 1: USB unplugged

Unplug the Pico from USB first. Keep the red probe on the pin and the black probe on GND. Use continuity mode (or Ω mode) for steps 1–7.

### 1. VBUS to GND (pin 40 to pin 38)
- **Do:** continuity mode, probes on pin 40 and pin 38.
- **Expect:** no beep. In Ω mode the reading starts low and climbs, or shows "OL" (open).
- **Fail:** a steady beep or ~0 Ω. VBUS is shorted to GND, which is why the USB port shuts down. On the soldered board, look for a solder bridge on pins 38–40.

### 2. 3V3 to GND (pin 36 to pin 38)
- **Do:** same as step 1 with pin 36.
- **Expect:** no beep.
- **Fail:** a beep means a short. Look for a bridge on pins 35–38.

### 3. 3V3_EN to GND (pin 37 to pin 38)
- **Do:** same, with pin 37.
- **Expect:** no beep. This pin is not used on the PCB.
- **Fail:** a beep means 3V3_EN is held low, so the regulator is off and the board never powers up. Pins 37 and 38 are adjacent, so look for a bridge between them.

### 4. RUN to GND (pin 30 to pin 28)
- **Do:** same, with pin 30.
- **Expect:** no beep.
- **Fail:** a beep means the chip is held in reset and stays dead.

### 5. VSYS to GND (pin 39 to pin 38)
- **Do:** same, with pin 39.
- **Expect:** no beep.
- **Fail:** a beep means a short on the power rail.

### 6. Pin to neighbour: bridges (soldered board only)
- **Do:** continuity mode. Touch each pair of **adjacent** pins on the Pico's edge, for example 1 and 2, 2 and 3, and so on down both sides.
- **Expect:** no beep for any pair. Skip the matrix lines if switches are installed, since GND pins stay separate from signal pins either way.
- **Fail:** a beep means a solder bridge between those two pads. Fix it with flux and solder wick, then repeat the check.

### 7. Each GP pin to GND (soldered board only)
- **Do:** continuity mode, black probe on GND, red probe on each of GP0–GP22 in turn (pins 1, 2, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25, 26, 27, 29).
- **Expect:** no beep for every pin, **if no switches are installed**. With switches installed, a pin may only conduct through a diode, so skip this step then.
- **Fail:** a beep means that pin is shorted to GND, either by a bridge or by a bad diode or via.

## Part 2: USB plugged in

Plug the Pico in with a USB-A to USB-C cable that you know carries data (see "Try this first"). Don't hold BOOTSEL for these voltage checks.

**Switch the meter to DC volts for steps 8–11** (V with a straight line, V⎓ or DCV). Do not use continuity or Ω mode on a powered board. On a manual-range meter, pick the 20 V range; an auto-ranging meter needs no setting. Black probe on GND (pin 38).

### 8. VBUS (pin 40)
- **Meter:** DC volts.
- **Do:** red probe on pin 40.
- **Expect:** about **5 V** (4.7–5.3 V).
- **Fail, ~0 V:** no power is reaching the board. The most likely cause is a USB-C-to-USB-C cable: the clone has no CC resistors, so use an A-to-C cable. Otherwise it's a bad cable or a broken connector. On the soldered board, go back to step 1.

### 9. VSYS (pin 39)
- **Meter:** DC volts.
- **Do:** red probe on pin 39.
- **Expect:** about **4.7–5 V**, a bit below VBUS.
- **Fail:** ~0 V with VBUS fine means the power diode or the connection after VBUS is bad.

### 10. 3V3 (pin 36)
- **Meter:** DC volts.
- **Do:** red probe on pin 36.
- **Expect:** about **3.3 V** (3.2–3.4 V).
- **Fail, ~0 V with VBUS and VSYS fine:** the regulator is off or dead. Check 3V3_EN again (step 3) or the board is faulty.

### 11. RUN (pin 30)
- **Meter:** DC volts.
- **Do:** red probe on pin 30.
- **Expect:** about **3.3 V**, pulled up.
- **Fail, ~0 V:** the chip is held in reset. Check step 4.

## Part 3: What the results mean

| Result | Meaning | Next step |
| --- | --- | --- |
| Power is fine (steps 8–11) but the Pico doesn't enumerate | Data path or BOOTSEL, not power | Go through "Try this first": data cable, other hub port, hold BOOTSEL |
| Loose board passes everything but still doesn't enumerate with BOOTSEL held on a known data chain | Bad chip, bad crystal or bad flash on a clone | Try a genuine Pico |
| Loose board fails step 8 | No power from the cable or connector | Use an A-to-C cable (C-to-C gives 0 V on these clones), or try a genuine Pico |
| Loose board fails step 10 | Dead regulator | Replace the Pico |
| Soldered board fails steps 1–7 | Solder bridge | Reflow with flux and solder wick, repeat |
| Soldered board passes steps 1–11 but doesn't enumerate | Same as the loose board's result | Likely the Pico, not the soldering |

Write down the readings for each step and bring them back, even for passing steps. Then I can narrow it down.
