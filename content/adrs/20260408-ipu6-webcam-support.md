# ADR: Intel IPU6 Webcam Support on Dell Precision 5470

**Date:** 2026-04-08
**Status:** Accepted
**Context:** Manjaro Linux with KDE Plasma on Dell Precision 5470, Intel 12th Gen i7-12800H

## Problem Statement

The integrated webcam is not functional under Linux despite all hardware being detected and kernel drivers loaded. Applications fail with "Link has been severed" errors when attempting to access camera devices.

## System Configuration

- **Hardware:** Intel IPU6 [8086:465d] with OV01A10 sensor via USB LJCA Bridge [8086:0b63]
- **Kernel:** 6.18.18-1-MANJARO
- **Firmware:** linux-firmware-intel 20260309-1 (up-to-date as of 2026-04-08)

## Root Cause

Intel IPU6 uses a "software ISP" architecture requiring userspace processing. The kernel drivers output raw Bayer sensor data; Intel provides closed-source binaries (`ipu6-camera-hal`, `ipu6-camera-bins`) to process this into usable video.

Additionally, the mainline kernel IPU6 drivers lack PSYS (Processing System) support required by the camera HAL. DKMS out-of-tree drivers from Intel are needed.

## Solution (Implemented)

### Installation Steps

1. Install Intel IPU6 camera stack from AUR:

   ```bash
   paru -S intel-ipu6-camera-bin intel-ipu6-camera-hal-git icamerasrc-git
   ```

   This also installs `intel-ipu6-dkms-git` as a dependency.

2. Install kernel headers (required for DKMS to build modules):

   ```bash
   sudo pacman -S linux618-headers
   ```

   DKMS will automatically build and install the IPU6 PSYS module.

3. Add user to `video` group (required for `/dev/ipu-psys0` access):

   ```bash
   sudo usermod -aG video $USER
   ```

4. Install v4l2loopback for virtual webcam (browser/Teams compatibility):

   ```bash
   sudo pacman -S v4l2loopback-dkms v4l2loopback-utils
   ```

5. Configure v4l2loopback module to load at boot:

   ```bash
   echo "v4l2loopback" | sudo tee /etc/modules-load.d/v4l2loopback.conf
   echo "options v4l2loopback devices=1 video_nr=42 card_label=\"IPU6 Virtual Webcam\"" | sudo tee /etc/modprobe.d/v4l2loopback.conf
   ```

