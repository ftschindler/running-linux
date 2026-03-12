# ADR: Hibernation Reliability on LUKS-Encrypted Systems

**Date:** 2026-03-12
**Status:** Proposed
**Context:** Manjaro Linux with KDE Plasma on LUKS+LVM, Intel 12th Gen i7-12800H

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

## Constraints

1. **S3 sleep unavailable** - BIOS/firmware does not support S3 (suspend-to-RAM)
2. **Modern sleep states drain battery** - S0/S2ix "Modern Standby" unusable for long periods
3. **No repartitioning** - Cannot modify disk layout without significant risk
4. **Encryption mandatory** - Unencrypted swap defeats the security purpose of LUKS
5. **Daily hibernation** - Need reliable hibernation for regular workflow

## Options Considered

### Option 1: Unencrypted Swap Partition

**Description:** Create a separate unencrypted partition for hibernation images.

**Implementation:**

```bash
# Requires repartitioning to create unencrypted swap
/dev/nvme0n1pX  swap  pri=10  # Unencrypted for hibernation
/dev/dm-1       swap  pri=1   # Encrypted for memory overflow
```

**Pros:**

- Most reliable hibernation (no LUKS decryption complexity)
- Fast resume (no encryption overhead)
- Well-tested, proven approach

**Cons:**

- **REJECTED:** Defeats purpose of LUKS encryption
- Exposes RAM contents (encryption keys, passwords, session data) in plaintext
- Requires repartitioning (risky on live system)
- Unacceptable security trade-off

### Option 2: Improve LUKS Hibernation Stability ⭐ RECOMMENDED

**Description:** Keep encrypted swap but add kernel parameters and configuration fixes to improve resume reliability.

**Implementation:**

#### A. Fix Initramfs Hook Order

The `resume` hook must come **after** `encrypt` and `lvm2` hooks so the encrypted swap is available during resume.

Current configuration (CORRECT):

```bash
# /etc/mkinitcpio.conf
HOOKS=(base udev autodetect microcode kms modconf block keyboard keymap
       consolefont plymouth encrypt lvm2 filesystems resume fsck)
                               ^^^^^^^ ^^^^ ^^^^^^^^^^^ ^^^^^^
                               1st     2nd  3rd         4th (CORRECT ORDER)
```

**No changes needed** - hooks are already in correct order.

#### B. Add Kernel Parameters for Stable Resume

```bash
# /etc/default/grub - Add to existing GRUB_CMDLINE_LINUX_DEFAULT
GRUB_CMDLINE_LINUX_DEFAULT="... no_console_suspend nvme_core.default_ps_max_latency_us=0"
```

**Parameter Explanations:**

- `no_console_suspend` - Keep console active during suspend/resume for debugging and stability
- `nvme_core.default_ps_max_latency_us=0` - Disable NVMe autonomous power state transitions during hibernation (prevents drive state corruption)

#### C. Verify Resume Parameter

Current configuration (CORRECT):

```bash
resume=/dev/linux-crypt-vg/swap
```

Ensures kernel knows where to restore hibernation image from encrypted swap.

#### D. Update GRUB and Rebuild Initramfs

```bash
# Apply kernel parameter changes
sudo grub-mkconfig -o /boot/grub/grub.cfg

# Rebuild initramfs (even though hooks are correct, ensures consistency)
sudo mkinitcpio -P
```

#### E. Testing Protocol

After configuration changes, test hibernation reliability:

```bash
# Test 1: Basic hibernation
systemctl hibernate
# Wake system, verify all processes restored correctly

# Test 2: Hibernation with load
# Open multiple applications, browser tabs, terminals
systemctl hibernate
# Wake, verify no NMI errors: journalctl -b -k | grep -i nmi

# Test 3: Long-duration hibernation
# Hibernate for 8+ hours (overnight)
# Wake, verify stability

# Test 4: Hibernation + VirtualBox
# After successful resume, start VirtualBox
# Verify no freeze occurs (this was the failure scenario)

# Monitor for NMI errors after each test
journalctl -b -k | grep -i "nmi\|dazed\|confused"
```

#### F. Monitoring Commands

