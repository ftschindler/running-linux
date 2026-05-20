---
title: Unified Media Structure for Jellyfin with Bind Mounts
---

- **Date:** 2026-05-20
- **Context:** Manjaro Linux, Jellyfin media server with content across multiple drives

## Problem Statement

Media files are scattered across multiple mounted drives with varying permissions. Jellyfin requires a consistent directory structure to organize libraries by media type (Movies, TV Shows, Music).

## Solution: Hierarchical Bind Mount Structure

**Core Concept:** Create a single directory per Jellyfin media type (e.g., `/media/movies`) and bind-mount source directories from multiple drives as subdirectories. This allows Jellyfin to scan one top-level folder per library while pulling content from various sources.

### Directory Structure

```text
/media/
├── movies/
│   ├── drive1/          # bind mount from /mnt/drive1/Movies
│   ├── drive2/          # bind mount from /mnt/drive2/Films
│   └── nas/             # bind mount from /mnt/nas/share/movies
├── shows/
│   ├── drive1/          # bind mount from /mnt/drive1/TV_Shows
│   └── nas/             # bind mount from /mnt/nas/share/tv
└── music/
    ├── drive1/          # bind mount from /mnt/drive1/Music
    └── drive2/          # bind mount from /mnt/drive2/Audio
```

### Implementation

```bash
# 1. Create media type directories
sudo mkdir -p /media/{movies,shows,music}/{drive1,drive2,nas}

# 2. Set up bind mounts (temporary test)
sudo mount --bind /mnt/drive1/Movies /media/movies/drive1
sudo mount --bind /mnt/drive1/TV_Shows /media/shows/drive1

# 3. Make persistent in /etc/fstab
# Use x-systemd.requires to ensure source is mounted first
/mnt/drive1/Movies    /media/movies/drive1    none  bind,nofail,x-systemd.requires=/mnt/drive1  0  0
/mnt/drive1/TV_Shows  /media/shows/drive1     none  bind,nofail,x-systemd.requires=/mnt/drive1  0  0
```

**Key Options:**

- `bind` - Create bind mount
- `nofail` - Continue boot if mount fails (prevents failures when drives are disconnected)
- `x-systemd.requires=` - Systemd dependency to mount source first

### Jellyfin Permissions

Grant read access using ACLs on source directories:

```bash
# Grant jellyfin user read/execute permissions
sudo setfacl -R -m u:jellyfin:rX /mnt/drive1/{Movies,TV_Shows}
sudo setfacl -R -d -m u:jellyfin:rX /mnt/drive1/{Movies,TV_Shows}

sudo systemctl restart jellyfin
```

The `-d` flag sets default ACLs for new files.

### Jellyfin Configuration

In Jellyfin, add libraries pointing to:

- **Movies Library:** `/media/movies`
- **TV Shows Library:** `/media/shows`
- **Music Library:** `/media/music`

Jellyfin will automatically scan all subdirectories (drive1/, drive2/, nas/) within each library.

## References

- [Arch Wiki: fstab](https://wiki.archlinux.org/title/Fstab)
- [Arch Wiki: File permissions and attributes (ACL)](https://wiki.archlinux.org/title/File_permissions_and_attributes#Access_Control_Lists)
- [systemd.mount - systemd mount options](https://www.freedesktop.org/software/systemd/man/latest/systemd.mount.html)
- [mount(8) - bind mounts](https://man.archlinux.org/man/mount.8#FILESYSTEM-INDEPENDENT_MOUNT_OPTIONS)

## Benefits

- **Single library path per media type** - Jellyfin scans one directory per library
- **Flexible source management** - Add/remove drives without reconfiguring Jellyfin
- **Unified permissions** - Apply ACLs once at source level
- **Boot resilience** - System boots successfully even if drives are missing (`nofail`)
