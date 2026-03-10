# ADR: Power and Thermal Management Strategy

**Date:** 2026-03-10
**Status:** Proposed
**Context:** Manjaro Linux with KDE Plasma on LUKS+LVM, Intel 12th Gen i7-12800H

## Problem Statement

The system has experienced freezes in the past due to power and thermal issues. A comprehensive power and thermal management solution is needed that:

1. Prevents thermal-induced system freezes
2. Provides user-friendly power controls
3. Optimizes battery life without sacrificing stability
4. Works reliably with LUKS+LVM storage setup

## System Information

- **CPU:** Intel Core i7-12800H (Alder Lake, 12th Gen, 14 cores)
- **GPU:** Intel Iris Xe Graphics (integrated)
- **RAM:** 32 GB (30 GiB usable)
- **Platform:** Manjaro Linux (rolling release)
- **Desktop:** KDE Plasma 6.5.5 with Powerdevil
- **Storage:** LUKS + LVM (NVMe with encrypted root and swap)
- **Swap:** 64 GB encrypted partition on LVM
- **Thermal Zones:** 14 thermal zones detected (CPU, memory, WiFi, sensors)

## Decision

Implement a layered power and thermal management approach with five complementary components:

### Layer 1: KDE Powerdevil (User Interface)

**Role:** User-facing power controls and profile switching

**Responsibilities:**

- CPU frequency scaling via GUI
- Display brightness management
- Screen timeout and sleep settings
- Battery/AC profile switching
- Keyboard backlight control

**Configuration:** System Settings → Power Management

### Layer 2: TLP (Advanced Power Management)

**Role:** Automatic device and system power optimization

**Responsibilities:**

- CPU governor and frequency management
- USB power control and autosuspend
- PCI/PCIe power saving (ASPM)
- Battery charge thresholds
- Disk I/O scheduler optimization
- WiFi power management
- Intel GPU frequency scaling
- Runtime power management for devices

**Configuration:** `/etc/tlp.conf` (see below)

### Layer 3: thermald (Thermal Protection)

**Role:** Proactive thermal management and emergency throttling

**Responsibilities:**

- Monitor all thermal zones
- Proactive thermal throttling before critical temps
- Prevent thermal-induced freezes
- Intel-specific thermal optimizations

**Configuration:** `/etc/thermald/thermal-conf.xml` (see below)

### Layer 4: Kernel Parameters

**Role:** Low-level system optimizations

**Responsibilities:**

- Enable Intel P-state driver
- GPU power saving features
- System watchdog for freeze detection
- IOMMU for device isolation

**Configuration:** GRUB kernel command line

### Layer 5: Memory Management (Swap)

**Role:** Prevent memory-pressure-induced freezes and optimize I/O performance

**Responsibilities:**

- Configure swap usage thresholds (swappiness)
- Optimize cache pressure for LUKS+LVM I/O
- Prevent excessive swap thrashing
- Balance memory reclamation policies

**Current Configuration:**

- **RAM:** 32 GB (30 GiB)
- **Swap:** 64 GB on encrypted LVM (`/dev/dm-1`)
- **Current swappiness:** 60 (default, too aggressive)
- **Current vfs_cache_pressure:** 100 (default)

**Problem:** With LUKS encryption, swap I/O is expensive. Default swappiness of 60 causes the kernel to swap aggressively even when RAM is available, leading to:

1. Increased disk I/O (expensive on encrypted volumes)
2. Higher CPU usage (encryption/decryption overhead)
3. Potential thermal issues from sustained I/O
4. System stuttering during memory pressure
5. Possible freezes when swap thrashing occurs

**Configuration:** `sysctl` parameters (see below)

## Implementation Plan

### Step 1: Remove Conflicts

```bash
# Disable power-profiles-daemon (conflicts with TLP)
sudo systemctl stop power-profiles-daemon
sudo systemctl disable power-profiles-daemon
sudo systemctl mask power-profiles-daemon
```

