# ADR: Intel IPU6 Webcam Support on Dell Precision 5470

**Date:** 2026-04-08
**Status:** Proposed
**Context:** Manjaro Linux with KDE Plasma on Dell Precision 5470, Intel 12th Gen i7-12800H

## Problem Statement

The integrated webcam is not functional under Linux despite all hardware being detected and kernel drivers loaded. Applications fail with "Link has been severed" errors when attempting to access camera devices.

## System Configuration

- **Hardware:** Intel IPU6 [8086:465d] with OV01A10 sensor via USB LJCA Bridge [8086:0b63]
- **Kernel:** 6.18.18-1-MANJARO
- **Firmware:** linux-firmware-intel 20260309-1 (up-to-date as of 2026-04-08)

## Current Status

### Currently Failing

```bash
# Camera detection works
v4l2-ctl --list-devices  # Shows ipu6 with /dev/video0-31

# But capture fails
ffmpeg -f v4l2 -i /dev/video16 test.jpg
# Error: Link has been severed
```

### After Solution Implementation

```bash
# Check HAL installation
ls -lh /usr/lib/libcamhal.so
gst-inspect-1.0 icamerasrc

# Test with GStreamer
gst-launch-1.0 icamerasrc ! videoconvert ! autovideosink

# Test in browser
firefox https://webcamtests.com

# Monitor for issues
journalctl -b -f | grep -iE "camera|ipu6|ivsc"
```

## Root Cause

Intel IPU6 uses a "software ISP" architecture requiring userspace processing. The kernel drivers output raw Bayer sensor data; Intel provides closed-source binaries (`ipu6-camera-hal`, `ipu6-camera-bins`) to process this into usable video

## Solution Options

### Option 1: Install Intel IPU6 Camera HAL (Recommended)

Install Intel's proprietary camera userspace libraries and integration layer.

**Advantages:**

- Full camera functionality with all ISP features
- Works with standard applications (Firefox, Chrome, Cheese, etc.)
- Maintained by Intel for modern laptops

**Disadvantages:**

- Requires AUR packages (not in official repos)
- Proprietary binaries (~100MB download)
- May have compatibility issues with future kernel updates

**Implementation:**

```bash
paru -S intel-ipu6-camera-bin intel-ipu6-camera-hal-git icamerasrc-git
```

### Option 2: Use libcamera with IPU6 Pipeline Handler

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
- [Intel IPU6 Bins GitHub](https://github.com/intel/ipu6-camera-bins)
- [AUR: ipu6-camera-bins](https://aur.archlinux.org/packages/ipu6-camera-bins)
- [AUR: ipu6-camera-hal](https://aur.archlinux.org/packages/ipu6-camera-hal)
- [AUR: icamerasrc](https://aur.archlinux.org/packages/icamerasrc)