```bash
# Check if hibernation completed successfully
journalctl -b -1 | grep -i hibernate | tail -20

# Check resume process for errors
journalctl -b -k | grep -i "resume\|hibernate"

# Check for hardware errors during resume
journalctl -b -k | grep -i "nmi\|mce\|hardware error"

# Verify swap is being used
swapon --show
```

**Pros:**

- ✅ Maintains LUKS encryption security
- ✅ No repartitioning required
- ✅ Low risk (only adds kernel parameters)
- ✅ Addresses known NVMe power state issues
- ✅ Console logging helps diagnose future issues
- ✅ Can be easily reverted if problematic

**Cons:**

- ⚠️ No guarantee of 100% reliability (LUKS hibernation inherently complex)
- ⚠️ May still experience rare resume failures
- ⚠️ Requires thorough testing to verify improvements

**Risk Assessment:** MEDIUM

- Known NVMe power state issues may be root cause
- Console suspend can cause hardware state confusion
- If this fails, no fallback except Option 3

### Option 3: Hybrid Swap Setup (Fallback)

**Description:** Use two swap spaces - small unencrypted for hibernation, large encrypted for memory pressure.

**Implementation:**

```bash
# Create 40GB unencrypted swap (requires repartitioning)
/dev/nvme0n1pX  swap  pri=10  # Hibernation only
/dev/dm-1       swap  pri=1   # Encrypted memory overflow

# Configure hibernate to use unencrypted swap
resume=/dev/nvme0n1pX
```

**Pros:**

- More reliable than pure LUKS hibernation
- Most runtime memory usage stays encrypted
- Hibernation images isolated from active swap

**Cons:**

- **Requires repartitioning** (disqualifies under current constraints)
- Hibernation images still unencrypted (security compromise)
- Complex setup with two swap spaces
- Higher risk during implementation

**Risk Assessment:** HIGH (due to repartitioning)

## Decision

### Implement Option 2: Improve LUKS Hibernation Stability

#### Rationale

1. **Meets all constraints:**
   - Maintains full LUKS encryption
   - No repartitioning required
   - Low implementation risk

2. **Addresses known issues:**
   - NVMe autonomous power states are a common cause of hibernation failures
   - Console suspend can interfere with hardware state restoration
   - Proper initramfs hooks already in place

3. **Testable and reversible:**
   - Changes are minimal (2 kernel parameters)
   - Can be reverted by removing parameters and regenerating GRUB config
   - Testing protocol provides clear success/failure criteria

4. **Industry precedent:**
   - NVMe power state issues are well-documented in Linux hibernation contexts
   - `no_console_suspend` is a standard troubleshooting parameter
   - Many users report success with these exact parameters

5. **Failure plan:**
   - If Option 2 fails after thorough testing, must reconsider constraints
   - Option 3 would require accepting repartitioning risk
   - Option 1 remains unacceptable due to security requirements

## Implementation Plan

### Phase 1: Apply Configuration (15 minutes)

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

### Phase 2: Testing (1-2 weeks)

#### Day 1-3: Basic Testing

- Test hibernation 3x per day
- Monitor for NMI errors after each resume
- Verify VirtualBox works after resume

#### Day 4-7: Stress Testing

- Hibernate with heavy workloads (10+ browser tabs, multiple VMs, development tools)
- Test overnight hibernation (8+ hours)
- Test hibernation → resume → VirtualBox → hibernate again cycle

#### Day 8-14: Production Use

- Use hibernation normally in daily workflow
- Document any issues immediately
- Keep `journalctl -b -k` logs for any problems

#### Success Criteria

- ✅ Zero NMI errors in 14-day period
- ✅ No system freezes after resume
- ✅ VirtualBox works reliably after resume
- ✅ No data loss or corruption events

#### Failure Criteria

- ❌ NMI errors continue to occur
- ❌ System freezes after resume (even once)
- ❌ Hibernation fails to complete or resume
- ❌ Data corruption detected

### Phase 3: Monitoring (Ongoing)

#### Daily Checks

```bash
# Check for NMI errors
journalctl -b -k | grep -i "nmi\|dazed"

# Verify successful hibernation
journalctl -b -1 | grep "hibernation exit"
```

#### Weekly Checks

```bash
# Review all hibernate-related errors
journalctl --since "7 days ago" | grep -i "hibernate\|resume" | grep -i "error\|fail\|warn"
```

