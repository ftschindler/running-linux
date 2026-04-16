# Bluetooth Headset Codec Switching Issue (MSBC → SBC)

**Date:** 2026-04-16

## Problem

Bluetooth headset (Shokz OpenMove) on Manjaro with PipeWire would immediately revert from MSBC codec back to SBC after manually selecting MSBC profile. This made the headset microphone unusable.

## Requirements

- Keep MSBC (headset) profile active when manually selected
- Allow microphone access without automatic profile switching
- Maintain stable codec selection

## Investigation

The issue was caused by WirePlumber's automatic Bluetooth profile switching feature (`autoswitch-bluetooth-profile.lua`). This script automatically:

- Switches to A2DP (high quality audio, no mic) when no capture stream is active
- Switches to HSP/HFP (headset mode with mic) only when microphone is actively being used

The autoswitch behavior is controlled by the setting `bluetooth.autoswitch-to-headset-profile` (default: `true`).

### Why It Started Happening

The issue appeared after a PipeWire update on April 8, 2026:

- **PipeWire upgraded:** 1.4.10 → 1.6.2
- **WirePlumber:** 0.5.13 (unchanged)

WirePlumber 0.5.13 (released January 2026) included an enhancement: "Enhanced Bluetooth profile autoswitch logic to be more robust and handle saved profiles correctly" (!739). Combined with PipeWire 1.6.2, this made the autoswitch feature work more reliably than in previous versions, where it may have been less effective or broken.

## Solution

Disable the automatic Bluetooth profile switching:

```bash
wpctl settings bluetooth.autoswitch-to-headset-profile false
```

This setting is persistent across reboots.

### Verification

After applying the fix:

1. Reconnect the Bluetooth headset
2. Switch to MSBC profile: `pactl set-card-profile bluez_card.<MAC_ADDRESS> headset-head-unit`
3. Verify codec: `wpctl inspect <device_id> | grep codec`

The profile should remain stable and show `api.bluez5.codec = "msbc"`.

### Reverting

To re-enable automatic switching:

```bash
wpctl settings bluetooth.autoswitch-to-headset-profile true
```