6. Create webcam manager script at `~/.local/bin/ipu6-webcam-manager`:

   ```bash
   #!/bin/bash
   # IPU6 Virtual Webcam On-Demand Manager
   # Uses a priming pipeline to keep device accessible, switches to real camera on demand

   VIRTUAL_DEVICE="/dev/video42"
   REAL_PIPELINE="gst-launch-1.0 icamerasrc ! video/x-raw,width=1280,height=720 ! videoconvert ! v4l2sink device=${VIRTUAL_DEVICE}"
   PRIMING_PIPELINE="gst-launch-1.0 videotestsrc pattern=black ! video/x-raw,width=1280,height=720,framerate=30/1 ! videoconvert ! v4l2sink device=${VIRTUAL_DEVICE}"

   REAL_PID=""
   PRIMING_PID=""
   CURRENT_MODE="priming"

   cleanup() {
       echo "Shutting down..."
       [ -n "$REAL_PID" ] && kill "$REAL_PID" 2>/dev/null
       [ -n "$PRIMING_PID" ] && kill "$PRIMING_PID" 2>/dev/null
       exit 0
   }

   trap cleanup SIGTERM SIGINT

   start_priming() {
       if [ -z "$PRIMING_PID" ] || ! kill -0 "$PRIMING_PID" 2>/dev/null; then
           echo "$(date): Starting priming pipeline (low-power mode)..."
           $PRIMING_PIPELINE >/dev/null 2>&1 &
           PRIMING_PID=$!
           CURRENT_MODE="priming"
       fi
   }

   start_real() {
       # Stop priming if running
       if [ -n "$PRIMING_PID" ] && kill -0 "$PRIMING_PID" 2>/dev/null; then
           kill "$PRIMING_PID" 2>/dev/null
           sleep 0.5
       fi

       # Start real camera
       if [ -z "$REAL_PID" ] || ! kill -0 "$REAL_PID" 2>/dev/null; then
           echo "$(date): Starting real camera pipeline (LED ON)..."
           $REAL_PIPELINE >/dev/null 2>&1 &
           REAL_PID=$!
           CURRENT_MODE="real"
       fi
   }

   stop_real() {
       if [ -n "$REAL_PID" ] && kill -0 "$REAL_PID" 2>/dev/null; then
           echo "$(date): Stopping real camera pipeline (LED OFF)..."
           kill "$REAL_PID" 2>/dev/null
           REAL_PID=""
           sleep 0.5
           start_priming
       fi
   }

   echo "IPU6 Virtual Webcam Manager started"

   # Start with priming pipeline
   start_priming
   sleep 2

   # Main monitoring loop
   while true; do
       # Count processes accessing the device (excluding our own pipelines)
       USERS=$(fuser ${VIRTUAL_DEVICE} 2>/dev/null | tr ' ' '\n' | grep -v "^$" | grep -v "^${REAL_PID}$" | grep -v "^${PRIMING_PID}$" | wc -l)

       if [ "$USERS" -gt 0 ]; then
           # Someone is using the camera
           if [ "$CURRENT_MODE" = "priming" ]; then
               start_real
           fi
       else
           # No external users
           if [ "$CURRENT_MODE" = "real" ]; then
               stop_real
           fi
       fi

       # Ensure priming is running when in priming mode
       if [ "$CURRENT_MODE" = "priming" ]; then
           if [ -z "$PRIMING_PID" ] || ! kill -0 "$PRIMING_PID" 2>/dev/null; then
               start_priming
           fi
       fi

       # Ensure real pipeline is running when in real mode
       if [ "$CURRENT_MODE" = "real" ]; then
           if [ -z "$REAL_PID" ] || ! kill -0 "$REAL_PID" 2>/dev/null; then
               start_real
           fi
       fi

       sleep 2
   done
   ```

   Make it executable: `chmod +x ~/.local/bin/ipu6-webcam-manager`

7. Create systemd user service at `~/.config/systemd/user/ipu6-virtual-webcam.service`:

   ```ini
   [Unit]
   Description=IPU6 Virtual Webcam Manager (On-Demand with Priming)
   After=pipewire.service

   [Service]
   Type=simple
   ExecStart=%h/.local/bin/ipu6-webcam-manager
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=default.target
   ```

8. Enable and start the service:

   ```bash
   systemctl --user enable --now ipu6-virtual-webcam.service
   ```

9. Hide raw IPU6 devices from browsers (optional but recommended):

   Create `/etc/udev/rules.d/60-ipu6-hide-raw-devices.rules`:

   ```bash
   # Hide raw IPU6 Bayer devices from applications, keep v4l2loopback virtual webcam visible
   # The raw IPU6 devices only work with Intel HAL anyway, not standard V4L2 apps

   # IPU6 raw devices - restrict to root only (hide from normal user applications)
   SUBSYSTEM=="video4linux", ATTR{name}=="Intel IPU6 ISYS Capture*", MODE="0600", GROUP="root"

   # Ensure v4l2loopback virtual webcam remains accessible
   SUBSYSTEM=="video4linux", ATTR{name}=="IPU6 Virtual Webcam", MODE="0660", GROUP="video"
   ```

   Apply the rule:

   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger --subsystem-match=video4linux
   ```

10. Reboot to load DKMS drivers and apply all configurations.

### How It Works

- **Priming Mode (default):** GStreamer pipeline outputs black frames at 1280x720@30fps to `/dev/video42`
  - LED is **OFF** (real camera not accessed)
  - Minimal CPU usage
  - Device appears functional to browsers/apps

- **Active Mode:** When application opens `/dev/video42`:
  - Manager script detects access via `fuser`
  - Stops priming pipeline
  - Starts real camera pipeline (icamerasrc)
  - LED turns **ON**

- **Back to Priming:** When application closes device:
  - Manager detects no external users
  - Stops real camera pipeline
  - Restarts priming pipeline
  - LED turns **OFF**

The privacy LED accurately reflects actual camera usage with ~2 second delay.

### Verification

After reboot:

```bash
# Verify DKMS module loaded
lsmod | grep intel_ipu6_psys

