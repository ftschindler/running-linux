---
title: Git AI Integration with OpenCode
---

**Context** – Manjaro Linux running OpenCode (with [OhMyOpenAgent](20260603-oh-my-openagent-installation.md)). This guide documents the installation, verification and behaviour of [Git AI](https://usegitai.com/) – a tool that tracks AI-generated code from prompt to commit.

## What is Git AI?

Git AI is a git extension that tracks AI-generated code in your repositories. It links every AI-written line to the **agent**, **model**, and **prompts** that generated it, providing:

- **AI Blame** – See which lines were written by AI vs humans, and query the original prompts
- **Commit Stats** – Aggregate AI vs human code percentages per commit
- **Prompt Storage** – All prompts and session data stored in git notes, travelling with the repository
- **No Workflow Changes** – Works transparently in the background
- **Fresh Checkout Ready** – After cloning, fetch notes to recover all AI attribution data

## How Git AI Works

Git AI uses a three-step process:

1. **Checkpoint Creation** – Coding agents call `git-ai checkpoint` whenever they write code or modify files
2. **Attribution on Commit** – Line-level attribution data is stored in Git Notes (`refs/notes/ai`), linking each line to the agent session
3. **Attribution Preservation** – Git AI moves and merges attributions during `rebase`, `squash`, `stash`, `cherry-pick`, etc.

Crucially, Git AI does **not** use AI or heuristics to "detect" AI code – agents explicitly report which lines they wrote via pre/post edit hooks.

## Installation

### 1. Install Git AI Globally

```bash
curl -sSL https://usegitai.com/install.sh | bash
```

This installs:

- `git-ai` binary to `~/.git-ai/bin/` (added to `$PATH` via `~/.local/bin/git-ai` symlink)
- VS Code extension (`git-ai.git-ai-vscode`)
- Agent hooks for Claude Code, GitHub Copilot, and OpenCode

### 2. Configure Prompt Storage

Set prompt storage to `notes` mode so all data travels with the repository:

```bash
git-ai config set prompt_storage notes
```

This stores all prompts and session transcripts in git notes (`refs/notes/ai`), ensuring they:

- Travel with the repository on clone/fetch
- Survive fresh checkouts
- Are versioned alongside your code

### 3. Disable Telemetry (Recommended for Local-Only Operation)

By default, git-ai sends anonymous usage metrics to `usegitai.com`. To ensure fully local operation:

```bash
# Disable OSS telemetry
git-ai config set telemetry_oss off

# Disable version checks (no outbound calls to check for updates)
git-ai config set disable_version_checks true

# Disable auto-updates
git-ai config set disable_auto_updates true
```

**What data is sent if telemetry is enabled:**

- Anonymous usage statistics (command counts, feature usage)
- Version information
- Session metadata (duration, operations performed)

**What NEVER leaves your machine:**

- Prompts and session transcripts
- Code changes or file contents
- File paths or repository structure
- API keys or credentials

With telemetry and auto-updates disabled, git-ai operates **100% locally** with zero external network calls.

### 4. Configure Git to Auto-Sync Notes (Per-Repository)

Configure git notes sync **per-repository** (not globally, as repos without git-ai will error on fetch):

```bash
# In each repository that uses git-ai:
git config --add remote.origin.fetch "+refs/notes/ai:refs/notes/ai"
git config push.defaultNotesRef refs/notes/ai
```

This ensures:

- Notes are pushed when you `git push`
- Notes are fetched when you `git fetch` or `git pull`
- Other repositories (without git-ai) are unaffected

### 5. Restart Agents

Any running agent sessions must be restarted for hooks to take effect.
Work done before installing git-ai (or before restarting agents) will be attributed as human.

## Verification

### Check Installation

```bash
git-ai --version
# Output: 1.5.13
```

### Check Configuration

Git AI stores global configuration at `~/.git-ai/config.json`:

```bash
cat ~/.git-ai/config.json
# Output:
# {
#   "telemetry_oss": "off",
#   "disable_version_checks": true,
#   "disable_auto_updates": true,
#   "api_base_url": "https://usegitai.com",
#   "prompt_storage": "notes"
# }
```

Key settings for local-only operation:

- `prompt_storage: "notes"` – All prompts stored in git notes (travels with repo)
- `telemetry_oss: "off"` – No usage metrics sent externally
- `disable_version_checks: true` – No outbound update checks
- `disable_auto_updates: true` – No automatic downloads

### Check Repository Attribution Data

After installation, git-ai creates repository-specific data:

```bash
# Check for .git/ai directory (checkpoint storage)
ls -la .git/ai/
# Output:
# drwxr-xr-x 4 felix felix 4096 Jun 24 14:03 .
# drwxr-xr-x 7 felix felix 4096 Jun 24 14:03 ..
# drwxr-xr-x 2 felix felix 4096 Jun 24 14:03 logs
# drwxr-xr-x 2 felix felix 4096 Jun 24 14:03 working_logs

# Check for AI notes on commits
git log --show-notes="ai" -1
# Output: warning: notes ref refs/notes/ai is invalid (no AI commits yet)

# Check AI stats for current repo
git ai stats
# Output: you ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ai
#          0%                                    0%
```

## Commands

### View AI Attribution

```bash
# Show AI notes on commits
git log --show-notes="ai"

# View AI blame for a file
git ai blame <file>

# View commit stats (AI vs human)
git ai stats
```

### Manage Configuration

```bash
# Show all config
git-ai config

# Set a config value
git-ai config set prompt_storage local

# Set per-repo override
git-ai config set include_prompts_in_repositories '[{"pattern":"github.com/org/repo","prompt_storage":"notes"}]'

# Reinstall hooks (e.g., after adding new agent)
git-ai install-hooks
```

### Uninstall

```bash
# Remove git-ai
rm -rf ~/.git-ai
rm ~/.local/bin/git-ai

# Remove from shell config (if added)
# Edit ~/.bashrc or ~/.zshrc to remove PATH entry

# Remove VS Code extension
code --uninstall-extension git-ai.git-ai-vscode
```
