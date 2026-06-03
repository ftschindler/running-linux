# 2026-06-03 – Install & Configure oh‑my‑openagent (OpenCode)

**Context** – This guide assumes you already have an OVHcloud AI Endpoints subscription configured in OpenCode (the "OVH" article in `content/done/20260603‑opencode‑ovh‑oh‑my‑opencode.md`). We therefore **skip all subscription questions** and directly run the Ultimate installer.

---

## Prerequisites

1. **OpenCode** version ≥ `1.0.150` installed and on your `$PATH`.
2. **Bun** (the JS runtime) – required for the installer (`bunx`).
3. Network connectivity to `https://github.com/code-yeongyu/oh‑my‑openagent`.

Verify OpenCode:

```bash
opencode --version
```

If the command fails, install OpenCode first (see the OVH article).

---

## Step 0 – Prepare a non‑interactive install

Because the OVH subscription is already active we can tell the installer to **skip all subscription prompts**:

```bash
export OMO_SKIP_SUBSCRIPTIONS=1   # tell the installer to skip the subscription interview
```

> The installer also respects `--skip-auth` to bypass provider OAuth prompts.

---

## Step 1 – Run the Ultimate installer

```bash
bunx oh‑my‑openagent install \
  --no‑tui \
  --platform=opencode \
  --skip‑auth \
  --claude=no \
  --gemini=no \
  --copilot=no
```

The `--claude`/`--gemini`/`--copilot` flags are required by the installer even when OVH is our only provider. We set them to `no`.

What the command does:

- Registers the plugin `"oh‑my‑openagent"` in `opencode.json`.
- Writes a **default** model config (all agents → `opencode/gpt-5-nano`) — the installer doesn't auto-detect OVH.
- We will replace that default with the actual OVH models in Step 3.

---

## Step 2 – Verify the plugin is loaded

```bash
opencode --version   # should still print the same version
bunx oh‑my‑openagent doctor   # health‑check, should report no errors
```

You should see the **plugin array** in `~/.config/opencode/opencode.json` contain:

```json
"plugin": ["oh‑my‑openagent"]
```

Now confirm the OVH models are actually available:

```bash
opencode models | grep ovhcloud
```

You should see all the OVH models listed (`qwen3.6-27b`, `gpt-oss-120b`, `qwen3.5-9b`, `qwen3.5-397b-a17b`, etc.). If nothing shows up, run `/connect` inside OpenCode and re-authenticate OVH first.

---

## Step 3 – Override the default model config with OVH recommendations

Replace the contents of `~/.config/opencode/oh‑my‑openagent.json` (created by the installer) with the full OVH config below. This maps every category and agent to the OVH models, and **enables Team Mode** with 4 parallel agents:

```json
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",
  "team_mode": {
    "enabled": true,
    "max_parallel_members": 4
  },
  "categories": {
    "visual-engineering": {
      "model": "ovhcloud/qwen3.6-27b",
      "fallback_models": [
        "ovhcloud/qwen2.5-vl-72b-instruct",
        "ovhcloud/mistral-small-3.2-24b-instruct-2506"
      ]
    },
    "deep": {
      "model": "ovhcloud/gpt-oss-120b",
      "fallback_models": [
        "ovhcloud/qwen3.5-397b-a17b",
        "ovhcloud/qwen3-32b"
      ]
    },
    "quick": {
      "model": "ovhcloud/qwen3.5-9b",
      "fallback_models": [
        "ovhcloud/gpt-oss-20b",
        "ovhcloud/mistral-7b-instruct-v0.3"
      ],
      "temperature": 0.3
    },
    "ultrabrain": {
      "model": "ovhcloud/qwen3.5-397b-a17b",
      "fallback_models": [
        "ovhcloud/gpt-oss-120b",
        "ovhcloud/meta-llama-3_3-70b-instruct"
      ],
      "temperature": 0.2
    },
    "artistry": {
      "model": "ovhcloud/qwen3.6-27b",
      "fallback_models": ["ovhcloud/gpt-oss-120b"]
    },
    "unspecified-low": {
      "model": "ovhcloud/qwen3.5-9b",
      "fallback_models": ["ovhcloud/gpt-oss-20b"]
    },
    "unspecified-high": {
      "model": "ovhcloud/gpt-oss-120b",
      "fallback_models": ["ovhcloud/qwen3.6-27b"]
    },
    "writing": {
      "model": "ovhcloud/qwen3.6-27b",
      "fallback_models": ["ovhcloud/qwen3-32b"]
    }
  },
  "agents": {
    "sisyphus": {
      "model": "ovhcloud/gpt-oss-120b",
      "fallback_models": ["ovhcloud/qwen3.6-27b", "ovhcloud/qwen3.5-397b-a17b"]
    },
    "hephaestus": {
      "model": "ovhcloud/gpt-oss-120b",
      "fallback_models": ["ovhcloud/qwen3.5-397b-a17b"]
    },
    "oracle": {
      "model": "ovhcloud/qwen3.5-397b-a17b",
      "fallback_models": ["ovhcloud/gpt-oss-120b"]
    },
    "explore": {
      "model": "ovhcloud/qwen3.5-9b",
      "fallback_models": ["ovhcloud/gpt-oss-20b"]
    },
    "librarian": {
      "model": "ovhcloud/qwen3.5-9b",
      "fallback_models": ["ovhcloud/gpt-oss-20b"]
    },
    "multimodal-looker": {
      "model": "ovhcloud/qwen3.6-27b",
      "fallback_models": ["ovhcloud/mistral-small-3.2-24b-instruct-2506"]
    },
    "prometheus": {
      "model": "ovhcloud/gpt-oss-120b",
      "fallback_models": ["ovhcloud/qwen3.5-397b-a17b"]
    },
    "metis": {
      "model": "ovhcloud/qwen3.6-27b",
      "fallback_models": ["ovhcloud/gpt-oss-120b"]
    },
    "momus": {
      "model": "ovhcloud/qwen3.5-397b-a17b",
      "fallback_models": ["ovhcloud/gpt-oss-120b"]
    },
    "atlas": {
      "model": "ovhcloud/gpt-oss-120b",
      "fallback_models": ["ovhcloud/qwen3.6-27b"]
    },
    "sisyphus-junior": {
      "model": "ovhcloud/gpt-oss-120b",
      "fallback_models": ["ovhcloud/qwen3.6-27b"]
    }
  }
}
```

**Important:** After writing the config, **restart OpenCode** (exit and start a new session) so the new model mappings and Team Mode take effect.

---

## Step 4 – Confirm model availability

```bash
# List the OVH models that the OpenCode provider currently knows about
/opencode models list | grep ovhcloud
```

You should see at least the four primary models (`qwen3.6‑27b`, `gpt‑oss‑120b`, `qwen3.5‑9b`, `qwen3.5‑397b‑a17b`). If a model is missing, run:

```bash
opencode models refresh   # forces a fresh catalog download from OVH
```

---

## Step 5 – Quick functional test

Run the built‑in `doctor` again (already done) and then a simple category test:

```bash
# Visual‑engineering test (frontend UI)
echo "Create a simple React button component" | opencode

# Quick test (single‑file edit)
echo "Fix the typo in README.md line 42" | opencode
```

The output should indicate the agent selected the appropriate category and used the corresponding model.

---

## Step 6 – Team Mode (now enabled)

Team Mode is oh-my-openagent's multi-agent orchestration layer. When enabled (it is, in the config above), the lead agent can spawn up to `max_parallel_members` specialist agents running **in parallel**, communicating via dedicated `team_*` tools (`team_create`, `team_send_message`, `team_task_create`, etc.).

Two skills ride on Team Mode out of the box:

- **`hyperplan`** — 5 hostile critics tear apart a plan from orthogonal angles before any code is written.
- **`security-research`** — 3 vulnerability hunters + 2 PoC engineers audit your codebase in parallel.

Adjust `max_parallel_members` (1-8) in the config if needed. The `tmux_visualization` option (disabled by default) shows each member's workspace in a tmux grid.

---

## Summary

- **Skip subscriptions** – use `--no‑tui --skip‑auth` (and `OMO_SKIP_SUBSCRIPTIONS=1`).
- **Use OVH‑recommended models** – set them in `~/.config/opencode/oh‑my‑openagent.json` as shown.
- **Team Mode enabled** by default with 4 parallel agents.
- **Restart OpenCode** after any config change.
- **Verify** with `bunx oh‑my‑openagent doctor` and a couple of quick prompts.

You are now ready to use `oh‑my‑openagent` with the same OVH model stack you already have configured for OpenCode.
