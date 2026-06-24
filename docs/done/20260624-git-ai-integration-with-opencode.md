---
title: Git AI Integration with OpenCode
---

**Context** – Manjaro Linux running OpenCode (via OhMyOpenAgent) with OVHcloud AI Endpoints. This guide documents the installation, verification and behaviour of [Git AI](https://usegitai.com/) – a tool that tracks AI-generated code from prompt to commit.

## What is Git AI?

Git AI is a git extension that tracks AI-generated code in your repositories. It links every AI-written line to the **agent**, **model**, and **prompts** that generated it, providing:

- **AI Blame** – See which lines were written by AI vs humans, and query the original prompts
- **Commit Stats** – Aggregate AI vs human code percentages per commit
- **Prompt Storage** – Sessions are stored locally (SQLite) or in git notes
- **No Workflow Changes** – Works transparently in the background

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

**Output from installation:**

```text
Installed git-ai 1.5.13
Setting up IDE/agent hooks...
✓ Claude Code: Hooks updated
✓ VS Code: Hooks already up to date
✓ GitHub Copilot: Hooks updated
✓ OpenCode: Hooks updated
```

### 2. Restart Agents

Any running agent sessions must be restarted for hooks to take effect:

```bash
# Kill existing opencode sessions
# Then restart opencode fresh
```

Work done before installing git-ai (or before restarting agents) will be attributed as human.

## Verification

### Check Installation

```bash
git-ai --version
# Output: 1.5.13
```

### Check Configuration

Git AI stores global configuration at `~/.git-ai/config.json`:

```json
{
  "api_base_url": "https://usegitai.com",
  "prompt_storage": "default",
  "git_path": "/usr/bin/git",
  "telemetry_oss_disabled": false,
  "disable_auto_updates": false,
  "update_channel": "latest"
}
```

Key configuration options:

- `prompt_storage` – Controls where prompts are stored:
  - `"default"` – Local SQLite database (outside git)
  - `"notes"` – Include in git notes (travels with repo)
  - `"local"` – Local SQLite only
- `include_prompts_in_repositories` – Per-repo overrides for prompt storage
- `exclude_repositories` – Repositories where git-ai should be disabled

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

## OpenCode Integration

### How the Plugin Works

Git AI installs a plugin at `~/.config/opencode/plugins/git-ai.ts` that hooks into OpenCode's plugin system. The plugin:

1. Listens for `tool.execute.before` and `tool.execute.after` events
2. Tracks file-modifying tools: `edit`, `write`, `patch`, `multiedit`, `apply_patch`, `bash`
3. Calls `git-ai checkpoint opencode --hook-input stdin` with JSON metadata:

   ```json
   {
     "hook_event_name": "PreToolUse",
     "session_id": "<session-id>",
     "tool_use_id": "<call-id>",
     "cwd": "<repo-dir>",
     "tool_name": "edit",
     "tool_input": { ... }
   }
   ```

### Plugin Location

- **Global**: `~/.config/opencode/plugins/git-ai.ts`
- **Project-local**: `.opencode/plugins/git-ai.ts`

The plugin is automatically installed by `git-ai install-hooks` and references the git-ai binary path at install time:

```typescript
const GIT_AI_BIN = "/home/felix/.git-ai/bin/git-ai"
```

### Debugging

Enable debug logging for the plugin:

```bash
export GIT_AI_OPENCODE_DEBUG=1
# or
export GIT_AI_DEBUG=true
```

This will output checkpoint errors to `console.error`.

## Storage Locations

### Global Configuration (Per-User)

```text
~/.git-ai/config.json          # Main configuration
~/.git-ai/bin/git-ai           # Binary
~/.git-ai/internal/            # Internal data (metrics, transcripts)
```

### Repository-Specific Data (Per-Repo)

```text
.git/ai/                       # Checkpoint storage
.git/ai/logs/                  # Session logs
.git/ai/working_logs/          # Working tree checkpoints
refs/notes/ai                  # Git notes with attribution
```

### Prompt/Session Transcripts

Controlled by `prompt_storage` config:

| Mode        | Storage Location                               | Travels with Repo? |
|-------------|------------------------------------------------|--------------------|
| `"default"` | `~/.git-ai/internal/transcripts-db` (SQLite)   | No                 |
| `"notes"`   | Git notes (`refs/notes/ai`)                    | Yes                |
| `"local"`   | Local SQLite only                              | No                 |

## Per-Repository Configuration

While the main `config.json` is global, you can configure per-repository behaviour:

```json
{
  "prompt_storage": "default",
  "include_prompts_in_repositories": [
    {
      "pattern": "github.com/myorg/sensitive-repo",
      "prompt_storage": "local"
    }
  ],
  "default_prompt_storage": "notes"
}
```

This configuration:

- Stores prompts locally (SQLite) for `sensitive-repo`
- Stores prompts in git notes for all other repos

## Capabilities and Limitations

### Supported Features

- **Edit/Write/Patch tools** – ✅ Line-level attribution
- **Files created via Bash** – ✅ (if cwd is in repo)
- **git worktrees** – ✅ Attribution maintained
- **Background Agents** – ✅ See docs
- **Multiple sessions per commit** – ✅
- **Human override detection** – ✅
- **Token/cost tracking** – ✅
- **Tool-call level attribution** – ✅

### Git Operations Support

- **`git rebase`** – ✅ Attribution preserved
- **`git cherry-pick`** – ✅
- **`git stash` / `pop`** – ✅
- **`git merge --squash`** – ✅
- **`git reset` (soft/mixed/hard)** – ✅
- **`git merge` (merge commit)** – ✅
- **`git commit --amend`** – ✅
- **`git checkout` / `switch`** – ✅
- **`git pull`** – ✅
- **`git push` / `fetch`** – ✅ Notes synced
- **`git mv`** – ❌ Renames not tracked
- **`git filter-branch`** – ❌ Bulk rewrites not tracked
- **`git replace`** – ❌ Object replacements not tracked

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

## Observations from This Test

1. **Installation is seamless** – The installer automatically detected and updated hooks for OpenCode, Claude Code, and GitHub Copilot

2. **No per-repo setup required** – Git AI works immediately in any git repository after global installation

3. **Plugin integration is robust** – The OpenCode plugin hooks into the standard `tool.execute.*` events and handles both file operations and bash commands

4. **Attribution data is local-first** – By default, prompts are stored in a local SQLite database (`~/.git-ai/internal/transcripts-db`), keeping repos lean and sensitive data private

5. **Git notes are git-native** – Attribution travels with commits via `refs/notes/ai`, which can be pushed to remotes that support notes

6. **OhMyOpenAgent compatibility** – The plugin works with OhMyOpenAgent (the OpenCode fork used in this setup) because it uses the standard OpenCode plugin API

## Next Steps

To fully verify the integration:

1. Make an edit using OpenCode with git-ai installed
2. Commit the change
3. Run `git ai stats` to see AI attribution
4. Run `git log --show-notes="ai"` to see the attribution metadata
5. Run `git ai blame <file>` to see line-level attribution

## References

- [Git AI Documentation](https://usegitai.com/docs/agents/opencode)
- [Git AI GitHub Repository](https://github.com/git-ai-project/git-ai)
- [OpenCode Plugin API](https://opencode.ai/docs/plugins/)
- [Git AI Standard Specification](https://github.com/git-ai-project/git-ai/blob/main/specs/git_ai_standard_v3.0.0.md)