#### Monthly Maintenance

- Review Arch Linux forums/wiki for new hibernation fixes
- Check for kernel updates with improved LUKS/NVMe support
- Document any new issues in this ADR

## Consequences

### If Successful (Expected)

**Positive:**

- ✅ Reliable daily hibernation with full encryption
- ✅ Battery drain eliminated during hibernation (vs. modern sleep)
- ✅ Fast resume compared to boot (15-30 seconds)
- ✅ Session preservation (open applications, unsaved work)
- ✅ No security trade-offs (full LUKS protection maintained)

**Neutral:**

- Resume time may be 5-10 seconds slower than unencrypted hibernation
- Requires vigilant monitoring for first 2 weeks
- Must keep this ADR updated with findings

**Negative:**

- Small risk of rare resume failures (inherent to LUKS hibernation)
- NVMe power saving slightly reduced (minor battery impact when *not* hibernating)

### If Unsuccessful (Contingency)

**If NMI errors continue:**

1. **Document failure details** - Update this ADR with specific error patterns
2. **Re-evaluate constraints** - Determine if repartitioning risk is acceptable
3. **Consider Option 3** - Hybrid swap as last resort
4. **Upstream engagement** - File kernel bug report with NMI details
5. **Hardware check** - Verify if NVMe firmware updates available

**If Option 2 fails, must choose:**

- **Accept Option 3** (hybrid swap with repartitioning risk)
- **Disable hibernation** (accept modern sleep battery drain)
- **Investigate S3 sleep** (check if BIOS update enables it)

## References

### Arch Linux Wiki

- **Power management/Suspend and hibernate**
  [https://wiki.archlinux.org/title/Power_management/Suspend_and_hibernate](https://wiki.archlinux.org/title/Power_management/Suspend_and_hibernate)
  Comprehensive guide to sleep states and hibernation setup

- **Dm-crypt/Swap encryption**
  [https://wiki.archlinux.org/title/Dm-crypt/Swap_encryption](https://wiki.archlinux.org/title/Dm-crypt/Swap_encryption)
  Encrypted swap configuration and hibernation considerations

- **Mkinitcpio**
  [https://wiki.archlinux.org/title/Mkinitcpio](https://wiki.archlinux.org/title/Mkinitcpio)
  Initramfs hook order and configuration

- **Solid State Drives/NVMe**
  [https://wiki.archlinux.org/title/Solid_State_Drives/NVMe](https://wiki.archlinux.org/title/Solid_State_Drives/NVMe)
  NVMe power state management and troubleshooting

### Kernel Documentation

- **Kernel Parameters**
  `no_console_suspend` - Documented in `kernel-parameters.txt`
  `nvme_core.default_ps_max_latency_us` - Documented in `nvme-core.rst`

### Related Issues

- **NMI during resume:** Common with NVMe APST (Autonomous Power State Transition)
- **LUKS hibernation:** Known complexity due to encryption layer in resume path
- **VirtualBox after resume:** Kernel modules sensitive to hardware state changes

## Appendix: NMI Error Analysis

**Error Message:**

```text
Mar 12 08:32:00 kernel: Uhhuh. NMI received for unknown reason 30 on CPU 0.
Mar 12 08:32:00 kernel: Dazed and confused, but trying to continue
```

**NMI Reason Code 30 (0x1E in hex):**

- Non-standard reason code (not in typical NMI reason list)
- Likely hardware-specific interrupt from chipset or NVMe controller
- Timing (19 seconds after resume) suggests device reinitialization issue

**Why NVMe Power States Matter:**

- NVMe drives enter autonomous power states during hibernation
- During resume, drive must transition back to active state
- If timing is wrong, drive may not be ready when kernel needs it
- This can trigger chipset-level NMI as emergency signal
- Disabling APST forces drive to stay in safe power states

**Why Console Matters:**

- Console suspend can freeze kernel logging subsystem
- Hardware errors during resume may not be properly handled
- `no_console_suspend` keeps error reporting active
- Helps kernel recover from unexpected hardware states

## Update Log

- **2026-03-12:** Initial draft based on March 12 freeze incident
- **2026-03-12:** Recommended Option 2 based on user constraints
