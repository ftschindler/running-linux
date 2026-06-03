---
title: Memory Fragmentation Mitigation to Prevent System Freezes
---

**Date:** 2026-04-15
**Context:** Manjaro Linux with KDE Plasma on Dell Precision 5470, Intel i7-12800H, 32GB RAM

## Problem Statement

The system experienced a complete freeze on April 15, 2026, at approximately 13:13. Investigation revealed a kernel memory allocation failure at 11:00:05 AM due to **memory fragmentation**:

**Incident Details:**

```text
Apr 15 11:00:05 kernel: upowerd: page allocation failure: order:4, mode:0x40cc0(GFP_KERNEL|__GFP_COMP)
Apr 15 11:00:05 kernel: Node 0 Normal free:259928kB boost:192052kB min:257408kB
Apr 15 11:00:05 kernel: Free swap = 62087756kB
Apr 15 11:00:05 kernel: Total swap = 67108860kB
```

**Root Cause:**

Despite having ~400MB free RAM and 62GB free swap, the kernel could not allocate **64KB of contiguous physical memory** (order:4 pages) due to memory fragmentation. This triggered kernel instability in the Dell laptop drivers, eventually leading to a complete system freeze approximately 2 hours later.

**Contributing Factors:**

- Memory fragmentation from long uptime with VirtualBox usage
- Transparent Huge Pages (THP) set to "always" mode (default) increases fragmentation
- No proactive memory pressure handling (earlyoom/systemd-oomd not configured)
- VirtualBox kernel modules running under memory pressure
- System uptime: ~4 hours before failure (9:24 AM boot → 13:13 freeze)

## Current Configuration

```bash
# Current THP setting
$ cat /sys/kernel/mm/transparent_hugepage/enabled
[always] madvise never

# Current swappiness
$ cat /proc/sys/vm/swappiness
60

# Memory at time of failure
Free RAM: ~400MB
Free swap: ~62GB (out of 64GB)
Memory in swap cache: 305,426 pages (~1.2GB)
```

## Solution

Implement a two-pronged approach to handle memory fragmentation proactively:

1. **Reduce THP-induced fragmentation** via kernel parameter
2. **Install earlyoom** to handle memory pressure before kernel panic

## Implementation

### Part 1: Configure Transparent Huge Pages (THP)

**Objective:** Reduce memory fragmentation by using THP only when applications explicitly request it.

```bash
# 1. Backup current GRUB configuration
sudo cp /etc/default/grub /etc/default/grub.backup-$(date +%Y%m%d)

# 2. Edit GRUB configuration
sudo nano /etc/default/grub

# 3. Add to GRUB_CMDLINE_LINUX_DEFAULT (append to existing parameters):
#    transparent_hugepage=madvise
#
# Full line should look like:
# GRUB_CMDLINE_LINUX_DEFAULT="quiet udev.log_priority=3 cryptdevice=UUID=5af18995-b106-4b9e-8e73-c43593bd45ec:linux-crypt root=/dev/linux-crypt-vg/root resume=/dev/linux-crypt-vg/swap no_console_suspend nvme_core.default_ps_max_latency_us=0 transparent_hugepage=madvise"

# 4. Update GRUB
sudo grub-mkconfig -o /boot/grub/grub.cfg

# 5. Reboot to apply
sudo reboot
```

**What this does:**

- `transparent_hugepage=always` (default): Kernel aggressively merges pages into 2MB huge pages, causing fragmentation
- `transparent_hugepage=madvise`: THP only used when applications request it via madvise(), reducing fragmentation
- Applications like VirtualBox can still use huge pages explicitly

### Part 2: Install and Configure earlyoom

**Objective:** Gracefully handle memory pressure by freeing memory before kernel OOM killer or allocation failures occur.

