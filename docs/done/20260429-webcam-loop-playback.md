---
title: Looped Virtual Webcam Playback Service
---

- **Date:** 2026-04-29
- **Context:** Manjaro Linux with KDE Plasma on Dell Precision 5470, building upon the IPU6 virtual webcam solution

## Problem Statement

During long video calls where camera presence is expected but a live feed is unnecessary, running the IPU6 camera pipeline continuously wastes CPU resources and keeps the privacy LED permanently on. A short pre-recorded loop provides realistic camera presence whilst reducing resource usage.

## Prerequisites

- Working IPU6 virtual webcam per [ADR 20260408 — IPU6 Webcam Support](20260408-ipu6-webcam-support.md)
- `ipu6-virtual-webcam.service` running and outputting to `/dev/video42`

## Solution (Implemented)

A systemd user service that:

1. Records a 1-minute clip from the live virtual webcam (`/dev/video42`) using `ffmpeg`
2. Plays the clip back in an infinite loop to a second v4l2loopback device (`/dev/video43`)
3. Runs until explicitly stopped

The service declares a dependency on `ipu6-virtual-webcam.service` to ensure the live camera feed is available during the recording phase.

### How It Works

```text
[IPU6 Camera] → icamerasrc → /dev/video42 (live)
                                    ↓
                            ffmpeg records 60s
                                    ↓
                              clip.mp4 (RAM)
                                    ↓
                            ffmpeg -stream_loop
                                    ↓
                              /dev/video43 (loop)
```

- During startup, a desktop notification announces the recording with a 3-second countdown
- During the first 60 seconds, the live camera must be active for recording
- A second notification confirms recording is complete and playback is starting
- After recording completes, the looped playback runs independently
- Applications select "IPU6 Loop Playback" as their camera device

### Installation Steps

1. Install `ffmpeg` and `libnotify` (if not already present):

   ```bash
   sudo pacman -S ffmpeg libnotify
   ```

   `libnotify` provides `notify-send` for desktop notifications.

2. Update v4l2loopback to provide a second virtual device.

   Replace `/etc/modprobe.d/v4l2loopback.conf`:

   ```bash
   echo 'options v4l2loopback devices=2 video_nr=42,43 card_label="IPU6 Virtual Webcam,IPU6 Loop Playback" exclusive_caps=1' | sudo tee /etc/modprobe.d/v4l2loopback.conf
   ```

   This changes `devices=1` to `devices=2` and assigns `/dev/video43` with the label "IPU6 Loop Playback". Both devices retain `exclusive_caps=1` for MS Teams compatibility.

3. Create the recording and playback script at `~/.local/bin/webcam-loop-record.sh`:

   ```bash
   #!/bin/bash
   set -euo pipefail

   CLIP="${XDG_RUNTIME_DIR}/webcam-loop-clip.mp4"
   SOURCE="/dev/video42"
   SINK="/dev/video43"

   cleanup() {
       rm -f "$CLIP"
   }
   trap cleanup EXIT

   notify-send -a "Webcam Loop" "Webcam Loop" "Recording will start in 3 seconds…"
   sleep 3

   # Record 1-minute clip from the live virtual webcam
   ffmpeg -y -f v4l2 -video_size 1280x720 -i "$SOURCE" \
       -t 60 -c:v libx264 -preset ultrafast -pix_fmt yuv420p "$CLIP"

   notify-send -a "Webcam Loop" "Webcam Loop" "Recording complete. Starting looped playback."

   # Loop playback to the second virtual webcam until stopped
   ffmpeg -re -stream_loop -1 -i "$CLIP" \
       -f v4l2 -pix_fmt yuv420p "$SINK"
   ```

   Make it executable:

   ```bash
   chmod +x ~/.local/bin/webcam-loop-record.sh
   ```

4. Create the systemd user service at `~/.config/systemd/user/webcam-loop.service`:

   ```ini
   [Unit]
   Description=Looped Webcam Playback (Record and Replay)
   After=ipu6-virtual-webcam.service
   Requires=ipu6-virtual-webcam.service

   [Service]
   Type=simple
   ExecStart=%h/.local/bin/webcam-loop-record.sh
   Restart=on-failure
   RestartSec=10

   [Install]
   WantedBy=default.target
   ```

5. Reload the v4l2loopback module and enable the service:

   ```bash
   # Reload v4l2loopback with the updated two-device configuration
   sudo modprobe -r v4l2loopback
   sudo modprobe v4l2loopback

   # Restart the live webcam (interrupted by module reload)
   systemctl --user restart ipu6-virtual-webcam.service

   # Reload systemd user units
   systemctl --user daemon-reload
   ```

   **Note:** A reboot also applies the new v4l2loopback configuration.

6. Start the loop service when needed:

   ```bash
   systemctl --user start webcam-loop.service
   ```

   The service will show a notification, wait 3 seconds, then record for 60 seconds from the live camera. A second notification confirms when loop playback begins on `/dev/video43`.

   To stop:

   ```bash
   systemctl --user stop webcam-loop.service
   ```

   To enable automatic start at login (optional):

   ```bash
   systemctl --user enable webcam-loop.service
   ```

### Verification

```bash
# Verify both v4l2loopback devices exist
v4l2-ctl --list-devices
# Should show both "IPU6 Virtual Webcam" and "IPU6 Loop Playback"

# Verify the loop service is running
systemctl --user status webcam-loop.service

# Check the loop device is outputting video
ffplay /dev/video43

# Test in browser (select "IPU6 Loop Playback" from device list)
firefox https://webcamtests.com
```

### Troubleshooting

**Issue:** Recording fails with "No such file or directory" for `/dev/video43`
**Solution:** The v4l2loopback module was not reloaded with the updated two-device configuration. Run `sudo modprobe -r v4l2loopback && sudo modprobe v4l2loopback` or reboot.

**Issue:** Recording produces a black or garbled clip
**Solution:** Ensure `ipu6-virtual-webcam.service` is running and producing output on `/dev/video42` before starting the loop service. Test with `ffplay /dev/video42`.

**Issue:** Playback loop has a brief stutter at the loop point
**Solution:** This is inherent to `ffmpeg -stream_loop`. For a smoother loop, record a clip where the start and end frames are similar (e.g. sitting still with a neutral expression).

**Issue:** "IPU6 Loop Playback" not visible in MS Teams
**Solution:** Ensure both v4l2loopback devices have `exclusive_caps=1` (set in the modprobe config). Restart Teams after starting the service.

**Issue:** Service fails to start with "Requires dependency failed"
**Solution:** The live webcam service is not running. Start it first with `systemctl --user start ipu6-virtual-webcam.service`, then retry.

## Trade-offs

- **`Requires=` dependency:** Stopping `ipu6-virtual-webcam.service` will also stop `webcam-loop.service`. This is intentional — the loop service needs to re-record on each start. To stop the live camera after recording completes whilst keeping the loop running, change `Requires=` to `Wants=` in the service unit.
- **~63-second startup delay:** The service shows a desktop notification, waits 3 seconds (to allow the user to prepare), then records for 60 seconds before loop playback begins. Start the service before joining a call.
- **Clip stored in RAM:** The recorded clip is saved to `$XDG_RUNTIME_DIR` (tmpfs). At 720p with ultrafast x264, a 1-minute clip is roughly 5–15 MB — negligible on any modern system.

## References

- [ADR 20260408 — IPU6 Webcam Support](20260408-ipu6-webcam-support.md)
- [ffmpeg v4l2 documentation](https://ffmpeg.org/ffmpeg-devices.html#v4l2)
- [v4l2loopback GitHub](https://github.com/umlaeute/v4l2loopback)
