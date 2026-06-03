---
title: Guarded Sudo for OpenCode Agents
---

- **Date:** 2026-06-03
- **Context:** Manjaro Linux (KDE Plasma) running OpenCode with a custom plugin tool

> Edit this document [on Github](https://github.com/ftschindler/running-linux/edit/main/content/done/20260603-opencode-guarded-sudo.md)

## Problem Statement

OpenCode agents execute shell commands non-interactively — there is no TTY for a standard `sudo` password prompt. Agents that need elevated privileges must either run as root (dangerous) or have passwordless sudo (equally dangerous). A safe middle ground is required: the agent can _request_ privilege escalation, but the human operator must explicitly approve each request via a GUI prompt that displays **which session**, **which command** and **which working directory** is asking.

## Solution

Two components work together:

1. **`opencode-askpass`** — a thin shell wrapper that injects session context into a GUI password prompt
2. **A custom `sudo` tool** (`~/.config/opencode/tools/sudo.ts`) — sets `SUDO_ASKPASS` and passes contextual information so the operator sees exactly what is being requested

When an agent calls the `sudo` tool, the user sees a KDE dialog showing the session ID, session title, working directory and exact command before entering their password.

## Prerequisites

- A GUI askpass helper (`ksshaskpass` on KDE Plasma; substitute `ssh-askpass-gnome` or `x11-ssh-askpass` on other desktops)
- OpenCode with plugin SDK support
- Bun runtime (used by OpenCode's plugin system)

## Installation

### 1. Install a GUI askpass helper

```bash
sudo pacman -S ksshaskpass
```

On other desktops, install the appropriate package and adjust the path in step 2.

### 2. Create the askpass wrapper

Save to `~/.local/bin/opencode-askpass` and make it executable:

```bash
cat > ~/.local/bin/opencode-askpass << 'EOF'
#!/bin/bash
PROMPT="${1:-Password:}"

if [ -n "$OPENCODE_SUDO_DISPLAY" ]; then
    PROMPT="$OPENCODE_SUDO_DISPLAY
$PROMPT"
fi

exec /usr/bin/ksshaskpass "$PROMPT" 2>/dev/null
EOF
chmod +x ~/.local/bin/opencode-askpass
```

The wrapper prepends the `OPENCODE_SUDO_DISPLAY` environment variable (set by the custom tool) to the standard password prompt, giving the operator full context before they authenticate.

### 3. Install the plugin SDK

In `~/.config/opencode/`:

```bash
cd ~/.config/opencode
cat > package.json << 'EOF'
{
  "dependencies": {
    "@opencode-ai/plugin": "1.4.3"
  }
}
EOF
bun install
```

### 4. Create the `sudo` tool

Save to `~/.config/opencode/tools/sudo.ts`:

```typescript
import { tool } from "@opencode-ai/plugin"
import { Database } from "bun:sqlite"

function getSessionTitle(sessionID: string): string {
  try {
    const dataDir = process.env.XDG_DATA_HOME || `${process.env.HOME}/.local/share`
    const db = new Database(`${dataDir}/opencode/opencode.db`, { readonly: true })
    const row = db.query("SELECT title FROM session WHERE id = ?")
      .get(sessionID) as { title: string } | null
    db.close()
    return row?.title || sessionID
  } catch {
    return sessionID
  }
}

function buildSudoDisplay(
  sessionID: string, command: string, cwd: string
): string {
  const title = getSessionTitle(sessionID)
  return (
    `opencode -s ${sessionID} [${title}]`
    + ` in ${cwd} wants to execute \`${command}\``
  )
}

export default tool({
  description:
    "Execute commands with sudo -A"
    + " (uses GUI password prompt via askpass helper)",
  args: {
    command: tool.schema
      .string()
      .describe("The command to execute with sudo"),
    description: tool.schema
      .string()
      .optional()
      .describe("Description of what the command does"),
    timeout: tool.schema
      .number()
      .optional()
      .describe("Optional timeout in milliseconds"),
    workdir: tool.schema
      .string()
      .optional()
      .describe("The working directory to run the command in"),
  },
  async execute(args, context) {
    const workdir = args.workdir || context.directory
    const timeout = args.timeout || 120000

    const proc = Bun.spawn(
      ['bash', '-c', `sudo -A ${args.command}`],
      {
        cwd: workdir,
        env: {
          ...process.env,
          SUDO_ASKPASS:
            `${process.env.HOME}/.local/bin/opencode-askpass`,
          OPENCODE_SUDO_DISPLAY:
            buildSudoDisplay(
              context.sessionID, args.command, workdir
            ),
        },
        stdout: 'pipe',
        stderr: 'pipe',
      }
    )

    const timeoutId = setTimeout(() => proc.kill(), timeout)

    try {
      const exitCode = await proc.exited
      clearTimeout(timeoutId)

      const stdout =
        await Bun.readableStreamToText(proc.stdout)
      const stderr =
        await Bun.readableStreamToText(proc.stderr)

      let output = ''
      if (stdout) output += stdout
      if (stderr) output += stderr
      if (exitCode !== 0) {
        output += `\n[Exit code: ${exitCode}]`
      }

      return output || '[No output]'
    } catch (error) {
      clearTimeout(timeoutId)
      throw error
    }
  },
})
```

### 5. Restart OpenCode

Custom tools are loaded automatically on the next session start. No registration in `opencode.json` is needed — OpenCode discovers tools from `~/.config/opencode/tools/` by convention.

## How It Works

```text
Agent calls the sudo tool with command="pacman -S foo"
        ↓
sudo.ts runs: sudo -A pacman -S foo
        ↓
Sets SUDO_ASKPASS=~/.local/bin/opencode-askpass
Sets OPENCODE_SUDO_DISPLAY with session/command context
        ↓
sudo -A invokes opencode-askpass
        ↓
opencode-askpass calls ksshaskpass with full context string
        ↓
KDE dialog appears:
  "opencode -s ses_xxx [Fix build] in /project
   wants to execute `pacman -S foo`
   Password:"
        ↓
User approves (enters password) or cancels
```

## Adapting for Other Desktops

Replace `ksshaskpass` in the askpass wrapper with your desktop's equivalent:

| Desktop | Package | Binary |
| --- | --- | --- |
| KDE Plasma | `ksshaskpass` | `/usr/bin/ksshaskpass` |
| GNOME | `ssh-askpass-gnome` | `/usr/lib/ssh/gnome-ssh-askpass` |
| Generic X11 | `x11-ssh-askpass` | `/usr/lib/ssh/x11-ssh-askpass` |
| Headless/TTY | `systemd-ask-password` | Requires different integration |

## References

- [OpenCode plugin SDK](https://opencode.ai) — custom tool authoring documentation
- [`ksshaskpass` on KDE](https://invent.kde.org/plasma/ksshaskpass) — the underlying GUI password prompt
