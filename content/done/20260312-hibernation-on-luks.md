---
title: Hibernation Reliability on LUKS-Encrypted Systems
---

- **Date:** 2026-03-12
- **Context:** Manjaro Linux with KDE Plasma on LUKS+LVM, Intel 12th Gen i7-12800H

## Problem Statement

The system experienced a complete freeze on March 12, 2026, at 09:35 due to a hibernation resume failure on LUKS-encrypted swap. Investigation revealed:

**Incident Timeline:**

- **March 11, 15:03** - System hibernated (RAM saved to encrypted swap)
- **March 12, 08:31** - System resumed from hibernation
- **March 12, 08:32** - NMI (Non-Maskable Interrupt) hardware error occurred 19 seconds after resume
- **March 12, 09:32** - VirtualBox kernel modules loaded (~1 hour later)
- **March 12, 09:35** - System completely froze, requiring hard reboot

**Root Cause:**

```text
Mar 12 08:32:00 kernel: Uhhuh. NMI received for unknown reason 30 on CPU 0.
Mar 12 08:32:00 kernel: Dazed and confused, but trying to continue
```

The hibernation resume process failed to properly restore CPU state after decrypting 32GB of RAM from LUKS-encrypted swap. The system remained in an unstable state for over an hour before VirtualBox triggered the final freeze.

**Key Challenge:** Modern sleep states (S0/S2ix "Modern Standby") consume excessive battery power (est. 10-20% per hour) on this hardware, and S3 sleep is not available. Hibernation is the **only viable option** for long-term power saving, making reliability critical for daily use.

## System Configuration

- **CPU:** Intel Core i7-12800H (Alder Lake, 12th Gen, 14 cores)
- **RAM:** 32 GB
- **Storage:** NVMe (nvme0n1) with LUKS encryption
- **Swap:** 64 GB encrypted LVM partition (`/dev/linux-crypt-vg/swap`)
- **Disk Layout:**

  ```text
  nvme0n1p6 (crypto_LUKS) → linux-crypt (LVM2) → linux-crypt-vg/swap (64GB)
  ```

- **Boot Parameters:**

  ```text
  cryptdevice=UUID=5af18995-b106-4b9e-8e73-c43593bd45ec:linux-crypt
  resume=/dev/linux-crypt-vg/swap
  ```

- **Initramfs Hooks (mkinitcpio):**

  ```bash
  HOOKS=(base udev autodetect microcode kms modconf block keyboard keymap
         consolefont plymouth encrypt lvm2 filesystems resume fsck)
  ```

- **Hibernation Frequency:** Daily usage

## Solution

Since S3 sleep is unavailable and modern sleep states drain battery excessively, hibernation is the only viable option for daily use. Unencrypted swap would defeat the purpose of LUKS encryption by exposing RAM contents (keys, passwords) in plaintext.

**Approach:** Add kernel parameters to fix known NVMe power state and console suspend issues during LUKS hibernation resume.

## Implementation

### Configuration Steps

```bash
# 1. Backup current configuration
sudo cp /etc/default/grub /etc/default/grub.backup
sudo cp /etc/mkinitcpio.conf /etc/mkinitcpio.conf.backup

# 2. Edit GRUB configuration
sudo nano /etc/default/grub
# Add to GRUB_CMDLINE_LINUX_DEFAULT (append to existing parameters):
#   no_console_suspend nvme_core.default_ps_max_latency_us=0

# 3. Verify the full line looks like:
# GRUB_CMDLINE_LINUX_DEFAULT="quiet udev.log_priority=3 cryptdevice=UUID=5af18995-b106-4b9e-8e73-c43593bd45ec:linux-crypt root=/dev/linux-crypt-vg/root resume=/dev/linux-crypt-vg/swap no_console_suspend nvme_core.default_ps_max_latency_us=0"

# 4. Update GRUB
sudo grub-mkconfig -o /boot/grub/grub.cfg

# 5. Rebuild initramfs (ensures consistency)
sudo mkinitcpio -P

# 6. Reboot to apply changes
sudo reboot
```

**What these parameters do:**

- `no_console_suspend` - Keeps console active during suspend/resume for stability
- `nvme_core.default_ps_max_latency_us=0` - Disables NVMe autonomous power states (prevents timing issues during resume)

**Current initramfs configuration (already correct):**

```bash
HOOKS=(... encrypt lvm2 filesystems resume ...)
       ^^^^^^^ ^^^^ ^^^^^^^^^^^ ^^^^^^
       Must be in this order for LUKS hibernation
```

### Monitoring Commands

```bash
# Check for NMI errors after resume
journalctl -b -k | grep -i "nmi\|dazed"

# Verify successful hibernation from previous boot
journalctl -b -1 | grep "hibernation exit"

# Check resume process for errors
journalctl -b -k | grep -i "resume\|hibernate"

# Check for hardware errors during resume
journalctl -b -k | grep -i "nmi\|mce\|hardware error"

# Review recent hibernate-related errors
journalctl --since "7 days ago" | grep -i "hibernate\|resume" | grep -i "error\|fail\|warn"

# Verify swap is configured correctly
swapon --show
```

## References

- [Arch Wiki: Power management/Suspend and hibernate](https://wiki.archlinux.org/title/Power_management/Suspend_and_hibernate)
- [Arch Wiki: Dm-crypt/Swap encryption](https://wiki.archlinux.org/title/Dm-crypt/Swap_encryption)
- [Arch Wiki: NVMe power state management](https://wiki.archlinux.org/title/Solid_State_Drives/NVMe)

**NMI Error (reason code 30):** Likely hardware-specific interrupt from NVMe controller during resume. NVMe autonomous power state transitions can cause timing issues when kernel tries to access the drive during hibernation resume.