# Verify PSYS device exists
ls -la /dev/ipu-psys0

# Verify group membership
groups | grep video

# Verify v4l2loopback virtual device exists
ls -la /dev/video42

# Verify manager service is running
systemctl --user status ipu6-virtual-webcam.service

# Check visible video devices (should only show video42)
v4l2-ctl --list-devices

# Test in browser (LED should turn on when accessing camera)
firefox https://webcamtests.com

# Verify privacy LED turns OFF when closing camera
# (close browser tab, wait ~2 seconds, LED should turn off)
```

**Expected behavior:**

- Privacy LED is OFF when idle
- LED turns ON within 2 seconds of opening camera in application
- LED turns OFF within 2 seconds of closing camera
- Only `/dev/video42` appears in browser device lists (32 raw IPU6 devices hidden)

### Troubleshooting

**Issue:** "Failed to open PSYS, error: Permission denied"
**Solution:** Ensure user is in `video` group and has logged out/in after adding group membership.

**Issue:** "Failed to open PSYS, error: No such file or directory"
**Solution:** Install kernel headers and reboot to ensure DKMS modules are built and loaded.

**Issue:** Virtual webcam shows "no signal" or black screen in browser
**Solution:** Check manager service status: `systemctl --user status ipu6-virtual-webcam.service`. If failed, check logs: `journalctl --user -u ipu6-virtual-webcam.service -n 50`

**Issue:** Privacy LED stays on constantly
**Solution:** The priming pipeline should keep LED off. Verify manager script is running and in priming mode. Check if real pipeline is stuck: `ps aux | grep gst-launch`.

**Issue:** v4l2loopback module not loading
**Solution:** Verify module is installed: `modinfo v4l2loopback`. Check config: `/etc/modules-load.d/v4l2loopback.conf` and `/etc/modprobe.d/v4l2loopback.conf`. Manual load: `sudo modprobe v4l2loopback video_nr=42`

**Issue:** Multiple video devices visible in browsers
**Solution:** Apply udev rule from step 9 to hide raw IPU6 devices. Reload: `sudo udevadm control --reload-rules && sudo udevadm trigger --subsystem-match=video4linux`

## Alternative Options Considered

### libcamera Framework

Open-source camera stack with experimental IPU6 support.

**Advantages:**

- Fully open-source
- Better long-term sustainability
- Integrated with modern Linux camera stack

**Disadvantages:**

- IPU6 support still experimental/incomplete as of 2026-04
- Requires building from git (not in stable releases)
- Limited application support

**Status:** Not mature enough for daily use; monitor libcamera git for IPU6 progress.

### Manual Media Pipeline (media-ctl)

Configure media pipeline manually for raw Bayer capture.

**Status:** Proof of concept only; requires manual ISP processing and media-ctl commands per session. Not practical.

## References

- [Arch Wiki: Webcam setup](https://wiki.archlinux.org/title/Webcam_setup)
- [Intel IPU6 Camera HAL GitHub](https://github.com/intel/ipu6-camera-hal)
- [Intel IPU6 DKMS Drivers GitHub](https://github.com/intel/ipu6-drivers)
- [AUR: intel-ipu6-camera-bin](https://aur.archlinux.org/packages/intel-ipu6-camera-bin)
- [AUR: intel-ipu6-camera-hal-git](https://aur.archlinux.org/packages/intel-ipu6-camera-hal-git)
- [AUR: intel-ipu6-dkms-git](https://aur.archlinux.org/packages/intel-ipu6-dkms-git)
- [AUR: icamerasrc-git](https://aur.archlinux.org/packages/icamerasrc-git)
