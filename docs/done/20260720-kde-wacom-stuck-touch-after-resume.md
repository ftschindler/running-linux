---
title: Fix Stuck Touchscreen Touch After Resume
---

- **Context:** Dell laptop, KDE Plasma on Manjaro (LUKS + LVM, X11 session), Wacom HID digitiser `WACF3233:00 056A:49BB` (i2c-hid, driver `wacom`)

## Problem

After a suspend/resume (`s2idle`) cycle, a "sticky mouse" symptom appeared: the cursor was invisible while moving over windows, continuous motion selected text that followed the pointer, and panel popups would not dismiss on click. A `plasmashell --replace` made no difference.

Root cause: the Wacom touchscreen returned from resume with `BTN_TOUCH` **latched down**, so the desktop behaved as if a finger were permanently held on the screen — an endless click-and-drag, not a laggy pointer. Full diagnosis in [Stuck Touchscreen Touch After Resume](../analysis/20260720-kde-wacom-stuck-touch-after-resume.md).

The symptom description was what cracked it: an invisible cursor, motion that selects text and clicks that never dismiss are all the signature of a **held mouse button**, not a laggy pointer. `evtest --query` on every input device then pinned it to the Wacom Finger node:

```text
event11 Wacom HID 49BB Finger  BTN_TOUCH → held (evtest --query exit 10)
hid device: 0018:056A:49BB.0002   driver = wacom
```

### Other paths investigated (all dead ends)

Before the button-state check, several pointer-motion hypotheses were explored and excluded — recorded here so the same ground is not covered twice:

- **Duplicate touchpad pointer** — the earlier [dual-pointer bug](../analysis/20260713-kde-sticky-mouse-i2c-hid-touchpad-duplicate-pointer.md) was still fixed; only the real touchpad emitted.
- **libinput motion jitter** — an apparent 2 s freeze was a measurement artifact (finger lifts between strokes); in-stroke motion was smooth (218/231 gaps under 16 ms).
- **i2c-designware runtime PM** — forcing the touchpad bus `control=on` changed nothing; reverted.
- **CPU / IO starvation** — pressure flat `0.00`, CPU frequency healthy.
- **GPU / compositor** — `i915` resumed cleanly, compositor active, `BadDamage` errors actually dropped after resume.
- **Dock-attached mouse** — the `typec` resume event attached no external pointer.

## Solution

Rebind the Wacom HID device to reset its state and clear the latched touch. **No extra packages are required** for the fix itself; `evtest` (from the `evtest` package) is only needed for the diagnostic query and the "only rebind if stuck" guard in the resume hook.

### 1. Immediate clear (no reboot, no logout)

```bash
echo -n "0018:056A:49BB.0002" | sudo tee /sys/bus/hid/drivers/wacom/unbind
sleep 1
echo -n "0018:056A:49BB.0002" | sudo tee /sys/bus/hid/drivers/wacom/bind
```

### 2. Durable fix — install the resume hook

Because the latch is resume-triggered, install a `systemd` `system-sleep` hook that rebinds the device after every resume, but only when a touch is actually stuck. Install `evtest` (for the stuck-check guard) and write the hook in one block:

```bash
sudo pacman -S --needed evtest

sudo tee /usr/lib/systemd/system-sleep/wacom-touch-unstick >/dev/null <<'EOF'
#!/usr/bin/env bash
# Clear a stuck Wacom touchscreen touch (BTN_TOUCH latched down) after resume.

case "$1/$2" in
 post/*)
  HID_DEV="0018:056A:49BB.0002"
  DRV="/sys/bus/hid/drivers/wacom"
  [ -e "$DRV/$HID_DEV" ] || exit 0

  finger_ev=""
  for n in /sys/class/input/event*; do
   if [ "$(cat "$n/device/name" 2>/dev/null)" = "Wacom HID 49BB Finger" ]; then
    finger_ev="/dev/input/$(basename "$n")"
    break
   fi
  done

  # If evtest is present and BTN_TOUCH is UP (exit 0), nothing to fix.
  if [ -n "$finger_ev" ] && command -v evtest >/dev/null 2>&1; then
   evtest --query "$finger_ev" EV_KEY BTN_TOUCH >/dev/null 2>&1 && exit 0
  fi

  echo -n "$HID_DEV" > "$DRV/unbind" 2>/dev/null || exit 0
  sleep 1
  echo -n "$HID_DEV" > "$DRV/bind" 2>/dev/null || true
  ;;
esac

exit 0
EOF

sudo chmod 755 /usr/lib/systemd/system-sleep/wacom-touch-unstick
```

No service needs enabling: `systemd-suspend.service` runs every executable in `/usr/lib/systemd/system-sleep/` automatically, passing `post suspend` (or `post hibernate`) on resume. The hook resolves the Finger evdev node dynamically (node numbers change across reboots) and rebinds only when `BTN_TOUCH` is held, so a normal resume incurs no cost.

### 3. Verify

```bash
# Find the Wacom Finger node, then query its touch state (exit 0 = up, 10 = held)
evtest --query /dev/input/event11 EV_KEY BTN_TOUCH; echo "exit=$?"

# Dry-run the hook as systemd would on resume (safe: only rebinds if stuck)
sudo /usr/lib/systemd/system-sleep/wacom-touch-unstick post suspend; echo "exit=$?"
```

Revert by deleting `/usr/lib/systemd/system-sleep/wacom-touch-unstick`.

### If the touchscreen is unused

If the touchscreen is never used, an alternative is to mask the device entirely so it can never inject a stuck touch — at the cost of disabling touchscreen (and possibly pen) input. The resume hook above is preferred as it keeps the digitiser working.
