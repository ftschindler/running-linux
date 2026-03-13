# ADR: Private Mesh Network with Tailscale/Headscale

**Date:** 2026-03-13
**Status:** Proposed
**Context:** Self-hosted infrastructure with rootless Docker and Traefik reverse proxy

## Problem Statement

Multiple devices (laptops, servers, mobile devices) need secure connectivity across different networks without manual VPN configuration. Requirements:

1. Zero-trust mesh networking between all devices
2. NAT traversal without port forwarding
3. Fully open-source stack (no proprietary services)
4. Self-hosted control plane for complete data sovereignty
5. Integration with existing rootless Docker + Traefik infrastructure

## System Information

- **Server Infrastructure:** Debian-based Linux with rootless Docker
- **Reverse Proxy:** Traefik (handling TLS termination)
- **Network Requirements:** Public IPv4/IPv6 address, UDP port availability
- **Devices:** Mixed (Linux, macOS, Windows, iOS, Android)

## Decision

Deploy **Headscale** as a self-hosted coordination server with **Tailscale clients** on all devices.

### What is Headscale?

Headscale is an open-source, self-hostable implementation of the Tailscale control plane server. It provides:

- Full compatibility with official Tailscale clients
- Complete control over coordination server infrastructure
- No dependency on Tailscale's SaaS service
- Implementation of the Tailscale protocol (based on WireGuard)

### Technology Stack

**Control Plane (Self-Hosted):**

