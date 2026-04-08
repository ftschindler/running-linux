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

4. Reboot to load DKMS drivers and apply group membership.

### Verification

After reboot:

```bash
# Verify DKMS module loaded
lsmod | grep intel_ipu6_psys

# Verify PSYS device exists
ls -la /dev/ipu-psys0

# Verify group membership
groups | grep video

# Test camera
gst-launch-1.0 icamerasrc ! "video/x-raw,width=1280,height=720" ! videoconvert ! autovideosink

# Test in browser
firefox https://webcamtests.com
```

### Troubleshooting

**Issue:** "Failed to open PSYS, error: Permission denied"
**Solution:** Ensure user is in `video` group and has logged out/in after adding group membership.

**Issue:** "Failed to open PSYS, error: No such file or directory"
**Solution:** Install kernel headers and reboot to ensure DKMS modules are built and loaded.

## Alternative Options Considered

Use the open-source libcamera framework with experimental IPU6 support.

**Advantages:**

- Fully open-source solution
- Integrated with modern Linux camera stack
- Better long-term sustainability

**Disadvantages:**

- IPU6 support still experimental/incomplete as of 2026-04
- May have limited ISP features compared to Intel HAL
- Requires building libcamera from git (IPU6 support not in stable releases)
- Not all applications support libcamera yet

**Implementation:**

```bash
sudo pacman -S libcamera libcamera-tools pipewire-v4l2
```

**Status:** Experimental; check libcamera git repository for current IPU6 support status.

### Option 3: Manual Media Pipeline Configuration (Advanced)

Manually configure media pipeline for raw Bayer capture with custom processing.

**Disadvantages:**

- Requires manual media-ctl commands for every session
- Must implement own ISP processing (debayering, etc.)
- Not practical for daily use

**Status:** Proof of concept only; not recommended.

### Option 4: IVSC Firmware Extraction (Not Recommended)

Extract IVSC firmware from Windows drivers.

**Disadvantages:**

- Complex extraction process
- Potential license violations
- Uncertain benefit (camera already detected)
- No official IVSC firmware for Linux

**Status:** Not recommended.

## References

- [Arch Wiki: Webcam setup](https://wiki.archlinux.org/title/Webcam_setup)
- [Intel IPU6 Camera HAL GitHub](https://github.com/intel/ipu6-camera-hal)
- [Intel IPU6 DKMS Drivers GitHub](https://github.com/intel/ipu6-drivers)
- [AUR: intel-ipu6-camera-bin](https://aur.archlinux.org/packages/intel-ipu6-camera-bin)
- [AUR: intel-ipu6-camera-hal-git](https://aur.archlinux.org/packages/intel-ipu6-camera-hal-git)
- [AUR: intel-ipu6-dkms-git](https://aur.archlinux.org/packages/intel-ipu6-dkms-git)
- [AUR: icamerasrc-git](https://aur.archlinux.org/packages/icamerasrc-git)
