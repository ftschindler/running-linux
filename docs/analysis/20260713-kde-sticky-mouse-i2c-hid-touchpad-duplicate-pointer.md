---
title: Sticky Mouse on KDE — I2C-HID Touchpad Exposing a Duplicate Pointer
---

**Context** – On a Dell laptop running KDE Plasma on Manjaro (LUKS + LVM, X11 session), the pointer felt _sticky_: it snapped, stalled then jumped, particularly whilst using the built-in touchpad. A `plasmashell --replace` did **not** help. This entry records the investigation and the confirmed root cause. The fix applied as a result is documented separately in [Fix Sticky Mouse — Suppress Duplicate Touchpad Pointer](../done/20260713-kde-sticky-mouse-i2c-hid-touchpad-duplicate-pointer.md).

- **Hardware**: Dell laptop, I2C-HID touchpad `VEN_0488:00 0488:1031`, Wacom HID digitiser, internal i8042 controller
- **Session**: X11 (`kwin_x11`), KDE Plasma
- **Date**: 2026-07-13
- **Method**: Kernel input enumeration (`/proc/bus/input/devices`, `/proc/interrupts`), `journalctl` boot-log analysis, `xinput`, `libinput list-devices`, `libinput quirks list`, `udevadm`, plus pressure/governor checks to exclude load-related causes.

## Verdict

The single physical touchpad is exposed to the input stack as **two competing pointer devices** — the correct absolute _Touchpad_ **and** a spurious relative _Mouse_ interface on the same hardware. libinput feeds **both** into the X11 core pointer, so every finger movement is interpreted twice (once as an absolute position, once as a relative delta). Those two interpretations collide on each HID packet, which is felt as _sticking_, snapping and stall-then-jump.

The fault sits in the **kernel HID → libinput** layer, well below Plasma. That is precisely why `plasmashell --replace` (which only restarts the panel and desktop shell, not the compositor or the pointer pipeline) had no effect. It is boot-deterministic and reproduces from a clean standalone boot, with no dock and no suspend involved.

## Why `plasmashell --replace` was never going to work

The pointer pipeline on X11 is:

```text
kernel HID (evdev)  →  libinput  →  xf86-input-libinput  →  X server  →  kwin_x11  →  applications
```

`plasmashell` is the **panel and desktop shell** only. It does not sit anywhere on that path. Restarting it cannot change how a duplicated evdev device is arbitrated. The relevant layers here are the kernel HID driver and libinput.

## The decisive evidence

### One physical device, two pointer nodes

Both the bogus _Mouse_ and the real _Touchpad_ share the **same libinput device group and the same bus id**, which proves they are the same physical hardware:

| libinput device | evdev node | Capabilities | Verdict |
| --- | --- | --- | --- |
| `VEN_0488:00 0488:1031 Mouse` | `event8` | `pointer` (relative) | **Spurious** — redundant relative interface |
| `VEN_0488:00 0488:1031 Touchpad` | `event9` | `pointer gesture` (absolute, 101×61 mm, tap, two-finger scroll) | **Correct** touchpad |
| `PS/2 Generic Mouse` | `event12` | `pointer` (relative) | **Phantom** on the i8042 AUX port |

Both `VEN_0488` nodes report `Id: i2c:0488:1031` and `Group: 6` under `libinput list-devices` — same device, two faces.

### The udev tags disagree on the same hardware

```text
event8  →  ID_INPUT_MOUSE=1
event9  →  ID_INPUT_TOUCHPAD=1 , ID_INPUT_TOUCHPAD_INTEGRATION=internal , 100×61 mm
```

The kernel is tagging one interface of the touchpad as a plain mouse. `xinput list` confirms **both** are attached to the _Virtual core pointer_ as active slaves.

### The driver rebind that creates the extra node

At boot the device is probed twice, ~300 ms apart, with a driver swap in between:

```text
21:22:14.414  hid-generic    0018:0488:1031.0001 ... Mouse   (first bind → input9/input10)
21:22:14.679  input re-created                              (input21/input22)
21:22:14.720  hid-multitouch 0018:0488:1031.0001 ... Mouse   (rebind, now current)
```

The device advertises itself as a generic _Mouse_, gets an initial `hid-generic` bind, then `hid-multitouch` takes over. The current driver is `hid-multitouch`, but the redundant relative _Mouse_ interface survives alongside the proper absolute touchpad.

## What was ruled out

Each of these was checked and excluded, so the diagnosis does not chase ghosts:

- **CPU / IO starvation** — `/proc/pressure/cpu` flat at `0.00`, IO pressure negligible, governor `schedutil`. Not a load problem.
- **IRQ storm** — touchpad IRQ (`VEN_0488` on `intel-gpio`) and `i2c_designware.1` interrupt counts are normal, not runaway.
- **Bluetooth** — the `hci0: Received unexpected HCI Event 0x00` messages fired only 64× in a 2 ms burst at boot then stopped; no Bluetooth mouse is connected. Cosmetic, unrelated.
- **Compositor tearing** — `kwin_x11` `BadDamage` / `BadWindow` XCB errors are benign X11 churn, not pointer input.
- **Dock / suspend race** — for the reproducing session there was **no** suspend, hibernate or dock event (continuous uptime, no `PM: suspend entry`, no USB mouse connect/disconnect). The only `hibernation` log lines were routine boot-time nosave-memory registration. The fault is present on a clean standalone boot.
- **Phantom PS/2 mouse as an external leftover** — the `PS/2 Generic Mouse` on `event12` is present from cold boot on the internal i8042 AUX port (where Dell's touchpad PS/2 emulation and WMI hooks also live), not a residue of a disconnected external mouse. When idle it emits no events, so it is a secondary suspect at most, not the primary cause.

## Fix

The applied fix — a surgical libinput quirk that suppresses the spurious relative interface whilst leaving the real touchpad untouched — is documented in [Fix Sticky Mouse — Suppress Duplicate Touchpad Pointer](../done/20260713-kde-sticky-mouse-i2c-hid-touchpad-duplicate-pointer.md).

### Note for the dock + suspend workflow

Although this occurrence reproduces on a clean boot, I2C-HID touchpads on this class of hardware are also prone to a **second, resume-time failure mode**: on resume or re-dock the pad can fail to re-probe or return on the wrong driver, and X11 does not always re-run device matching. If sticking is ever noticeably worse specifically after undocking or resume, capture the resume-time logs and compare against the clean-boot baseline recorded here — that would be a distinct fault stacked on top of this one.
