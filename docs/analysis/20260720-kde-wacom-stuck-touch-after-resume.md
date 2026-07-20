---
title: Stuck Touchscreen Touch After Resume — Phantom Drag Masquerading as a Sticky Mouse
---

**Context** – On the same Dell laptop (KDE Plasma on Manjaro, LUKS + LVM, X11 session) a "sticky mouse" symptom recurred after a suspend/resume cycle. It presented like the earlier [duplicate-pointer touchpad bug](20260713-kde-sticky-mouse-i2c-hid-touchpad-duplicate-pointer.md), but was a **completely different fault**: the Wacom touchscreen digitiser returned from `s2idle` with `BTN_TOUCH` latched down, so the desktop behaved as if a finger were permanently held on the screen. The fix is documented in [Fix Stuck Touchscreen Touch After Resume](../done/20260720-kde-wacom-stuck-touch-after-resume.md).

- **Hardware**: Wacom HID digitiser `WACF3233:00 056A:49BB` (i2c-hid, driver `wacom`), Dell laptop
- **Session**: X11 (`kwin_x11`), KDE Plasma, Intel Iris Xe (`i915`)
- **Date**: 2026-07-20
- **Method**: Layer-split input diagnosis — `libinput debug-events` timing, `xinput`, `evtest --query` for physical button state, `journalctl` resume-log analysis, plus two Oracle consultations.

## Verdict

The symptom was **not** a sticky or laggy pointer at all — it was a **stuck mouse button**. The `Wacom HID 49BB Finger` device was latched reporting `BTN_TOUCH` permanently down, which the desktop interpreted as an endless click-and-drag. Rebinding the Wacom HID device cleared the phantom touch and resolved every symptom. The latch occurred across an `s2idle` resume, which is why it returned after suspend and why `plasmashell --replace` never helped — the fault was in kernel HID device state, not the shell.

## The misleading trail (and why the symptom description cracked it)

The recurrence was initially chased as a pointer-motion problem, which led nowhere because every mechanical layer tested clean:

- The earlier duplicate-pointer fix was still intact: the spurious relative `Mouse` node (`event8`) was silenced (`Send Events Mode Enabled: 0, 0`), and only the real touchpad emitted during motion.
- No touchpad re-probe at resume; i2c-hid IRQs advancing normally.
- CPU/IO pressure flat `0.00`, CPU frequency healthy, compositor active, `i915` resumed cleanly with no GPU hang or software-cursor fallback.
- An apparent "2-second freeze" in `libinput debug-events` timing turned out to be a **measurement artifact** — the large inter-event gaps were finger lifts between strokes, not real stalls. In-stroke motion was smooth (218 of 231 gaps under 16 ms).

The breakthrough was the **user's description of the actual behaviour** rather than any timing metric:

- The cursor was **invisible** while moving over a terminal window, becoming visible only at window borders and the panel.
- Continuous motion in a GUI **selected a body of text that followed the pointer**.
- Widget popups in the panel **would not dismiss on click**.

Every one of these is the signature of a **held mouse button**, not a laggy pointer: invisible cursor because a drag is "in progress", motion-selects-text because button-plus-motion is a drag-select, and clicks that don't dismiss because a phantom button-down breaks click handling.

## The decisive evidence

Physical button state was queried per device with `evtest --query`, which reports whether a key/button bit is currently set:

```text
event8  VEN_0488 Mouse     BTN_LEFT  → up
event9  VEN_0488 Touchpad  BTN_LEFT  → up
event12 PS/2 Generic Mouse BTN_LEFT  → up
event11 Wacom HID 49BB Finger  BTN_TOUCH → DOWN/held   ← stuck
```

`evtest --query /dev/input/event11 EV_KEY BTN_TOUCH` returned exit code `10` (bit set / held). The device behind it:

```text
hid: 0018:056A:49BB.0002   driver = wacom
```

## Fix

Rebinding the Wacom HID device resets its state and clears the latched touch:

```bash
echo -n "0018:056A:49BB.0002" | sudo tee /sys/bus/hid/drivers/wacom/unbind
sleep 1
echo -n "0018:056A:49BB.0002" | sudo tee /sys/bus/hid/drivers/wacom/bind
```

After the rebind, `evtest --query` returned exit `0` (touch up) and all symptoms cleared. Because the latch is resume-triggered, the durable fix is a `systemd` `system-sleep` hook that rebinds the device on every resume — see [the fix entry](../done/20260720-kde-wacom-stuck-touch-after-resume.md).

## Relationship to the earlier touchpad bug

These are two independent faults that produce a superficially similar "sticky mouse" complaint on the same machine:

- The [duplicate-pointer touchpad bug](20260713-kde-sticky-mouse-i2c-hid-touchpad-duplicate-pointer.md) is a genuine dual-pointer arbitration problem, fixed with a libinput quirk. That fix remains correct and in place.
- This stuck-touch bug is a resume-time HID state latch on the Wacom digitiser, unrelated to the touchpad.

The lesson: when a "sticky mouse" survives the obvious pointer-layer fixes, check the **physical button state of every input device** (`evtest --query`) — including the touchscreen — before assuming the problem is pointer motion.
