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

6. Create systemd user service at `~/.config/systemd/user/ipu6-virtual-webcam.service`:

   ```ini
   [Unit]
   Description=IPU6 Virtual Webcam (Always-On)
   After=pipewire.service

   [Service]
   Type=simple
   ExecStart=/usr/bin/gst-launch-1.0 icamerasrc ! video/x-raw,width=1280,height=720 ! videoconvert ! v4l2sink device=/dev/video42
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=default.target
   ```

7. Enable and start the service:

   ```bash
   systemctl --user enable --now ipu6-virtual-webcam.service
   ```

8. Create udev rule to ensure correct permissions for IPU6 devices:

   Create `/etc/udev/rules.d/60-ipu6-permissions.rules`:

   ```bash
   # Ensure IPU6 raw video devices are accessible to video group
   # Required for icamerasrc to access the camera hardware

   SUBSYSTEM=="video4linux", ATTRS{name}=="Intel IPU6 ISYS Capture ?", MODE="0660", GROUP="video"
   SUBSYSTEM=="video4linux", ATTRS{name}=="Intel IPU6 ISYS Capture ??", MODE="0660", GROUP="video"
   ```

   Apply the rule:

   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger --subsystem-match=video4linux
   ```

   **Note:** The raw IPU6 devices will be visible in browser device lists alongside the virtual webcam. Users should select "IPU6 Virtual Webcam" when choosing a camera. Hiding these devices would break icamerasrc functionality.

9. Reboot to load DKMS drivers and apply all configurations.

### How It Works

The solution uses a simple always-on GStreamer pipeline:

- `icamerasrc` captures video from the IPU6 camera (processes raw Bayer data via Intel HAL)
- `videoconvert` converts to standard formats
- `v4l2sink` outputs to `/dev/video42` (v4l2loopback virtual device)
- The pipeline runs continuously as a systemd user service
- All applications see `/dev/video42` as a standard webcam

**Trade-off:** The privacy LED is always ON while the service is running. This is necessary for reliable application compatibility (especially MS Teams) which needs real camera frames for device detection.

To temporarily disable the camera, stop the service:

```bash
systemctl --user stop ipu6-virtual-webcam.service
```

To restart it:

```bash
systemctl --user start ipu6-virtual-webcam.service
```

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

# Verify service is running
systemctl --user status ipu6-virtual-webcam.service

# Check visible video devices
v4l2-ctl --list-devices

# Test in browser (select "IPU6 Virtual Webcam" from device list)
firefox https://webcamtests.com

# Test in Teams
# Camera should appear in Teams settings and work for video calls
```

**Expected behavior:**

- Privacy LED is always ON while service is running
- Camera works in all applications (Firefox, Chrome, Teams, etc.)
- Multiple video devices visible in browser - select "IPU6 Virtual Webcam"
- CPU usage: ~5-10% when pipeline is running, more when actively streaming

### Troubleshooting

**Issue:** "Failed to open PSYS, error: Permission denied"
**Solution:** Ensure user is in `video` group and has logged out/in after adding group membership.

**Issue:** "Failed to open PSYS, error: No such file or directory"
**Solution:** Install kernel headers and reboot to ensure DKMS modules are built and loaded.

**Issue:** Virtual webcam shows "no signal" or black screen
**Solution:** Check service status: `systemctl --user status ipu6-virtual-webcam.service`. If failed, check logs: `journalctl --user -u ipu6-virtual-webcam.service -n 50`. Restart service: `systemctl --user restart ipu6-virtual-webcam.service`

**Issue:** v4l2loopback module not loading
**Solution:** Verify module is installed: `modinfo v4l2loopback`. Check config: `/etc/modules-load.d/v4l2loopback.conf` and `/etc/modprobe.d/v4l2loopback.conf`. Manual load: `sudo modprobe v4l2loopback video_nr=42`

**Issue:** MS Teams doesn't recognize camera
**Solution:** This should not occur with the always-on pipeline. Verify the service is running and restart Teams.

**Issue:** Want to disable camera LED
**Solution:** Not possible with this solution. The LED is hardware-controlled and turns on when the sensor is active. To disable the camera entirely, stop the service: `systemctl --user stop ipu6-virtual-webcam.service`

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