- **Headscale Server:** Coordination and control plane
- **Container:** Official `headscale/headscale` Docker image
- **Reverse Proxy:** Traefik (TLS termination, Let's Encrypt)
- **Database:** SQLite (embedded, file-based)

**Client Software (All Devices):**

- **Official Tailscale Clients:** Open-source BSD-3-Clause licensed
  - Linux: Available in most distribution repos
  - macOS/Windows: Official installers
  - iOS/Android: App stores
  - All configured to use custom Headscale server URL

### Architecture Overview

```text
┌──────────────────────────────────────────────────────────┐
│                   Internet                                │
└────────────┬──────────────────────────┬──────────────────┘
             │                          │
             │ HTTPS (443/tcp)          │ UDP (3478/udp)
             │ Control Plane            │ STUN (NAT traversal)
             │                          │
       ┌─────▼──────────────────────────▼─────┐
       │         Your Server                   │
       │  ┌─────────────┐    ┌──────────────┐ │
       │  │   Traefik   │───▶│  Headscale   │ │
       │  │  (TLS/443)  │    │   (8080)     │ │
       │  └─────────────┘    └──────────────┘ │
       │   Rootless Docker                     │
       └───────────────────────────────────────┘
                    │
                    │ WebSocket + Control Protocol
                    │
       ┌────────────┴──────────────┐
       │   Tailscale Clients       │
       │  ┌────┐ ┌────┐ ┌────┐    │
       │  │ PC │ │Srv │ │Mob │    │
       │  └────┘ └────┘ └────┘    │
       │                           │
       │  ┌─────────────────────┐  │
       │  │  Peer-to-Peer Mesh  │  │
       │  │  (WireGuard UDP)    │  │
       │  └─────────────────────┘  │
       └───────────────────────────┘
```

**Traffic Flow:**

1. **Control Traffic:** Clients ↔ Headscale (via HTTPS/WebSocket)
   - Device registration and authentication
   - Peer discovery and coordination
   - Policy enforcement

2. **Data Traffic:** Client ↔ Client (direct peer-to-peer)
   - WireGuard encrypted tunnels
   - Direct when possible (NAT traversal)
   - Via DERP relay when direct connection fails

## Implementation

### Prerequisites

**Server Requirements:**

- Public IPv4 address (IPv6 optional but recommended)
- Ports available:
  - 443/tcp: Already handled by Traefik
  - 3478/udp: STUN for NAT traversal (if enabling DERP)
- Traefik running in rootless Docker
- Valid domain name pointing to server

**DNS Configuration:**

```text
headscale.example.com    A       <your-ipv4>
headscale.example.com    AAAA    <your-ipv6>
```

**IMPORTANT:** If using Cloudflare DNS, orange cloud proxy MUST be disabled. Cloudflare's proxy does not support the WebSocket protocol requirements for Tailscale.

### Step 1: Directory Structure

```bash
mkdir -p ~/docker/headscale/{config,data}
cd ~/docker/headscale
```

### Step 2: Download Example Configuration

```bash
curl -o config/config.yaml \
  https://raw.githubusercontent.com/juanfont/headscale/main/config-example.yaml
```

### Step 3: Headscale Configuration

Edit `config/config.yaml` with these key settings:

```yaml
# Public URL (HTTPS, behind Traefik)
server_url: https://headscale.example.com

# Internal listen address (non-privileged port for rootless Docker)
listen_addr: 0.0.0.0:8080

# Metrics endpoint (internal only)
metrics_listen_addr: 0.0.0.0:9090

# TLS: Disabled (Traefik handles termination)
tls_cert_path: ""
tls_key_path: ""

# gRPC for CLI commands
grpc_listen_addr: 0.0.0.0:50443
grpc_allow_insecure: false  # Use TLS in production

# IP address ranges for mesh network
prefixes:
  v4: 100.64.0.0/10        # Default Tailscale range
  v6: fd7a:115c:a1e0::/48  # Default Tailscale range

# DERP relay server (optional but recommended)
derp:
  server:
    enabled: true
    region_id: 999
    region_code: "selfhosted"
    region_name: "Self-hosted DERP"
    verify_clients: true
    stun_listen_addr: "0.0.0.0:3478"
    ipv4: <your-public-ipv4>
    ipv6: <your-public-ipv6>  # Optional

  # Optionally use Tailscale's public DERP servers as fallback
  urls:
    - https://controlplane.tailscale.com/derpmap/default
  paths: []

# Database configuration
database:
  type: sqlite
  sqlite:
    path: /var/lib/headscale/db.sqlite

# DNS configuration for mesh
dns:
  magic_dns: true
  base_domain: mesh.example.com
  nameservers:
    - 1.1.1.1
    - 8.8.8.8
```

**Configuration Rationale:**

- **Port 8080:** Non-privileged, compatible with rootless Docker
- **No TLS in Headscale:** Traefik terminates TLS at edge
- **DERP enabled:** Provides relay fallback when direct connection fails
- **SQLite database:** Simple, file-based, sufficient for most deployments
- **MagicDNS:** Allows using device names instead of IPs

### Step 4: Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  headscale:
    image: headscale/headscale:0.28.0
    container_name: headscale
    restart: unless-stopped

    # Security: Read-only container with tmpfs for runtime
    read_only: true
    tmpfs:
      - /var/run/headscale

    # Volume mounts
    volumes:
      - ./config:/etc/headscale:ro
      - ./data:/var/lib/headscale

    # Direct port exposure for STUN (UDP)
    # Cannot be proxied through Traefik
    ports:
      - "3478:3478/udp"

    # Traefik integration
    labels:
      - "traefik.enable=true"

      # HTTP router
      - "traefik.http.routers.headscale.rule=Host(`headscale.example.com`)"
      - "traefik.http.routers.headscale.entrypoints=websecure"
      - "traefik.http.routers.headscale.tls=true"
      - "traefik.http.routers.headscale.tls.certresolver=letsencrypt"

      # Service definition
      - "traefik.http.services.headscale.loadbalancer.server.port=8080"

    # Command
    command: serve

    # Health check
    healthcheck:
      test: ["CMD", "headscale", "health"]
      interval: 30s
      timeout: 5s
      retries: 3

    # Network
    networks:
      - traefik

networks:
  traefik:
    external: true
```

**Important Notes:**

- **UDP Port 3478:** Must be directly published, not proxied through Traefik
- **Traefik Network:** Assumes existing Traefik deployment with network named `traefik`
- **Read-only Filesystem:** Security hardening, tmpfs for runtime state
- **Health Check:** Uses built-in `headscale health` command

### Step 5: Set Permissions (Rootless Docker)

```bash
# Ensure data directory is writable
chmod 755 data

# If running as specific UID (e.g., 1000), set ownership
# chown -R 1000:1000 data
```

### Step 6: Deploy Headscale

```bash
docker compose up -d
```

**Verify deployment:**

```bash
# Check container logs
docker logs headscale

# Test health endpoint
curl https://headscale.example.com/health

# Expected response: {"status": "ok"}
```

### Step 7: Create First User/Namespace

Headscale organizes devices into "users" (also called namespaces):

```bash
# Create a user
docker exec headscale headscale users create personal

# List users
docker exec headscale headscale users list
```

### Step 8: Connect First Device

**Linux Example:**

```bash
# Install Tailscale client
sudo apt install tailscale  # Debian/Ubuntu
# or
sudo pacman -S tailscale    # Arch

# Connect to Headscale server
sudo tailscale up --login-server=https://headscale.example.com
```

**The client will output a registration URL. Copy it.**

**Register device on server:**

```bash
# On server, register the device
docker exec headscale headscale nodes register --user personal --key <KEY_FROM_URL>

# Alternative: Use pre-authentication keys
docker exec headscale headscale preauthkeys create --user personal --expiration 24h
# Use the generated key during `tailscale up --authkey=<KEY>`
```

**Verify device registration:**

```bash
docker exec headscale headscale nodes list
```

**macOS/Windows:**

1. Install official Tailscale application
2. Open preferences/settings
3. Set custom control server URL: `https://headscale.example.com`
4. Log in and complete registration (same process as Linux)

**Mobile (iOS/Android):**

1. Install Tailscale app
2. Settings → Use Custom Coordination Server
3. Enter: `https://headscale.example.com`
4. Complete registration flow

### Step 9: Configure Device Routes (Optional)

**Share subnet access:**

```bash
# On a Linux device, advertise local subnet
sudo tailscale up --advertise-routes=192.168.1.0/24

# On server, approve the route
docker exec headscale headscale routes list
docker exec headscale headscale routes enable --route=<ROUTE_ID>
```

**Exit node (route all traffic through device):**

```bash
# Advertise as exit node
sudo tailscale up --advertise-exit-node

# On server, approve
docker exec headscale headscale routes list
docker exec headscale headscale routes enable --route=<ROUTE_ID>

# On another device, use exit node
tailscale up --exit-node=<EXIT_NODE_NAME>
```

## Verification and Monitoring

### Health Checks

```bash
# Headscale health
curl https://headscale.example.com/health

# Container status
docker ps | grep headscale

# Container logs
docker logs -f headscale

# View connected nodes
docker exec headscale headscale nodes list
```

### Client Connectivity

```bash
# Check Tailscale status
tailscale status

# Ping another device on mesh
ping 100.64.0.2

# Test with device name (MagicDNS)
ping laptop.mesh.example.com

# Check active connections
tailscale netcheck
```

### Metrics (Prometheus)

Headscale exposes Prometheus metrics on port 9090:

```bash
# If exposing metrics externally (NOT recommended in docker-compose above)
curl http://localhost:9090/metrics
```

**Recommended:** Keep metrics internal, scrape from within Docker network.

## Networking Details

### Ports Summary

| Port | Protocol | Purpose | Exposure | Proxied |
|------|----------|---------|----------|---------|
| 443  | TCP      | Control plane (HTTPS + WebSocket) | External | Yes (Traefik) |
| 8080 | TCP      | Headscale internal HTTP | Internal | N/A |
| 50443| TCP      | gRPC (CLI commands) | Internal | N/A |
| 9090 | TCP      | Metrics | Internal | N/A |
| 3478 | UDP      | STUN (NAT traversal) | External | No (direct) |

### WebSocket Requirements

**Critical:** Headscale requires WebSocket support with custom upgrade protocol:

- Standard: `Upgrade: websocket`
- Tailscale-specific: `Upgrade: tailscale-control-protocol`

**Traefik handles this natively** with no special configuration.

**Alternative reverse proxies** (for reference):

**nginx configuration:**

```nginx
location / {
    proxy_pass http://localhost:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### DERP Relay System

**What is DERP?**

DERP (Designated Encrypted Relay for Packets) provides fallback relay when direct peer-to-peer connection fails (e.g., behind symmetric NAT).

**Deployment Modes:**

1. **Self-hosted DERP only** (as configured above):
   - Maximum privacy
   - Your server relays all non-direct traffic
   - Requires adequate bandwidth

2. **Hybrid** (self-hosted + Tailscale public):
   - Fallback to Tailscale's public DERP servers
   - Better global coverage
   - Some traffic may relay through Tailscale infrastructure
   - Configuration: Keep `urls` in DERP config

3. **Tailscale public DERP only**:
   - Disable `derp.server.enabled`
   - Use only `derp.urls`
   - Least infrastructure burden
   - Less privacy (metadata visible to Tailscale)

**Trade-offs:**

- **Self-hosted:** Full privacy, more bandwidth, potential latency
- **Public DERP:** Better performance, metadata exposure, less control

## Management Tasks

### Common Administrative Commands

```bash
# Alias for convenience
alias headscale='docker exec headscale headscale'

# User management
headscale users create <name>
headscale users list
headscale users rename --old-name <old> --new-name <new>
headscale users destroy <name>

# Node management
headscale nodes list
headscale nodes register --user <user> --key <key>
headscale nodes delete --identifier <node-id>
headscale nodes expire --identifier <node-id>

# Pre-authentication keys
headscale preauthkeys create --user <user> --expiration 24h
headscale preauthkeys list --user <user>

# Route management
headscale routes list
headscale routes enable --route <route-id>
headscale routes disable --route <route-id>

# ACL (Access Control Lists)
# Edit config/acl.yaml, then:
docker restart headscale
```

### Backup Strategy

**Critical data to backup:**

```bash
# Database (contains all node registrations, users, keys)
data/db.sqlite

# Configuration
config/config.yaml
config/acl.yaml  # If using ACLs
```

**Backup script:**

```bash
#!/bin/bash
BACKUP_DIR="/backup/headscale/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Stop Headscale (optional, but ensures consistency)
docker stop headscale

# Backup database and config
cp data/db.sqlite "$BACKUP_DIR/"
cp config/config.yaml "$BACKUP_DIR/"
cp config/acl.yaml "$BACKUP_DIR/" 2>/dev/null || true

# Restart
docker start headscale

echo "Backup saved to $BACKUP_DIR"
```

### Updates

```bash
# Pull new image
docker compose pull

# Backup database first
./backup.sh

# Restart with new image
docker compose up -d

# Verify
docker logs headscale
headscale nodes list
```

## Security Considerations

### Access Control

**ACL Configuration:**

Create `config/acl.yaml`:

```yaml
acls:
  - action: accept
    src: ["personal:*"]
    dst: ["personal:*:*"]

  - action: accept
    src: ["admin:*"]
    dst: ["*:*"]
```

**ACL Features:**

- Group-based access control
- Service-based rules (SSH, HTTP, etc.)
- Tag-based policies
- User isolation

### Authentication

**Node Authentication Options:**

1. **Interactive Registration** (default):
   - Manual approval via CLI
   - Best for personal use
   - High security

2. **Pre-authentication Keys**:
   - Time-limited registration tokens
   - Good for automated deployments
   - Set short expiration (24h recommended)

3. **OIDC Integration** (optional):
   - External identity provider (Keycloak, Authentik, etc.)
   - Centralized authentication
   - Better for teams

### Network Isolation

**Firewall Rules (Server):**

```bash
# Allow HTTPS (if not already)
sudo ufw allow 443/tcp

# Allow STUN for DERP
sudo ufw allow 3478/udp
```

**Traefik Security:**

- Ensure rate limiting is configured
- Consider IP allowlisting for administrative endpoints
- Use strong TLS configuration (TLS 1.3 preferred)

### Container Security

**Current hardening:**

- Read-only filesystem (`read_only: true`)
- tmpfs for runtime state
- Non-root user (default in official image)
- Minimal base image (distroless)

**Additional considerations:**

- Regular image updates
- Vulnerability scanning (Trivy, Clair)
- Resource limits (CPU/memory)

## Troubleshooting

### Headscale Not Starting

**Check logs:**

```bash
docker logs headscale
```

**Common issues:**

1. **Port already in use:**

   ```bash
   # Check what's using port 3478
   sudo ss -ulnp | grep 3478
   ```

2. **Database permission error:**

   ```bash
   # Fix permissions
   chmod 755 data
   ls -la data/db.sqlite
   ```

3. **Invalid configuration:**

   ```bash
   # Validate config
   docker run --rm -v ./config:/etc/headscale:ro \
     headscale/headscale:latest headscale validate
   ```

### Client Cannot Connect

**Symptoms:** `tailscale up` hangs or fails

**Diagnostics:**

```bash
# Test Headscale is reachable
curl -v https://headscale.example.com/health

# Check DNS resolution
nslookup headscale.example.com

# Verify TLS certificate
curl -vI https://headscale.example.com

# Check client logs
journalctl -u tailscaled -f  # Linux systemd
```

**Common issues:**

1. **Cloudflare proxy enabled:**
   - Disable orange cloud in Cloudflare DNS
   - Wait for DNS propagation

2. **Firewall blocking:**
   - Verify port 443/tcp is open
   - Check client-side firewall

3. **Wrong server URL:**
   - Verify client configuration: `tailscale status`
   - Reset if needed: `tailscale logout`, then `tailscale up --login-server=...`

### WebSocket Connection Failures

**Symptoms:** Device registers but shows offline, control plane disconnects

**Check WebSocket support:**

```bash
# Test WebSocket connection (requires websocat or similar)
websocat wss://headscale.example.com/ts2021

# Check Traefik logs
docker logs traefik | grep headscale
```

**Solution:** Verify Traefik labels are correct, especially `loadbalancer.server.port=8080`

### Peers Cannot Connect (NAT Traversal Issues)

**Symptoms:** Devices registered but cannot ping each other

**Diagnostics:**

```bash
# Check connectivity
tailscale netcheck

# View peer status
tailscale status

# Check if DERP is working
tailscale netcheck | grep DERP
```

**Common issues:**

1. **STUN port blocked:**
   - Verify UDP 3478 is open on server
   - Check: `nc -vu <server-ip> 3478`

2. **DERP server unreachable:**
   - Verify DERP config in `config.yaml`
   - Check public IP is correct
   - Ensure DERP is enabled: `derp.server.enabled: true`

3. **Symmetric NAT:**
   - Some NAT types prevent direct connections
   - DERP relay should handle this automatically
   - Verify DERP is functioning

### Database Corruption

**Symptoms:** Headscale crashes, SQLite errors in logs

**Recovery:**

```bash
# Stop container
docker stop headscale

# Restore from backup
cp /backup/headscale/<date>/db.sqlite data/

# Or attempt repair
sqlite3 data/db.sqlite "PRAGMA integrity_check;"

# Restart
docker start headscale
```

## Performance Considerations

### Resource Usage

**Typical resource consumption:**

- **CPU:** Very low (<1% idle, <5% active)
- **RAM:** ~50-100 MB
- **Disk I/O:** Minimal (SQLite writes)
- **Network:** Depends on DERP relay usage

**Scaling:**

- SQLite suitable for <1000 nodes
- For larger deployments, consider PostgreSQL:

  ```yaml
  database:
    type: postgres
    postgres:
      host: postgres
      port: 5432
      name: headscale
      user: headscale
      pass: <password>
  ```

### DERP Relay Bandwidth

**Estimation:**

- **Direct connections:** No relay bandwidth used
- **Relayed traffic:** All data flows through server
- **Typical ratio:** 10-30% of connections require relay

**Bandwidth calculation:**

- 10 devices × 30% relay rate = 3 active relays
- 1 Mbps average per relay = 3 Mbps
- Add headroom: ~10 Mbps total

**Optimization:**

- Use public DERP servers as fallback
- Deploy regional DERP servers if needed
- Monitor bandwidth usage: `iftop`, `vnstat`

## Expected Outcomes

After successful deployment:

✓ **Zero-configuration connectivity:** Devices connect automatically across networks
✓ **NAT traversal:** Works behind routers without port forwarding
✓ **Encrypted mesh:** All traffic encrypted with WireGuard
✓ **Low latency:** Direct peer-to-peer when possible
✓ **DNS resolution:** Devices accessible by name (MagicDNS)
✓ **Subnet routing:** Access home/office networks remotely
✓ **Exit node capability:** Route internet traffic through trusted device
✓ **Full FOSS stack:** Complete control and transparency
✓ **Self-hosted:** No dependency on external services

## Trade-offs

**Advantages:**

- Complete data sovereignty (self-hosted control plane)
- Full open-source stack (no proprietary components)
- Works with existing rootless Docker infrastructure
- Compatible with official Tailscale clients (excellent UX)
- No subscription fees
- Fine-grained access control (ACLs)
- MagicDNS and subnet routing capabilities

**Disadvantages:**

- Requires server with public IP
- Manual server maintenance and updates
- DERP relay bandwidth from your server
- More complex initial setup than SaaS Tailscale
- No official Tailscale features: Funnel, Taildrop (some alternatives exist)
- Responsibility for backups and disaster recovery

## Alternatives Considered

### Alternative 1: Tailscale SaaS

**Description:** Use Tailscale's hosted coordination server

**Rejected Because:**

- Proprietary coordination server
- Control plane metadata visible to Tailscale
- Not fully FOSS stack
- Subscription costs for teams

**When to Consider:**

- Don't want to manage infrastructure
- Need Tailscale-specific features (Funnel, SSH, etc.)
- Require enterprise support

### Alternative 2: Netmaker

**Description:** Self-hosted mesh VPN with web UI

**Not Selected Because:**

- More complex architecture (requires multiple components)
- Less mature than Headscale
- WireGuard configuration instead of Tailscale protocol

**When to Consider:**

- Need web-based management UI
- Want more control over WireGuard configs
- Traditional VPN model preferred

### Alternative 3: Netbird

**Description:** Another Tailscale-compatible self-hosted solution

**Not Selected Because:**

- Newer project (less battle-tested)
- Similar to Headscale but less community adoption

**When to Consider:**

- Want additional features (SSO, activity logs UI)
- Prefer Go-based projects

## References

- [Headscale Official Documentation](https://headscale.net/)
- [Headscale GitHub Repository](https://github.com/juanfont/headscale)
- [Tailscale Open Source Clients](https://github.com/tailscale/tailscale)
- [WireGuard Protocol](https://www.wireguard.com/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Tailscale How It Works](https://tailscale.com/blog/how-tailscale-works/)

## Revision History

- **2026-03-13:** Initial draft - Headscale deployment with rootless Docker and Traefik

---

**Next Steps:**

1. Review and approve this ADR
2. Prepare server infrastructure (DNS, firewall rules)
3. Deploy Headscale with Docker Compose
4. Create initial user/namespace
5. Connect first test device
6. Verify connectivity and DERP functionality
7. Connect remaining devices
8. Configure ACLs if needed
9. Set up backup automation
10. Document device-specific connection instructions