```bash
# 1. Install earlyoom
sudo pacman -S earlyoom

# 2. Configure earlyoom (optional - adjust thresholds)
sudo nano /etc/default/earlyoom

# Recommended settings:
# EARLYOOM_ARGS="-r 3600 -m 5 -s 10 --avoid '(^|/)(init|systemd|Xorg|sddm|plasmashell)$' --prefer '(^|/)(VBoxHeadless|chromium|firefox)$'"
#
# Explanation:
# -r 3600    : Report memory status every hour
# -m 5       : Trigger at 5% available memory
# -s 10      : Trigger at 10% available swap
# --avoid    : Don't kill critical system processes
# --prefer   : Prefer killing VirtualBox VMs and browsers first

# 3. Enable and start earlyoom
sudo systemctl enable earlyoom.service
sudo systemctl start earlyoom.service

# 4. Verify it's running
systemctl status earlyoom.service
journalctl -u earlyoom.service -f
```

### Monitoring Commands

```bash
# Check THP setting after reboot
cat /sys/kernel/mm/transparent_hugepage/enabled
# Should show: always [madvise] never

# Check kernel command line
cat /proc/cmdline | grep transparent_hugepage

# Monitor earlyoom activity
journalctl -u earlyoom.service --since today

# Check for memory allocation failures
journalctl -b -k | grep "page allocation failure"

# Monitor memory fragmentation
cat /proc/buddyinfo

# Check memory stats
cat /proc/meminfo | grep -E "(MemFree|MemAvailable|AnonHugePages|ShmemHugePages)"

# Monitor system memory pressure
cat /proc/pressure/memory
```

## Trade-offs

### Transparent Hugepage = madvise

**Benefits:**

- ✅ Reduced memory fragmentation
- ✅ More reliable memory allocations under pressure
- ✅ Applications can still opt-in to huge pages
- ✅ Better for mixed workloads (desktop + VMs)

**Drawbacks:**

- ⚠️ Slightly reduced performance for applications that benefit from THP but don't request it
- ⚠️ Applications must explicitly use madvise() to get huge pages

### earlyoom

**Benefits:**

- ✅ Prevents kernel panic and freezes from memory pressure
- ✅ Graceful memory reclamation before critical failure
- ✅ Configurable to protect critical processes
- ✅ Can prefer killing less important processes (browsers, VMs)

**Drawbacks:**

- ⚠️ May kill VirtualBox VMs or browsers under memory pressure (but prevents total freeze)
- ⚠️ Requires tuning thresholds for your workload
- ⚠️ Additional background service (minimal overhead)

## Expected Outcome

1. **Reduced fragmentation:** `transparent_hugepage=madvise` will reduce memory fragmentation from THP defragmentation attempts
2. **Proactive handling:** earlyoom will free memory before kernel allocation failures occur
3. **Graceful degradation:** If memory pressure occurs, earlyoom kills less critical processes instead of system freeze
4. **Better stability:** VirtualBox usage under normal conditions should not trigger allocation failures

## Alternative: systemd-oomd

If you prefer systemd's built-in solution:

```bash
# Enable systemd-oomd (included in systemd)
sudo systemctl enable systemd-oomd.service
sudo systemctl start systemd-oomd.service

# Configure memory pressure thresholds (optional)
sudo mkdir -p /etc/systemd/oomd.conf.d/
sudo nano /etc/systemd/oomd.conf.d/custom.conf

# Add:
# [OOM]
# DefaultMemoryPressureLimit=5%
```

**Note:** earlyoom is generally preferred for desktop workloads as it's more configurable and aggressive.

## References

- [Kernel Documentation: Transparent Hugepages](https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html)
- [Arch Wiki: Improving performance - Memory fragmentation](https://wiki.archlinux.org/title/Improving_performance#Memory_fragmentation)
- [earlyoom GitHub](https://github.com/rfjakob/earlyoom)
- [systemd-oomd documentation](https://www.freedesktop.org/software/systemd/man/systemd-oomd.service.html)

## Implementation Notes

- These changes are **complementary** to the Dell keyboard backlight polling fix
- Can be implemented independently or together
- Start with Part 1 (THP), then add Part 2 (earlyoom) if issues persist
- Monitor system for 1-2 weeks to assess effectiveness