**Rationale:** TLP and power-profiles-daemon conflict. TLP provides more granular control needed for thermal management. See [Arch Wiki: TLP](https://wiki.archlinux.org/title/TLP) for details.

### Step 2: Install Required Packages

```bash
sudo pacman -S tlp tlp-rdw thermald cpupower acpi_call \
               lm_sensors powertop
```

**Package purposes:**

- `tlp` + `tlp-rdw`: Advanced power management with NetworkManager integration
- `thermald`: Intel thermal management daemon
- `cpupower`: CPU frequency utilities (used by Powerdevil)
- `acpi_call`: Battery threshold control for laptops
- `lm_sensors`: Hardware temperature monitoring
- `powertop`: Power consumption analysis tool

### Step 3: TLP Configuration

Create `/etc/tlp.conf` with the following key settings.

For complete documentation, see [TLP Configuration](https://linrunner.de/tlp/settings/) and [Arch Wiki: TLP](https://wiki.archlinux.org/title/TLP).

```conf
# ===== CPU Performance vs Power =====

# Governors: performance on AC for responsiveness, powersave on battery
CPU_SCALING_GOVERNOR_ON_AC=performance
CPU_SCALING_GOVERNOR_ON_BAT=powersave

# Frequency limits (in kHz)
# Allow Powerdevil to control within these bounds
CPU_SCALING_MIN_FREQ_ON_AC=800000
CPU_SCALING_MAX_FREQ_ON_AC=4800000
CPU_SCALING_MIN_FREQ_ON_BAT=800000
CPU_SCALING_MAX_FREQ_ON_BAT=3600000

# Intel P-state Energy/Performance Preference (EPP)
# performance: Maximum performance
# balance_power: Balanced (recommended for battery)
CPU_ENERGY_PERF_POLICY_ON_AC=performance
CPU_ENERGY_PERF_POLICY_ON_BAT=balance_power

# ===== Turbo Boost Control =====
# Disable on battery to prevent thermal issues
CPU_BOOST_ON_AC=1
CPU_BOOST_ON_BAT=0

# Hardware P-States (HWP) dynamic boost for Alder Lake
CPU_HWP_DYN_BOOST_ON_AC=1
CPU_HWP_DYN_BOOST_ON_BAT=0

# ===== Platform Profiles =====
# ACPI platform profile for firmware-level power management
PLATFORM_PROFILE_ON_AC=balanced
PLATFORM_PROFILE_ON_BAT=low-power

# ===== Disk I/O Optimization =====
# Important: mq-deadline scheduler for better LVM/LUKS performance
# Reduces latency spikes that can cause perceived freezes
DISK_IOSCHED="mq-deadline mq-deadline"

# ===== PCIe Power Management =====
PCIE_ASPM_ON_AC=default
PCIE_ASPM_ON_BAT=powersupersave

# ===== Intel GPU Power Management =====
# Conservative limits to prevent thermal issues
INTEL_GPU_MIN_FREQ_ON_AC=300
INTEL_GPU_MIN_FREQ_ON_BAT=300
INTEL_GPU_MAX_FREQ_ON_AC=1400
INTEL_GPU_MAX_FREQ_ON_BAT=800
INTEL_GPU_BOOST_FREQ_ON_AC=1400
INTEL_GPU_BOOST_FREQ_ON_BAT=800

# ===== WiFi Power Saving =====
WIFI_PWR_ON_AC=off
WIFI_PWR_ON_BAT=on

# ===== USB Autosuspend =====
USB_AUTOSUSPEND=1
# Add problematic USB device IDs here
USB_DENYLIST=""

# ===== Battery Care (Dell laptops) =====
# Keep battery between 75-80% for longevity
# Adjust or disable if not applicable
START_CHARGE_THRESH_BAT0=75
STOP_CHARGE_THRESH_BAT0=80

# ===== Runtime Power Management =====
RUNTIME_PM_ON_AC=auto
RUNTIME_PM_ON_BAT=auto

# ===== Audio Power Saving =====
SOUND_POWER_SAVE_ON_AC=0
SOUND_POWER_SAVE_ON_BAT=1
```

**Key design decisions:**

- **Turbo boost disabled on battery**: Primary thermal protection mechanism
- **mq-deadline I/O scheduler**: Reduces latency for encrypted LVM volumes
- **Conservative GPU frequencies**: Prevents thermal runaway on integrated graphics
- **Balanced platform profiles**: Firmware-level thermal cooperation

### Step 4: thermald Configuration

Create `/etc/thermald/thermal-conf.xml`.

For more information, see [thermald documentation](https://github.com/intel/thermal_daemon) and [Arch Wiki: thermald](https://wiki.archlinux.org/title/Thermald).

```xml
<?xml version="1.0"?>
<ThermalConfiguration>
  <Platform>
    <Name>Manjaro Intel 12th Gen</Name>
    <ProductName>*</ProductName>
    <Preference>QUIET</Preference>
    <ThermalZones>
      <ThermalZone>
        <Type>x86_pkg_temp</Type>
        <TripPoints>
          <!-- First trip point: Start power clamping at 75°C -->
          <TripPoint>
            <SensorType>x86_pkg_temp</SensorType>
            <Temperature>75000</Temperature>
            <type>passive</type>
            <CoolingDevice>
              <index>1</index>
              <type>intel_powerclamp</type>
              <influence>100</influence>
              <SamplingPeriod>5</SamplingPeriod>
            </CoolingDevice>
          </TripPoint>
          <!-- Second trip point: CPU frequency throttling at 85°C -->
          <TripPoint>
            <SensorType>x86_pkg_temp</SensorType>
            <Temperature>85000</Temperature>
            <type>passive</type>
            <CoolingDevice>
              <index>1</index>
              <type>intel_pstate</type>
              <influence>100</influence>
              <SamplingPeriod>2</SamplingPeriod>
            </CoolingDevice>
          </TripPoint>
        </TripPoints>
      </ThermalZone>
    </ThermalZones>
  </Platform>
</ThermalConfiguration>
```

**Thermal strategy:**

1. **75°C threshold**: Begin power clamping (reduces package power without frequency throttling)
2. **85°C threshold**: Aggressive CPU frequency reduction
3. **Goal**: Never reach 95°C+ where thermal shutdowns and freezes occur

**Rationale:** Proactive intervention prevents reaching critical temperatures. Power clamping is less disruptive than frequency throttling.

### Step 5: Kernel Parameters

Edit `/etc/default/grub` and add to `GRUB_CMDLINE_LINUX_DEFAULT`.

For more details on kernel parameters, see [Arch Wiki: Kernel parameters](https://wiki.archlinux.org/title/Kernel_parameters) and [Arch Wiki: CPU frequency scaling](https://wiki.archlinux.org/title/CPU_frequency_scaling).

```text
intel_pstate=active intel_iommu=on i915.enable_fbc=1 i915.enable_psr=2 watchdog.timeout=30
```

**Parameter breakdown:**

- `intel_pstate=active`: Use Intel P-state driver (required for Alder Lake hybrid architecture)
- `intel_iommu=on`: Enable IOMMU for better device isolation and DMA protection
- `i915.enable_fbc=1`: Frame Buffer Compression (reduces memory bandwidth, saves power)
- `i915.enable_psr=2`: Panel Self Refresh v2 (display power saving)
- `watchdog.timeout=30`: Hardware watchdog to detect and recover from freezes

After editing, regenerate GRUB config:

```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### Step 6: Enable Services

```bash
# Enable and start TLP
sudo systemctl enable tlp.service
sudo systemctl start tlp.service

# Enable and start thermald
sudo systemctl enable thermald.service
sudo systemctl start thermald.service

# Enable NetworkManager dispatcher for TLP
sudo systemctl enable NetworkManager-dispatcher.service

# Mask systemd-rfkill to prevent conflicts with TLP
sudo systemctl mask systemd-rfkill.service
sudo systemctl mask systemd-rfkill.socket
```

### Step 7: KDE Powerdevil Configuration

Configure via **System Settings → Power Management**

**Recommended profile settings:**

**AC Power Profile:**

- CPU: Performance governor
- Display: Full brightness
- Suspend: After 30 minutes of inactivity
- Display dim/off: After 15 minutes

**Battery Profile:**

- CPU: Powersave governor
- Display: 60-70% brightness
- Suspend: After 15 minutes of inactivity
- Display dim/off: After 5 minutes

**Low Battery Profile (<20%):**

- CPU: Powersave governor
- Display: 50% brightness
- Suspend: After 5 minutes of inactivity
- Display dim/off: After 2 minutes

**Note:** Powerdevil and TLP coexist because:

- TLP sets baseline governors and limits
- Powerdevil can override current governor selection
- TLP respects manual cpufreq changes
- Profile switching triggers TLP to reapply AC/battery settings

### Step 8: Configure Swap and Memory Management

**Current situation:**

- 32 GB RAM with 64 GB encrypted swap
- Swappiness: 60 (kernel default, too aggressive)
- VFS cache pressure: 100 (default)

**Problem:** Aggressive swapping on encrypted volumes causes:

- High encryption/decryption CPU overhead → thermal issues
- Increased disk I/O → power consumption
- System stuttering and potential freezes during memory pressure

**Solution:** Optimize for minimal swap usage while preventing OOM situations.

For background on swap configuration, see [Arch Wiki: Swap](https://wiki.archlinux.org/title/Swap) and [Arch Wiki: Improving performance](https://wiki.archlinux.org/title/Improving_performance).

Create `/etc/sysctl.d/99-swap-memory.conf`:

```conf
# ===== Swap Management =====

# Swappiness: How aggressively kernel swaps memory pages
# Default: 60 (too aggressive for systems with adequate RAM)
# Range: 0-200 (0 = avoid swap, 100 = default, 200 = aggressive)
#
# Recommended: 10 for 32GB RAM systems
# - Keeps working set in RAM
# - Only swaps when necessary (>90% RAM usage)
# - Reduces LUKS encryption overhead
# - Improves thermal profile (less I/O = less CPU for crypto)
vm.swappiness=10

# VFS Cache Pressure: How aggressively kernel reclaims inode/dentry cache
# Default: 100 (balanced)
# Range: 0-infinity (lower = keep more filesystem cache)
#
# Recommended: 50 for encrypted systems with good RAM
# - Prioritizes keeping filesystem metadata in cache
# - Reduces repeated LUKS decryption of directory structures
# - Important for LVM performance (metadata-heavy)
# - Improves perceived responsiveness
vm.vfs_cache_pressure=50

# Dirty ratio: Percentage of RAM that can be filled with dirty pages
# before forcing synchronous writes
# Default: 20 (20% of 32GB = 6.4GB can be dirty)
#
# Recommended: 10 for encrypted volumes
# - Prevents large write bursts (thermal spike prevention)
# - More frequent smaller writes = better thermal distribution
# - Reduces risk of data loss
# - Helps avoid I/O storms that trigger thermal throttling
vm.dirty_ratio=10

# Dirty background ratio: When background writeback starts
# Default: 10
#
# Recommended: 5 for encrypted volumes
# - Earlier background writeback
# - Smoother I/O distribution over time
# - Prevents accumulation of large dirty buffers
# - Reduces peak thermal load from write bursts
vm.dirty_background_ratio=5

# ===== Memory Overcommit =====

# Overcommit handling: How kernel handles memory allocation requests
# 0 = heuristic (default) - allow reasonable overcommit
# 1 = always allow overcommit
# 2 = never overcommit (strict)
#
# Keep default (0) - good balance for desktop systems
vm.overcommit_memory=0

# Overcommit ratio: Percentage of RAM to consider when overcommit_memory=2
# Only relevant if switching to strict mode
# vm.overcommit_ratio=50

# ===== Out-of-Memory (OOM) Behavior =====

# OOM kill allocating task: Kill the task that triggered OOM
# 0 = kill based on badness score (default)
# 1 = kill the allocating task
#
# Keep default - better system stability
vm.oom_kill_allocating_task=0

# Panic on OOM: Reboot system on OOM (useful for servers, not desktops)
# 0 = kill processes (default, recommended for desktop)
# 1 = panic and reboot
vm.panic_on_oom=0
```

**Apply configuration:**

For more on sysctl configuration, see [Arch Wiki: sysctl](https://wiki.archlinux.org/title/Sysctl).

```bash
# Create the configuration file (use editor or cat)
sudo nano /etc/sysctl.d/99-swap-memory.conf

# Apply immediately without reboot
sudo sysctl -p /etc/sysctl.d/99-swap-memory.conf

# Verify settings
sysctl vm.swappiness vm.vfs_cache_pressure vm.dirty_ratio vm.dirty_background_ratio
```

**Expected behavior after configuration:**

- **Swap usage**: Only when RAM usage exceeds ~90%
- **Filesystem cache**: More persistent, fewer LUKS decryptions
- **Write patterns**: Smaller, more frequent (better thermal distribution)
- **System responsiveness**: Improved under memory pressure
- **Thermal profile**: Lower CPU usage from reduced encryption overhead

**Rationale for values:**

1. **swappiness=10**: With 32GB RAM, swap should be last resort
   - Most desktop workloads fit in 32GB
   - Encrypted swap I/O is expensive (CPU + disk)
   - Better to keep working set in RAM
   - Only swap inactive pages when truly necessary

2. **vfs_cache_pressure=50**: Favor keeping filesystem metadata cached
   - LUKS makes directory traversal expensive
   - LVM metadata lookups are frequent
   - Caching reduces repeated decryption
   - Especially important for development workflows

3. **dirty_ratio=10 / dirty_background_ratio=5**: Smooth write distribution
   - Prevents large write bursts that spike thermals
   - 10% of 32GB = 3.2GB buffer (still generous)
   - More predictable I/O patterns
   - Helps thermal management stay ahead of load

**Alternative values for different scenarios:**

**Low RAM scenario (8-16GB):**

```conf
vm.swappiness=60          # Need to use swap more
vm.vfs_cache_pressure=100 # Default balance
vm.dirty_ratio=15
vm.dirty_background_ratio=10
```

**SSD without encryption:**

```conf
vm.swappiness=20          # Less expensive swap I/O
vm.vfs_cache_pressure=100 # Less benefit from caching
vm.dirty_ratio=20         # Can handle bursts better
vm.dirty_background_ratio=10
```

**Extreme performance (ignore thermal):**

```conf
vm.swappiness=200         # Very aggressive swapping
vm.vfs_cache_pressure=200 # Aggressive cache reclaim
vm.dirty_ratio=40         # Large write buffers
vm.dirty_background_ratio=20
```

## Component Interplay

### How the layers work together

```text
User adjusts power → Powerdevil → cpufreq subsystem
                                        ↓
AC/Battery switch → TLP → Applies baseline policies → Respects Powerdevil settings
                                        ↓
Temperature rise → thermald → Emergency throttling only when needed
                                        ↓
Memory pressure → Kernel VM → Consults swappiness/cache settings → Minimal swap usage
                                        ↓
All policies enforced by Linux kernel (cpufreq, thermal, PM, VM subsystems)
```

### Conflict prevention

1. **TLP vs Powerdevil:** No conflict
   - TLP uses `CPU_SCALING_GOVERNOR` which Powerdevil can override
   - TLP reapplies settings only on power source changes
   - Both write to same sysfs interfaces in cooperative manner

2. **thermald vs TLP:** No conflict
   - thermald monitors temperatures passively
   - Only intervenes during thermal emergencies
   - TLP manages power, thermald manages thermal safety

3. **Kernel parameters:** Foundation for all tools
   - `intel_pstate=active` required for both TLP and Powerdevil
   - GPU parameters apply independently

4. **Memory management (swap):** No conflicts, complements thermal management
   - Low swappiness reduces LUKS encryption overhead (less CPU usage)
   - Reduced I/O from swap = lower power consumption
   - Better cache behavior improves perceived performance
   - Prevents memory-pressure-induced freezes
   - Works independently of other power/thermal tools

## Verification and Monitoring

### Check TLP status

```bash
sudo tlp-stat -s    # Summary
sudo tlp-stat -b    # Battery information
sudo tlp-stat -t    # Temperatures
sudo tlp-stat -p    # Processor
```

### Monitor temperatures

```bash
watch -n 2 sensors
```

### Check thermal events

```bash
journalctl -u thermald -f
```

### Power consumption analysis

```bash
sudo powertop  # Interactive power analysis
```

### CPU frequency monitoring

```bash
watch -n 1 "grep MHz /proc/cpuinfo"
```

### Verify TLP is managing devices

```bash
sudo tlp-stat --processor
sudo tlp-stat --graphics
sudo tlp-stat --usb
```

### Monitor swap and memory usage

```bash
# Real-time memory and swap monitoring
watch -n 2 "free -h && echo && swapon --show"

# Check current sysctl values
sysctl vm.swappiness vm.vfs_cache_pressure vm.dirty_ratio vm.dirty_background_ratio

# Monitor swap activity (pages in/out per second)
vmstat 2

# Detailed memory statistics
cat /proc/meminfo | grep -E "Mem|Swap|Dirty|Writeback"

# Check if swap is causing I/O pressure
iostat -x 2  # Watch for high utilization on dm-1 (swap device)
```

## Troubleshooting

### If freezes still occur

1. **Check for thermal throttling events:**

   ```bash
   sudo journalctl -b | grep -i "thermal\|throttl"
   ```

2. **Lower thermal thresholds** in `/etc/thermald/thermal-conf.xml`:
   - Try 70°C for power clamping
   - Try 80°C for frequency throttling

3. **Disable turbo boost entirely** in `/etc/tlp.conf`:

   ```conf
   CPU_BOOST_ON_AC=0
   CPU_BOOST_ON_BAT=0
   ```

4. **Check system logs during/after freeze:**

   ```bash
   sudo journalctl -b -1     # Previous boot
   sudo journalctl -b        # Current boot
   ```

5. **Enable kernel panic on soft lockup** (creates crash dump):

   ```bash
   echo "kernel.softlockup_panic=1" | sudo tee /etc/sysctl.d/99-watchdog.conf
   sudo sysctl -p /etc/sysctl.d/99-watchdog.conf
   ```

6. **Check for hardware issues:**

   ```bash
   # Check memory errors
   sudo journalctl -b | grep -i "mce\|machine check"

   # Check disk errors (important for LUKS+LVM)
   sudo journalctl -b | grep -i "ata\|nvme\|error"
   ```

7. **Verify LUKS+LVM performance:**

   ```bash
   # Check if disk latency is causing issues
   sudo iotop -o
   ```

### Common issues

**Problem:** TLP not applying settings
**Solution:** Check for conflicts with `power-profiles-daemon`:

```bash
systemctl status power-profiles-daemon  # Should be masked
```

**Problem:** thermald not starting
**Solution:** Check thermal zones exist:

```bash
ls /sys/class/thermal/thermal_zone*/type
```

**Problem:** Battery thresholds not working
**Solution:** Check if `acpi_call` module is loaded:

```bash
lsmod | grep acpi_call
sudo modprobe acpi_call
```

**Problem:** Powerdevil not showing CPU frequency options
**Solution:** Ensure `cpupower` is installed and `intel_pstate` is active:

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

**Problem:** System freezing under memory pressure
**Solution:** Check swap thrashing and adjust swappiness:

```bash
# Check current swap usage and activity
vmstat 2 10  # Watch 'si' and 'so' columns (swap in/out)

# If swap activity is high (>1000 pages/sec sustained)
# Lower swappiness further
echo "vm.swappiness=5" | sudo tee -a /etc/sysctl.d/99-swap-memory.conf
sudo sysctl -p /etc/sysctl.d/99-swap-memory.conf

# If OOM killer is triggering frequently
sudo journalctl -b | grep -i "out of memory\|oom"
# Consider increasing swappiness back to 20
```

**Problem:** High CPU usage from kswapd (swap daemon)
**Solution:** System is thrashing, reduce memory usage or adjust settings:

```bash
# Check what's using memory
ps aux --sort=-%mem | head -20

# Temporarily clear caches to free memory
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# If problem persists, increase swappiness temporarily
echo 20 | sudo tee /proc/sys/vm/swappiness
```

**Problem:** Slow system after resume from suspend/hibernate
**Solution:** Swap may need to be read back into RAM:

```bash
# Check swap usage after resume
swapon --show

# If swap is heavily used, consider disabling hibernation
# or reducing swappiness to prevent swapping before sleep
```

## Expected Outcomes

After implementing this plan:

✓ **Thermal stability:** System should not exceed 85°C under normal load
✓ **No thermal freezes:** Proactive throttling prevents critical temperatures
✓ **User control:** Easy power profile switching via KDE interface
✓ **Automatic optimization:** TLP manages power without user intervention
✓ **Battery longevity:** Charge thresholds and power management extend battery life
✓ **Performance on demand:** Performance mode available when plugged in
✓ **LUKS+LVM optimized:** I/O scheduler tuned for encrypted volumes
✓ **Minimal swap usage:** Reduced encryption overhead and thermal load
✓ **Better responsiveness:** Optimized cache behavior for encrypted filesystem
✓ **Stable under memory pressure:** No freezes from swap thrashing

## Trade-offs

**Advantages:**

- Comprehensive thermal protection
- User-friendly interface (Powerdevil)
- Automatic power optimization (TLP)
- Proven stability on Arch-based systems
- Fine-grained control over all power states
- Optimized for encrypted storage (LUKS+LVM)
- Reduced thermal load from minimal swap usage
- Better memory management prevents freeze conditions

**Disadvantages:**

- Slightly more complex than single-tool solutions
- Requires manual configuration file editing
- Need to understand interaction between components
- May reduce maximum performance on battery (by design)
- Low swappiness may cause OOM on systems with <16GB RAM
- Requires monitoring to tune swap settings for specific workloads

## Alternatives Considered

### Alternative 1: Powerdevil only

**Rejected:** Insufficient granularity for thermal management, no per-device power control

### Alternative 2: TLP only (no Powerdevil)

**Rejected:** Poor user experience, no GUI for profile switching

### Alternative 3: power-profiles-daemon + Powerdevil

**Rejected:** Less granular than TLP, insufficient control for thermal issues

### Alternative 4: auto-cpufreq

**Rejected:** Conflicts with Powerdevil, less mature than TLP, fewer device controls

### Alternative 5: zram instead of swap partition

**Considered:** Compressed RAM (zram) instead of encrypted swap partition

**Analysis:**

- **Pros:** Lower latency, no disk I/O, no encryption overhead
- **Cons:** Reduces available RAM, compression CPU overhead, limited by RAM size
- **Decision:** Keep encrypted swap for now, but zram is viable alternative

**When to consider zram:**

- Primary concern is I/O latency, not capacity
- CPU is underutilized (compression is cheap)
- Want faster suspend/resume
- Willing to sacrifice some RAM for performance

**Implementation note:** Can be added alongside swap partition for hybrid approach

### Alternative 6: Disable swap entirely

**Considered:** Remove swap partition completely

**Analysis:**

- **Pros:** Zero encryption overhead, no thermal load from swap
- **Cons:** Risk of OOM killer, no hibernate support, system crashes under memory pressure
- **Decision:** Rejected - 32GB RAM is not enough to guarantee no memory pressure

**When to consider:**

- 64GB+ RAM systems
- Workloads with predictable memory usage
- Hibernation not needed
- Aggressive OOM killer acceptable

## References

### Official Documentation

- [TLP Documentation](https://linrunner.de/tlp/) - Complete TLP configuration guide
- [TLP FAQ](https://linrunner.de/tlp/faq/) - Common questions and troubleshooting
- [thermald GitHub](https://github.com/intel/thermal_daemon) - Intel thermal daemon source and documentation
- [Intel P-state Driver Documentation](https://www.kernel.org/doc/html/latest/admin-guide/pm/intel_pstate.html) - Kernel P-state documentation
- [Linux Memory Management Documentation](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/vm.html) - Kernel VM sysctl parameters
- [Powerdevil Documentation](https://userbase.kde.org/Power_Management) - KDE power management

### Arch Wiki Articles

- [Power management](https://wiki.archlinux.org/title/Power_management) - Overview of power management on Linux
- [CPU frequency scaling](https://wiki.archlinux.org/title/CPU_frequency_scaling) - CPU governor and frequency configuration
- [Swap](https://wiki.archlinux.org/title/Swap) - Swap configuration and optimization
- [Improving performance](https://wiki.archlinux.org/title/Improving_performance) - System performance tuning
- [dm-crypt/Encrypting an entire system](https://wiki.archlinux.org/title/Dm-crypt/Encrypting_an_entire_system) - LUKS encryption setup
- [Laptop](https://wiki.archlinux.org/title/Laptop) - Laptop-specific optimizations
- [TLP](https://wiki.archlinux.org/title/TLP) - TLP installation and configuration on Arch
- [thermald](https://wiki.archlinux.org/title/Thermald) - thermald setup on Arch
- [Kernel parameters](https://wiki.archlinux.org/title/Kernel_parameters) - How to configure kernel boot parameters
- [sysctl](https://wiki.archlinux.org/title/Sysctl) - Runtime kernel parameter configuration

## Revision History

- **2026-03-10:** Initial draft - Comprehensive power and thermal management plan
- **2026-03-10:** Added Layer 5 (Memory Management) with swap and swappiness configuration

---

**Next Steps:**

1. Review and approve this ADR
2. Implement Step 1-8 (installation and configuration)
3. Reboot system
4. Monitor temperatures, memory usage, and system stability for 48 hours
5. Adjust thermal thresholds and swap settings if needed
6. Update this ADR with actual results and any modifications
