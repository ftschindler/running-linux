---
title: Fix Sticky Mouse — Suppress Duplicate Touchpad Pointer
---

- **Context:** Dell laptop, KDE Plasma on Manjaro (LUKS + LVM, X11 session), I2C-HID touchpad `VEN_0488:00 0488:1031`

## Problem

The pointer felt _sticky_ — snapping, stalling then jumping, mostly whilst using the built-in touchpad. A `plasmashell --replace` made no difference.

Root cause: the single physical touchpad is exposed to libinput as **two competing pointer devices** — the correct absolute _Touchpad_ (`event9`) and a spurious relative _Mouse_ interface (`event8`) on the same hardware — so every finger movement is interpreted twice and the two readings collide. Full diagnosis in [Sticky Mouse on KDE — I2C-HID Touchpad Exposing a Duplicate Pointer](../analysis/20260713-kde-sticky-mouse-i2c-hid-touchpad-duplicate-pointer.md).

## Solution

Suppress the spurious relative interface with a libinput quirk, keeping the correct touchpad. **No extra packages are required** — the quirk engine ships in the base `libinput` package, already installed as a KDE/X11 dependency. (`libinput-tools` and `xorg-xinput` are only needed for the `libinput`/`xinput` diagnostic commands, not for the fix itself.)

Create `/etc/libinput/local-overrides.quirks`:

```ini
[Dell VEN_0488:1031 duplicate relative pointer]
MatchName=VEN_0488:00 0488:1031 Mouse
MatchUdevType=mouse
MatchBus=i2c
MatchVendor=0x0488
MatchProduct=0x1031
AttrEventCode=-REL_X;-REL_Y
```

This matches only the bogus relative `Mouse` node (`event8`) — not the real `Touchpad` (`event9`), which is `MatchUdevType=touchpad` — and strips its relative motion codes so libinput stops treating it as a pointer. The touchpad and its gestures are untouched.

### Verification

```bash
# Confirm the quirk is picked up (should list the property override for event8)
sudo libinput quirks list /dev/input/event8

# Touch the pad and confirm a SINGLE device emits, not two
sudo libinput debug-events
```

Then log out and back in (or restart the X server) so `xf86-input-libinput` re-reads the quirk, and confirm the sticking is gone. Revert by deleting the file.

If the phantom `PS/2 Generic Mouse` (`event12`) ever injects motion (check with `sudo libinput debug-events --device /dev/input/event12` whilst not touching the pad), disable it too — blacklist `psmouse` if no genuine PS/2 device is ever attached.
