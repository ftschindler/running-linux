---
title: Using Obsidian
---

This repository can be opened as an [Obsidian](https://obsidian.md) vault. Core settings
(link format, attachment folder, enabled core plugins) are shipped in the `.obsidian/` directory
and apply automatically.

## First-time setup

After cloning the repository and opening the folder as an Obsidian vault for the first time:

1. Obsidian will ask whether to **trust community plugins** for this vault. Choose _Trust author
   and enable plugins_.

2. Open **Settings > Community plugins** and install the
   [Excalidraw](https://github.com/zsviczian/obsidian-excalidraw-plugin) plugin. The plugin's
   configuration is already tracked in the repository and will apply once the plugin is installed.

That is all — no further configuration is needed.

## What is shipped in the repository

The following `.obsidian/` files are tracked in Git so that all contributors share the same
defaults:

| File                                           | Purpose                                 |
| ---------------------------------------------- | --------------------------------------- |
| `app.json`                                     | Markdown link format, attachment folder |
| `backlink.json`                                | Backlink pane configuration             |
| `community-plugins.json`                       | List of enabled community plugins       |
| `core-plugins.json`                            | Enabled/disabled core plugins           |
| `plugins/obsidian-excalidraw-plugin/data.json` | Excalidraw plugin settings              |

Everything else (workspace layout, plugin runtime files, caches) is gitignored and local to each
contributor's machine.

## Excalidraw in Obsidian

The shipped plugin settings ensure diagrams are saved in the correct format. See
[Editing Conventions](editing_conventions.md#excalidraw-diagrams) for the full conventions on
diagram format, referencing and exports.
When editing a page, open the _command palette_ (`CTRL + p` by default) and choose one of excalidraws create + embed options to create a diagram that is embedded into and placed beside the page.

## What to avoid

See [Editing Conventions](editing_conventions.md) for the full list. In particular, Obsidian
users should be aware of:

- **Wiki-links** (`[[page]]`) — the shipped `app.json` configures link autocomplete to use
  standard Markdown format instead.
- **Note embeds** (exclamation mark followed by `[[file]]`) — rejected by a pre-commit hook.
