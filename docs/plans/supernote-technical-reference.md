# Supernote Technical Reference

**Document Purpose**: Comprehensive technical specifications and capabilities of Supernote e-ink devices for Linux users seeking FOSS-compatible digital note-taking solutions.

**Last Updated**: June 2026
**Device Focus**: Supernote A5 X2 Manta, A6 X2 Nomad

## Table of Contents

- [Executive Summary](#executive-summary)
- [Hardware Specifications](#hardware-specifications)
- [File Formats](#file-formats)
- [Transfer Methods](#transfer-methods)
- [Self-Hosted Private Cloud](#self-hosted-private-cloud)
- [Community Tools](#community-tools)
- [Official Documentation](#official-documentation)
- [Comparison with Alternatives](#comparison-with-alternatives)
- [Linux Setup Guide](#linux-setup-guide)

## Executive Summary

**Supernote** (by Ratta) is an e-ink note-taking device manufacturer with unique FOSS-friendly features:

| Feature               | Status             | Notes                                    |
| --------------------- | ------------------ | ---------------------------------------- |
| **File Format**       | ✅ Open            | `.note` format fully reverse-engineered  |
| **Local Transfer**    | ✅ WiFi + USB      | No cloud required                        |
| **Self-Hosted Cloud** | ✅ Official Docker | Private Cloud protocol documented        |
| **Community Tools**   | ✅ 7+ Parsers      | Python, Rust, C#, Go                     |
| **Offline OCR**       | ✅ On-device       | Handwriting recognition without internet |
| **User Repairable**   | ✅ Modular         | Replaceable battery, expandable storage  |

**FOSS Rating**: ⭐⭐⭐⭐⭐ **HIGH** - Best in class for open ecosystem

## Hardware Specifications

### Supernote A5 X2 Manta

| Specification    | Value                                                 |
| ---------------- | ----------------------------------------------------- |
| **Screen**       | 10.7" E Ink Carta 1300                                |
| **Resolution**   | 1920 × 2560 (300 PPI)                                 |
| **Dimensions**   | 251.3 × 182.6 × 6.0 mm (thinnest edge: 3.6 mm)        |
| **Weight**       | 375g                                                  |
| **Storage**      | 32GB internal + microSD (up to 2TB, exFAT/NTFS/FAT32) |
| **RAM**          | 4GB                                                   |
| **Battery**      | 3600mAh (user-replaceable)                            |
| **Connectivity** | WiFi 2.4/5 GHz, Bluetooth 5.0, USB-C 2.0              |
| **Frontlight**   | ❌ None (true paper feel)                             |
| **Stylus**       | Wacom EMR (ceramic nibs, never wear)                  |
| **Price**        | ~$459 USD                                             |

### Supernote A6 X2 Nomad

| Specification  | Value                               |
| -------------- | ----------------------------------- |
| **Screen**     | 7.8" E Ink Carta 1300               |
| **Resolution** | 1872 × 1404 (300 PPI)               |
| **Dimensions** | 193 × 139 × 6.8 mm                  |
| **Weight**     | 266g                                |
| **Storage**    | 32GB internal + microSD (up to 2TB) |
| **RAM**        | 4GB                                 |
| **Battery**    | 2700mAh (user-replaceable)          |
| **Price**      | ~$329 USD                           |

### Key Hardware Features

1. **FeelWrite 2 Self-Recovery Film**: Textured screen surface for paper-like writing feel
2. **Ceramic Nibs**: Never wear out, no replacements needed
3. **Modular Design**: User-replaceable battery, microSD expansion
4. **No Frontlight**: Deliberate design choice for optimal pen-to-screen feel
5. **Wacom EMR**: Passive stylus, no charging required, 4096 pressure levels

**Sources**:

- [Supernote Manta Product Page](https://supernote.com/products/supernote-manta)
- [Supernote EU Specs](https://supernote.eu/product/supernote-set-a5x2-manta/)
- [Supernote X2 User Manual (PDF)](https://ib.supernote.com/x2/Manta&Nomad_V3.23.32_EN.pdf)

## File Formats

### Native Format: `.note`

The `.note` format is **well-documented and reverse-engineered** with full community parser support.

#### File Structure

```text
.note file layout:
┌─────────────────────────────────┐
│ Header (8 bytes)                │
│ - Magic number (4 bytes)        │
│ - Version number (4 bytes)      │
├─────────────────────────────────┤
│ File content (variable)         │
│ - Page data blocks              │
│ - Layer bitmaps (RLE compressed)│
│ - Stroke data (TOTALPATH)       │
├─────────────────────────────────┤
│ Footer (last 4 bytes = offset)  │
│ - Key-value pairs (TOC)         │
│   - FILE_FEATURE (config)       │
│   - PAGE_0, PAGE_1, ...         │
└─────────────────────────────────┘
```

#### Stroke Data Structure

Each stroke contains:

- **Pen type**: Ballpoint, fountain, marker, pencil, highlighter
- **Pen color**: Black, gray, white (grayscale palette)
- **Thickness**: Variable (pressure-sensitive)
- **Coordinates**: x, y (32-bit, little-endian)
- **Pressure**: 4096 levels
- **Tilt**: Direction vector (16-bit × 2)
- **Timestamp**: Per-stroke timing
- **Category**: "straightLine" or "others"

#### Page Data

Each page contains:

- **MAINLAYER**: Primary writing surface
  - `LAYERBITMAP`: Run-length encoded bitmap → PNG export
- **TOTALPATH**: All stroke data
  - Stroke headers (52-byte fixed buffers)
  - Point coordinates (32-bit)
  - Pressure/tilt modifiers (16-bit × 2)

**Technical Analysis**: [Investigating the SuperNote Notebook Format](https://walnut356.github.io/posts/inspecting-the-supernote-note-format/)

### Supported Import/Export Formats

| Format           | Import    | Export       | Notes             |
| ---------------- | --------- | ------------ | ----------------- |
| **.note**        | ✅ Native | ✅ Native    | Primary format    |
| **PDF**          | ✅ Yes    | ✅ Yes       | Vector or raster  |
| **EPUB**         | ✅ Yes    | ❌ No        | Reading only      |
| **Word (.docx)** | ✅ Yes    | ❌ No        | Reading only      |
| **PNG/JPG/WebP** | ✅ Yes    | ✅ Yes       | Image export      |
| **SVG**          | ❌ No     | ✅ Via tools | Community parsers |
| **Markdown**     | ❌ No     | ✅ Via tools | AI OCR conversion |
| **TXT**          | ✅ Yes    | ✅ Via tools | Text extraction   |

**Source**: [Supernote Support - File Formats](https://support.supernote.com/)

## Transfer Methods

### 1. Browse & Access (WiFi Local Transfer)

**Description**: Built-in web server for local file transfer over WiFi.

**How it Works**:

1. Swipe down from top menu → Enable "Browse & Access"
2. Device displays local IP (e.g. `http://192.168.1.50:8080`)
3. Open browser on any device on same LAN
4. Upload/download files via web interface

**Requirements**:

- Supernote and receiving device on same WiFi network
- No internet connection required (works on isolated LAN)

**Pros**:

- ✅ No cloud dependency
- ✅ Works offline
- ✅ Cross-platform (any device with browser)
- ✅ No software installation needed

**Cons**:

- ⚠️ Manual transfer (no auto-sync)
- ⚠️ Requires WiFi network

**Official Documentation**:

- [Transfer Files - Supernote Support](https://support.supernote.com/en_US/organizing/transfer-files)
- [X2 Manual Section 8.6](https://ib.supernote.com/x2/Manta&Nomad_V3.23.32_EN.pdf)

### 2. USB Cable (Mass Storage)

**Description**: Direct file access via USB-C cable.

**How it Works**:

1. Connect Supernote to computer via USB-C
2. Device appears as MTP storage
3. Access folders directly:
   - `/Note/` - Notebooks (.note files)
   - `/Document/` - PDFs, EPUBs
   - `/Inbox/` - Received files
   - `/EXPORT/` - Exported files

**Pros**:

- ✅ Fast transfer speeds
- ✅ No network required
- ✅ Direct filesystem access

**Cons**:

- ⚠️ MTP can be problematic on Linux (gvfs conflicts)
- ⚠️ Requires physical cable

**Linux Setup**:

```bash
# Install MTP tools
sudo pacman -S mtp-tools libmtp jmtpfs

# Disable automount (prevent gvfs conflicts)
# KDE: System Settings → Removable Storage
# GNOME: dconf write /org/gnome/desktop/media-handling/automount false

# Mount manually (if needed)
jmtpfs ~/mnt/supernote

# Access files
ls ~/mnt/supernote/Note/
```

**Official Documentation**:

- [Transfer Files - Supernote Support](https://support.supernote.com/en_US/organizing/transfer-files)

### 3. Supernote Cloud (Official)

**Description**: Official cloud sync service by Ratta.

**Features**:

- Automatic sync across devices
- Web interface for file management
- Mobile app integration (iOS/Android)

**Supported Services**:

- Supernote Cloud (official)
- Dropbox
- Google Drive
- OneDrive

**Pros**:

- ✅ Seamless automatic sync
- ✅ Official support
- ✅ Multi-device sync

**Cons**:

- ⚠️ Cloud dependency (requires internet)
- ⚠️ Data stored on third-party servers

**Official Documentation**:

- [Supernote Cloud Support](https://cloud.supernote.com)
- [X2 Manual Section 3.6](https://ib.supernote.com/x2/Manta&Nomad_V3.23.32_EN.pdf)

### 4. Private Cloud (Self-Hosted)

**Description**: Official Docker-based self-hosted cloud server.

**Features**:

- Full sync protocol compatibility
- Local data ownership
- Web management interface
- Automatic sync over WebSocket

**Deployment Options**:

- Docker / Docker Compose
- Linux script installation
- Synology NAS compatible

**Ports Required**:

| Port  | Purpose                     | Protocol  |
| ----- | --------------------------- | --------- |
| 19072 | Web interface + manual sync | HTTP      |
| 19443 | HTTPS (self-signed)         | HTTPS     |
| 18072 | Automatic sync (WebSocket)  | WebSocket |

**Docker Quick Start**:

```bash
docker run -d \
  --name supernote-private-cloud \
  -p 19072:8080 \
  -p 18072:18072 \
  -v /data/supernote:/data \
  -e MYSQL_ROOT_PASSWORD="your_password" \
  -e SUPERNOTE_CLOUD_ADMIN_EMAIL="admin@example.com" \
  -e SUPERNOTE_CLOUD_ADMIN_PASSWORD="your_password" \
  supernote/private-cloud
```

**Device Configuration**:

1. Settings → Sync → Private Cloud
2. Enter server URL (e.g. `http://192.168.1.5:19072`)
3. Log in with admin credentials
4. Select folders to sync
5. Enable auto-sync

**Pros**:

- ✅ Full data ownership
- ✅ No third-party cloud
- ✅ Official protocol support
- ✅ Automatic sync

**Cons**:

- ⚠️ Requires self-hosting setup
- ⚠️ HTTPS requires reverse proxy + custom domain

**Official Documentation**:

- [Setting Up Private Cloud](https://support.supernote.com/Whats-New/setting-up-your-own-supernote-private-cloud-beta)
- [Docker Deployment Manual (PDF)](https://ib.supernote.com/private-cloud/Supernote-Private-Cloud-Manual-Deployment-Method-Using-Docker-Containers.pdf)
- [Linux Deployment Manual (PDF)](https://ib.supernote.com/private-cloud/Supernote-Private-Cloud-Deployment-Manual.pdf)
- [Private Cloud Changelog](https://support.supernote.com/change-log/supernote-private-cloud-changelog)

### 5. Direct Transfer (Mobile App)

**Description**: WiFi transfer via Supernote Partner App.

**How it Works**:

1. Enable "Direct Transfer" on Supernote (Settings → My Device)
2. Open Supernote Partner App on phone (same WiFi)
3. Select file → Share → Supernote Partner
4. Pair devices (code verification)
5. Transfer completes to `/Inbox/`

**Pros**:

- ✅ No cloud required
- ✅ Mobile-friendly
- ✅ Quick sharing

**Cons**:

- ⚠️ Requires mobile app
- ⚠️ Manual transfer only

**Official Documentation**:

- [Transfer Files - Supernote Support](https://support.supernote.com/en_US/organizing/transfer-files)

## Self-Hosted Private Cloud

### Official Implementation

**Technology Stack**:

- Backend: Java / Spring Boot
- Database: MySQL
- Frontend: Node.js
- Web Server: Nginx (internal reverse proxy)

**Docker Architecture**:

```text
┌─────────────────────────────────────────┐
│ Docker Host                             │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ supernote-service container     │   │
│  │  - Port 8080: Nginx reverse proxy│   │
│  │  - Port 443: HTTPS service      │   │
│  │  - supernote-service: Sync API  │   │
│  └─────────────────────────────────┘   │
│           │                             │
│  Host Port Mapping:                     │
│  - 19072:8080 (HTTP access)            │
│  - 19443:443 (HTTPS access)            │
│  - 18072:18072 (Auto-sync WebSocket)   │
└─────────────────────────────────────────┘
```

**Nginx Reverse Proxy Configuration** (for HTTPS with trusted cert):

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 80;
    listen 443 ssl;
    server_name your_domain_name;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_session_timeout 60m;
    ssl_protocols TLSv1.2;
    ssl_prefer_server_ciphers on;

    client_max_body_size 20480m;

    access_log /var/log/nginx/supernote.access.log;
    error_log /var/log/nginx/supernote.error.log;

    location / {
        proxy_pass http://YOUR_PRIVATE_CLOUD_IP:19072;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_connect_timeout 6000;
        proxy_send_timeout 6000;
        proxy_read_timeout 6000;
    }

    location ~ ^/socket.io/(.*) {
        proxy_ignore_client_abort on;
        proxy_http_version 1.1;
        proxy_connect_timeout 60s;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;

        proxy_set_header X-NginX-Proxy true;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "$connection_upgrade";

        proxy_pass http://YOUR_PRIVATE_CLOUD_IP:18072;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Source**: [Private Cloud Deployment Manual](https://ib.supernote.com/private-cloud/Supernote-Private-Cloud-Deployment-Manual.pdf) - Section 5.5

### Community Implementations

#### 1. allenporter/supernote (Python)

**Features**:

- Private Cloud protocol implementation
- AI synthesis (Gemini Vision OCR)
- Semantic search (vectorised content)
- Modern web UI
- MCP (Model Context Protocol) support

**Installation**:

```bash
pip install supernote[server]
```

**Usage**:

```python
from supernote.notebook import parse_notebook

notebook = parse_notebook("mynote.note")
notebook.to_pdf("output.pdf")
```

**GitHub**: [allenporter/supernote](https://github.com/allenporter/supernote)

#### 2. nickian/Supernote-Private-Cloud

**Features**:

- Docker Compose deployment
- Simplified setup
- Nginx configuration for SSL

**GitHub**: [nickian/Supernote-Private-Cloud](https://github.com/nickian/Supernote-Private-Cloud)

#### 3. camerahacks/super-supernote

**Features**:

- Deployment guide with Nginx Proxy Manager
- Backup strategies (rsync)
- HTTPS/SSL configuration tips

**GitHub**: [camerahacks/super-supernote](https://github.com/camerahacks/super-supernote)

#### 4. nickian/Supernote-Private-Cloud-PHP-Client

**Features**:

- PHP API client
- File upload/download
- Directory listing
- Authentication

**API Endpoints**:

| Endpoint                               | Method | Purpose                  |
| -------------------------------------- | ------ | ------------------------ |
| `/api/official/user/query/random/code` | POST   | Get randomCode for login |
| `/api/official/user/account/login/new` | POST   | Authenticate + JWT       |
| `/api/file/list/query`                 | POST   | List directory           |
| `/api/file/upload/apply`               | POST   | Request upload           |
| `/api/oss/upload`                      | POST   | Upload file              |
| `/api/file/upload/finish`              | POST   | Confirm upload           |

**GitHub**: [nickian/Supernote-Private-Cloud-PHP-Client](https://github.com/nickian/Supernote-Private-Cloud-PHP-Client)

## Community Tools

### File Parsers & Converters

| Tool               | Language | Formats                        | GitHub                                                                |
| ------------------ | -------- | ------------------------------ | --------------------------------------------------------------------- |
| **supernote-tool** | Python   | PNG, SVG, PDF, vector PDF, TXT | [jya-dev/supernote-tool](https://github.com/jya-dev/supernote-tool)   |
| **supynote**       | Python   | PDF, Markdown (WiFi sync)      | [Thopiax/supynote](https://github.com/Thopiax/supynote)               |
| **sn2md**          | Python   | Markdown + AI OCR              | [dsummersl/sn2md](https://github.com/dsummersl/sn2md)                 |
| **supernote**      | Python   | PDF, PNG, SVG, text            | [allenporter/supernote](https://github.com/allenporter/supernote)     |
| **supernote-cli**  | Python   | Markdown, PNG, OCR             | [borismus/supernote-cli](https://github.com/borismus/supernote-cli)   |
| **snlib**          | Rust     | SVG, PNG, ImHex patterns       | [Walnut356/snlib](https://github.com/Walnut356/snlib)                 |
| **SupernoteSharp** | C#       | PNG, PDF, SVG, TXT             | [nelinory/SupernoteSharp](https://github.com/nelinory/SupernoteSharp) |

### Tool Usage Examples

#### supernote-tool (Python)

```bash
# Convert first page to PNG
supernote-tool convert your.note output.png

# Convert all pages to PNG
supernote-tool convert -a your.note output.png

# Convert to SVG
supernote-tool convert -t svg your.note output.svg

# Convert to PDF (all pages)
supernote-tool convert -t pdf -a your.note output.pdf

# Convert to vector PDF (handwriting as vectors)
supernote-tool convert -t pdf --pdf-type vector -a your.note output.pdf

# Extract text (real-time recognition)
supernote-tool extract-text your.note output.txt

# Dump metadata as JSON
supernote-tool analyze your.note
```

#### supynote (Python)

```bash
# Auto-discover device on WiFi
supynote auto-discover

# List files
supynote list

# Download all notes
supynote download Note/

# Convert to PDF (vector format)
supynote convert my-note.note

# Convert all notes in directory
supynote convert Note/ --output ~/Notes/
```

#### sn2md (Python)

```bash
# Convert single .note to Markdown
sn2md file my-note.note

# Convert directory of notes
sn2md directory ~/Notes/

# With custom config
sn2md --config ~/sn2md-config.toml file my-note.note
```

**Config Example** (`~/.config/sn2md.toml`):

```toml
template = "default"
model = "gpt-4o-mini"
openai_api_key = "your-key"

[prompt]
text = """
Convert the following image to markdown:
- If a diagram appears, create a mermaid codeblock
- Use $$, $ style math blocks for equations
- Don't wrap text in codeblocks
"""
```

#### supernote-cli (Python)

```bash
# List all notes
notebook ls

# Download and transcribe single note
notebook show 20260501_073927

# Download with PNG export
notebook show 20260501_073927 -o ~/notes/

# With Ollama OCR (local LLM)
notebook show 20260501_073927 --ocr ollama -o ~/notes/

# Convert to Markdown
notebook md 20260501_073927
```

#### snlib (Rust)

```rust
use snlib::{parse_notebook, export_png};

let notebook = parse_notebook("mynote.note")?;
let png_data = export_png(&notebook, 0)?; // Page 0
std::fs::write("output.png", png_data)?;
```

## Official Documentation

### Product Documentation

| Document               | URL                                                                                                        | Format |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- | ------ |
| **Manta Product Page** | [supernote.com/products/supernote-manta](https://supernote.com/products/supernote-manta)                   | Web    |
| **Nomad Product Page** | [supernote.com/pages/supernote-nomad](https://supernote.com/pages/supernote-nomad)                         | Web    |
| **X2 User Manual**     | [ib.supernote.com/x2/Manta&Nomad_V3.23.32_EN.pdf](https://ib.supernote.com/x2/Manta&Nomad_V3.23.32_EN.pdf) | PDF    |
| **Support Centre**     | [support.supernote.com](https://support.supernote.com)                                                     | Web    |

### Transfer & Sync

| Document                  | URL                                                                                                                                                                    | Format |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| **Transfer Files**        | [support.supernote.com/en_US/organizing/transfer-files](https://support.supernote.com/en_US/organizing/transfer-files)                                                 | Web    |
| **Partner App (Mobile)**  | [support.supernote.com/Tools-Features/1753209-supernote-partner-app-for-mobile](https://support.supernote.com/Tools-Features/1753209-supernote-partner-app-for-mobile) | Web    |
| **Partner App (Desktop)** | [support.supernote.com/Tools-Features/supernote-partner-app-for-desktop](https://support.supernote.com/Tools-Features/supernote-partner-app-for-desktop)               | Web    |
| **Supernote Cloud**       | [cloud.supernote.com](https://cloud.supernote.com)                                                                                                                     | Web    |

### Private Cloud

| Document                | URL                                                                                                                                                                                                                                | Format |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| **Private Cloud Setup** | [support.supernote.com/Whats-New/setting-up-your-own-supernote-private-cloud-beta](https://support.supernote.com/Whats-New/setting-up-your-own-supernote-private-cloud-beta)                                                       | Web    |
| **Docker Deployment**   | [ib.supernote.com/private-cloud/Supernote-Private-Cloud-Manual-Deployment-Method-Using-Docker-Containers.pdf](https://ib.supernote.com/private-cloud/Supernote-Private-Cloud-Manual-Deployment-Method-Using-Docker-Containers.pdf) | PDF    |
| **Linux Deployment**    | [ib.supernote.com/private-cloud/Supernote-Private-Cloud-Deployment-Manual.pdf](https://ib.supernote.com/private-cloud/Supernote-Private-Cloud-Deployment-Manual.pdf)                                                               | PDF    |
| **Changelog**           | [support.supernote.com/change-log/supernote-private-cloud-changelog](https://support.supernote.com/change-log/supernote-private-cloud-changelog)                                                                                   | Web    |

### Developer Documentation

| Document           | URL                                                                                                                                                  | Format        |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **Developer Docs** | [docs.supernote.com/en](https://docs.supernote.com/en)                                                                                               | Web           |
| **Plugin API**     | [docs.supernote.com/en/api-reference/supernote-plugin](https://docs.supernote.com/en/api-reference/supernote-plugin)                                 | Web           |
| **File API**       | [docs.supernote.com/en/api-reference/supernote-plugin/plugin-file-api](https://docs.supernote.com/en/api-reference/supernote-plugin/plugin-file-api) | Web           |
| **Element Types**  | [docs.supernote.com/zh/api-reference/supernote-plugin/types/trail](https://docs.supernote.com/zh/api-reference/supernote-plugin/types/trail)         | Web (Chinese) |
| **LLM Index**      | [docs.supernote.com/llms.txt](https://docs.supernote.com/llms.txt)                                                                                   | Text          |

### Software Updates

| Document             | URL                                                                                                                                                                | Format |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------ |
| **Change Log**       | [support.supernote.com/en_US/change-log](https://support.supernote.com/en_US/change-log)                                                                           | Web    |
| **Roadmap (Trello)** | [trello.com/b/l0COP24j/supernote-a5-x-a6-x-manta-nomad-software-roadmap-2025](https://trello.com/b/l0COP24j/supernote-a5-x-a6-x-manta-nomad-software-roadmap-2025) | Web    |

## Comparison with Alternatives

### Device Comparison

| Feature                | Supernote Manta    | reMarkable 2      | Boox Go 10.3       | Kindle Scribe    |
| ---------------------- | ------------------ | ----------------- | ------------------ | ---------------- |
| **Thickness**          | 6.0mm              | 4.7mm             | 4.6mm              | 5.8mm            |
| **Weight**             | 375g               | 403g              | 360g               | 433g             |
| **Screen**             | 10.7" Carta 1300   | 10.3" Carta 1200  | 10.3" Carta 1200   | 10.2" Carta 1200 |
| **Frontlight**         | ❌ No              | ❌ No             | ✅ Yes             | ✅ Yes           |
| **Native Format**      | .note (open)       | .rm (rev-eng)     | PDF/PNG            | .nbk (closed)    |
| **USB Access**         | ✅ MTP             | ✅ SSH            | ⚠️ MTP             | ❌ None          |
| **WiFi Transfer**      | ✅ Browse & Access | ❌ Cloud only     | ⚠️ Android sharing | ❌ Cloud only    |
| **Self-Hosted Cloud**  | ✅ Official Docker | ❌ Community only | ❌ None            | ❌ None          |
| **Community Tools**    | 7+ parsers         | 10+ tools         | ADB only           | None             |
| **Battery**            | Replaceable        | Sealed            | Sealed             | Sealed           |
| **Expandable Storage** | ✅ microSD 2TB     | ❌ No             | ❌ No              | ❌ No            |
| **Writing Feel**       | 9.5/10             | 9.0/10            | 7.0/10             | 6.0/10           |
| **FOSS Rating**        | ⭐⭐⭐⭐⭐ HIGH    | ⭐⭐⭐⭐ HIGH     | ⭐⭐⭐ MEDIUM      | ⭐ LOW           |

### FOSS Format Comparison

| Format      | Device     | Openness              | Tools      | Export Options         |
| ----------- | ---------- | --------------------- | ---------- | ---------------------- |
| **.note**   | Supernote  | ✅ Fully documented   | 7+ parsers | PDF, SVG, PNG, MD, TXT |
| **.rm**     | reMarkable | ✅ Reverse-engineered | 10+ tools  | PDF, SVG, PNG          |
| **PDF/PNG** | Boox       | ✅ Standard formats   | ADB/MTP    | Native export          |
| **.nbk**    | Kindle     | ❌ Encrypted          | None       | PDF (cloud only)       |

### Sync Method Comparison

| Method                | Supernote                  | reMarkable          | Boox               | Kindle            |
| --------------------- | -------------------------- | ------------------- | ------------------ | ----------------- |
| **Official Cloud**    | ✅ Supernote Cloud         | ✅ reMarkable Cloud | ❌ N/A             | ✅ Amazon         |
| **Third-Party Cloud** | ✅ Dropbox/GDrive/OneDrive | ❌ No               | ✅ Android apps    | ❌ Amazon only    |
| **Self-Hosted**       | ✅ Official Docker         | ❌ Community only   | ❌ None            | ❌ None           |
| **Local WiFi**        | ✅ Browse & Access         | ❌ No               | ⚠️ Android sharing | ❌ No             |
| **USB**               | ✅ MTP                     | ✅ SSH              | ⚠️ MTP             | ❌ No             |
| **Offline Sync**      | ✅ Private Cloud           | ❌ Cloud required   | ⚠️ Manual          | ❌ Cloud required |

## Linux Setup Guide

### Prerequisites

```bash
# Install MTP tools (for USB transfer)
sudo pacman -S mtp-tools libmtp jmtpfs

# Install Python tools (for .note conversion)
pip install supernote-tool supynote sn2md

# Install Rust tools (optional, for snlib)
cargo install snlib
```

### USB Transfer Setup

```bash
# 1. Disable automount (prevent gvfs conflicts)
# KDE: System Settings → Removable Storage → Uncheck "Automount"
# GNOME:
dconf write /org/gnome/desktop/media-handling/automount false

# 2. Connect Supernote via USB-C
# Device should appear in lsusb
lsusb | grep -i "supernote\|ratta"

# 3. Mount manually (if needed)
jmtpfs ~/mnt/supernote

# 4. Access files
ls ~/mnt/supernote/Note/

# 5. Unmount when done
fusermount -u ~/mnt/supernote
```

### WiFi Transfer Setup

```bash
# 1. On Supernote: Settings → Browse & Access → Enable
# Note the displayed IP address (e.g. 192.168.1.50:8080)

# 2. On Linux: Open browser
firefox http://192.168.1.50:8080

# 3. Upload/download files via web interface
```

### Private Cloud Setup (Docker)

```bash
# 1. Create Docker Compose file
cat > docker-compose.yml << EOF
version: '3.8'
services:
  supernote-private-cloud:
    image: supernote/private-cloud:latest
    ports:
      - "19072:8080"
      - "18072:18072"
    volumes:
      - /data/supernote:/data
    environment:
      - MYSQL_ROOT_PASSWORD=your_root_password
      - SUPERNOTE_CLOUD_ADMIN_EMAIL=admin@example.com
      - SUPERNOTE_CLOUD_ADMIN_PASSWORD=your_admin_password
    restart: unless-stopped
EOF

# 2. Start container
docker compose up -d

# 3. Access web interface
firefox http://localhost:19072

# 4. Configure Supernote device
# Settings → Sync → Private Cloud
# Server: http://YOUR_SERVER_IP:19072
# Login with admin credentials
```

### Convert .note to PDF

```bash
# Using supernote-tool
supernote-tool convert -t pdf -a ~/Notes/my-note.note ~/Exports/my-note.pdf

# Using supynote (from device)
supynote convert ~/Notes/my-note.note --output ~/Exports/

# Using Python API
python3 << EOF
from supernote.notebook import parse_notebook
notebook = parse_notebook("my-note.note")
notebook.to_pdf("output.pdf")
EOF
```

### Convert .note to Markdown (with OCR)

```bash
# Using sn2md (requires OpenAI API key)
export OPENAI_API_KEY="your-key"
sn2md file my-note.note --output ~/Notes/

# Using supernote-cli with Ollama (local LLM)
notebook show my-note --ocr ollama -o ~/Notes/

# Using supynote
supynote convert my-note.note --format markdown
```

### Backup Strategy

```bash
# 1. Manual USB backup
rsync -av ~/mnt/supernote/Note/ ~/Backup/Supernote/Note/

# 2. WiFi backup (Browse & Access)
wget -r http://192.168.1.50:8080/Note/ -P ~/Backup/Supernote/

# 3. Private Cloud backup (if self-hosted)
rsync -av /data/supernote/ ~/Backup/Supernote-Cloud/

# 4. Automated backup script
cat > ~/scripts/backup-supernote.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR=~/Backup/Supernote/$DATE

# Mount device
jmtpfs ~/mnt/supernote

# Backup notes
rsync -av ~/mnt/supernote/Note/ $BACKUP_DIR/Note/

# Unmount
fusermount -u ~/mnt/supernote

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
EOF

chmod +x ~/scripts/backup-supernote.sh
```

## Quick Reference

### Port Summary

| Port  | Service                 | Protocol  | Required For               |
| ----- | ----------------------- | --------- | -------------------------- |
| 8080  | Private Cloud internal  | HTTP      | Docker container           |
| 19072 | Private Cloud HTTP      | HTTP      | Web interface, manual sync |
| 19443 | Private Cloud HTTPS     | HTTPS     | Secure web access          |
| 18072 | Private Cloud auto-sync | WebSocket | Automatic background sync  |

### File Paths

| Location       | Purpose                          |
| -------------- | -------------------------------- |
| `/Note/`       | Notebooks (.note files)          |
| `/Document/`   | PDFs, EPUBs, documents           |
| `/Inbox/`      | Received files (Direct Transfer) |
| `/EXPORT/`     | Exported files from device       |
| `/SCREENSHOT/` | Screenshots                      |
| `/MyStyle/`    | Custom templates, themes         |

### Keyboard Shortcuts (Device)

| Gesture               | Action     |
| --------------------- | ---------- |
| Two-finger swipe up   | Undo       |
| Two-finger swipe down | Redo       |
| Two-finger tap        | Eraser     |
| Long press sidebar    | Quick menu |
| Swipe from edge       | Page turn  |

## Resources

### Official Resources

- **Website**: [supernote.com](https://supernote.com)
- **Support**: [support.supernote.com](https://support.supernote.com)
- **Cloud**: [cloud.supernote.com](https://cloud.supernote.com)
- **Developer Docs**: [docs.supernote.com](https://docs.supernote.com)
- **Roadmap**: [Trello Board](https://trello.com/b/l0COP24j/supernote-a5-x-a6-x-manta-nomad-software-roadmap-2025)

### Community Resources

- **Reddit**: [r/Supernote](https://reddit.com/r/Supernote)
- **GitHub Tools**: Search "supernote" or "supernote-tool"
- **Private Cloud Guide**: [camerahacks/super-supernote](https://github.com/camerahacks/super-supernote)
- **Format Analysis**: [walnut356.github.io/posts/inspecting-the-supernote-note-format](https://walnut356.github.io/posts/inspecting-the-supernote-note-format/)

## Conclusion

**Supernote** stands out as the most FOSS-friendly e-ink note-taking device available in 2026:

✅ **Open file format** (.note fully documented)
✅ **Official self-hosted cloud** (Docker deployment)
✅ **Local transfer options** (WiFi + USB, no cloud required)
✅ **Active community** (7+ parsers, multiple languages)
✅ **User-repairable** (replaceable battery, expandable storage)
✅ **Offline functionality** (handwriting recognition, local sync)

For Linux users prioritising data ownership, local control and open ecosystems, Supernote is the **recommended choice** over reMarkable, Boox or Kindle Scribe.

**Document Version**: 1.0
**Created**: June 2026
**Maintained By**: Community contributions welcome
