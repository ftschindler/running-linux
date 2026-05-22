---
title: PKB Tech Stack Plan
---

- **Date:** 2026-05-20
- **Context:** Planning a publishable Personal Knowledge Base (PKB) as a git-based static site

## Requirements

A git repository containing Markdown files and Excalidraw diagrams, built into a static site via
GitHub Actions and deployable to GitHub Pages. The repository must support three usage scenarios
equally well:

### Usage Scenario 1 (default): Text Editor + excalidraw.com

Any contributor with a text editor and a browser can:

1. Edit `.md` files in any editor (VS Code, vim, etc.)
2. Create/edit diagrams on [excalidraw.com](https://excalidraw.com) and save `.excalidraw` files
   into the repository
3. Build and preview the site locally
4. Push changes; CI builds and deploys

No proprietary tooling required.

### Usage Scenario 2: Obsidian + Excalidraw Plugin

A contributor with [Obsidian](https://obsidian.md) (free for commercial use since Feb 2025) and
the [Excalidraw plugin](https://github.com/zsviczian/obsidian-excalidraw-plugin) installed can:

1. Open the repository folder as an Obsidian vault
2. Edit `.md` files with full Obsidian UX (callouts, graph view, backlinks)
3. Create/edit diagrams directly within Obsidian via the Excalidraw plugin
4. Build and preview the site locally
5. Push changes; CI builds and deploys

Obsidian is a first-class citizen but never a requirement.

### Usage Scenario 3: CI (GitHub Actions)

On push to `main` (and on PRs for validation):

1. Checkout repository (including large files)
2. Build site
3. Deploy to GitHub Pages

### Cross-Platform Constraint

Local builds must work identically on Linux, macOS and Windows with minimal prerequisites.

### Additional Constraints

- Excalidraw diagrams stored as `.excalidraw` files (standard JSON format) with git LFS
- The rendered site must support a light/dark mode toggle with diagrams adapting accordingly
- All tooling must be free for commercial use
- Single source of truth per diagram (no pre-rendered exports to keep in sync)

## Tech Stack

### Static Site Generator: [MkDocs](https://www.mkdocs.org/) + [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

**Why MkDocs:**

- Python-based, cross-platform via `uv` (single tool manages Python version + packages)
- Massive plugin ecosystem (300+ plugins)
- Simple configuration (`mkdocs.yml`)
- Fast builds, live-reload dev server

**Why Material for MkDocs:**

- MIT-licensed, all features free (Insiders tier discontinued Nov 2025)
- Built-in light/dark mode toggle
- Excellent search, admonitions, tabs, content tabs, annotations
- Native Mermaid diagram support
- Responsive, accessible, well-maintained

**Consideration:** The MkDocs ecosystem is in transition. MkDocs 1.x is unmaintained (no releases
in 18 months). MkDocs 2.0 is a ground-up rewrite that
[removes the plugin system entirely](https://squidfunk.github.io/mkdocs-material/blog/2026/02/18/mkdocs-2.0/)
and is incompatible with Material for MkDocs. Material for MkDocs 9.7.5 pins `mkdocs<2` so builds
remain stable today. The Material team is building
[Zensical](https://zensical.org/) as a drop-in replacement for MkDocs 1.x, preserving the plugin
API and theme compatibility. The expected migration path is: `mkdocs` → `zensical` (a dependency
swap, not a rewrite). Our plugin dependencies are small and simple, so adapting them if needed is
low-effort.

### Excalidraw Rendering: [mkdocs-excalidraw](https://github.com/qdeli187/mkdocs-excalidraw)

**Why:**

- Renders `.excalidraw` files (standard JSON format) to SVG client-side using the official
  [`@excalidraw/excalidraw`](https://www.npmjs.com/package/@excalidraw/excalidraw) library
- Automatic dark/light mode support: detects Material's `data-md-color-media` attribute via
  `MutationObserver`, re-renders with appropriate theme on toggle
- Single source of truth: only `.excalidraw` files are committed (no pre-rendered SVGs)
- Lightbox support via [`mkdocs-glightbox`](https://github.com/blueswen/mkdocs-glightbox)

**How it works:**

1. At build time: `![](diagram.excalidraw)` is transformed into an
   `<excalidraw-renderer src="diagram.excalidraw">` custom element
2. At runtime: the browser fetches the `.excalidraw` JSON and renders it to SVG with the current
   theme baked in
3. On theme toggle: `MutationObserver` detects the change and triggers a re-render

**Consideration:** Small project (8 stars as of May 2026). The implementation is thin (~200 lines)
and uses the official Excalidraw rendering library. If unmaintained in future, it can be forked or
replaced with a custom MkDocs hook.

### Obsidian Compatibility: [mkdocs-obsidian-support-plugin](https://github.com/ndy2/mkdocs-obsidian-support-plugin)

**Why:**

- Converts Obsidian callouts (`> [!note]`) to Material admonitions at build time
- Handles Obsidian comments and tags

**Convention:** Standard Markdown links (`[text](path.md)`) are used throughout — not wiki-links.
Obsidian is configured via a shipped `.obsidian/app.json` with `"useMarkdownLinks": true` so that
its link autocomplete generates standard Markdown links.

**Enforced:** A pre-commit hook forbids Obsidian note embeds (`![[...]]`) which have no standard
Markdown equivalent and would require additional build-time conversion.

### Backlinks: [mkdocs-backlinks-section-plugin](https://github.com/six-two/mkdocs-backlinks-section-plugin)

**Why:**

- Automatically appends a "Backlinks" section to the bottom of each page listing all pages that
  link to it
- Works with Material out of the box (no theme template modifications)
- Zero configuration beyond adding the plugin to `mkdocs.yml`

**Consideration:** Small project (8 stars as of May 2026, MIT). Simple implementation, easy to
fork if needed.

### Python Toolchain: [uv](https://docs.astral.sh/uv/)

**Why:**

- Single binary, installs in seconds, works on Linux/macOS/Windows
- Manages Python versions (via `.python-version` in the repo)
- Manages dependencies (via `pyproject.toml` or `requirements.txt`)
- No system Python required: `uv run mkdocs serve` handles everything
- Deterministic installs via lockfile

### Version Control: Git + [LFS](https://git-lfs.com/)

**Why LFS for `.excalidraw` files:**

- Excalidraw JSON files can grow large (complex diagrams with many elements)
- Binary-like change patterns (JSON diffs are not meaningful for diagrams)
- Keeps the git history lightweight

## Repository Structure

```text
my-pkb/
├── docs/                              # content root
│   ├── index.md
│   ├── some_topic.md                  # plain Markdown, standard [text](path.md) links
│   └── diagrams/
│       └── architecture.excalidraw    # single source of truth per diagram
├── .scripts/                          # pre-commit helper scripts
│   └── check_excalidraw_settings.py   # validates Excalidraw plugin config
├── mkdocs.yml                         # MkDocs configuration
├── pyproject.toml                     # Python dependencies (managed by uv)
├── uv.lock                            # deterministic dependency resolution
├── .python-version                    # Python version pinning (e.g. 3.12)
├── .gitattributes                     # LFS rules
├── .gitignore                         # includes .obsidian/ selective tracking
├── .pre-commit-config.yaml            # lint + format + guards
├── .markdownlint-cli2.jsonc           # markdownlint rules
├── .pymarkdown.json                   # pymarkdown rules
├── .markdown_link_check_config.json   # link checker config
├── .obsidian/                         # shipped Obsidian vault config
│   ├── app.json                       # useMarkdownLinks, attachmentFolderPath
│   ├── backlink.json                  # backlink pane configuration
│   ├── community-plugins.json         # enabled community plugins
│   ├── core-plugins.json              # enabled/disabled core plugins
│   └── plugins/
│       └── obsidian-excalidraw-plugin/
│           └── data.json              # plugin settings (file format, embeds, no auto-export)
├── .github/
│   └── workflows/
│       └── deploy.yml                 # build + deploy
└── README.md
```

## Configuration Notes

### `.gitattributes`

```gitattributes
* text eol=lf
*.excalidraw filter=lfs diff=lfs merge=lfs -text
```

### `.python-version`

```text
3.13
```

### `pyproject.toml` (dependencies)

```toml
[project]
name = "my-pkb"
requires-python = ">=3.12"
dependencies = [
    # MkDocs 2.0 removes the plugin system and is incompatible with Material for MkDocs.
    # Pin to <2 until Zensical (https://zensical.org/) is ready as a drop-in replacement.
    # See: https://squidfunk.github.io/mkdocs-material/blog/2026/02/18/mkdocs-2.0/
    "mkdocs>=1.6,<2",
    "mkdocs-material",
    "mkdocs-obsidian-support-plugin",
    "mkdocs-backlinks-section-plugin",
    "mkdocs-excalidraw",
    "mkdocs-glightbox",
]
```

### `mkdocs.yml` (key sections)

```yaml
site_name: My PKB
repo_url: https://github.com/your-org/your-pkb
edit_uri: edit/main/docs/

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - search
  - obsidian-support
  - backlinks_section
  - excalidraw
  - glightbox

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - toc:
      permalink: true
```

### Obsidian Excalidraw Plugin Configuration

Enforced via shipped `.obsidian/plugins/obsidian-excalidraw-plugin/data.json` and validated by a
pre-commit hook. Contributors opening the folder as a vault get the correct settings
automatically — no manual configuration needed. However, the Excalidraw plugin itself must be
installed manually (see below).

### `.obsidian/app.json`

Shipped in the repository so that contributors opening the folder as a vault get the correct
defaults:

```json
{
  "useMarkdownLinks": true,
  "attachmentFolderPath": "./"
}
```

| Setting | Value | Why |
|---|---|---|
| `useMarkdownLinks` | `true` | Obsidian's link autocomplete generates standard Markdown links (`[text](path.md)`) instead of wiki-links (`[[path]]`) |
| `attachmentFolderPath` | `"./"` | New attachments (including Excalidraw drawings) are created in the same folder as the active file, not at the vault root. This keeps diagrams alongside the Markdown files that reference them |

### `.obsidian/community-plugins.json`

Tells Obsidian which community plugins are enabled:

```json
["obsidian-excalidraw-plugin"]
```

### `.obsidian/` Version Control

The `.obsidian/` directory contains a mix of shared configuration (safe to track) and
device-specific state (must be ignored). The `.gitignore` ignores everything by default, then
explicitly allows shared files:

```gitignore
# Obsidian: ignore everything by default, then allow shared config
.obsidian/*
!.obsidian/app.json
!.obsidian/backlink.json
!.obsidian/community-plugins.json
!.obsidian/core-plugins.json
!.obsidian/plugins/
.obsidian/plugins/*
!.obsidian/plugins/obsidian-excalidraw-plugin/
.obsidian/plugins/obsidian-excalidraw-plugin/*
!.obsidian/plugins/obsidian-excalidraw-plugin/data.json
```

**Tracked files** (shared configuration):

| File | Purpose |
|---|---|
| `app.json` | Markdown link format, attachment folder |
| `backlink.json` | Backlink pane configuration |
| `community-plugins.json` | List of enabled community plugins |
| `core-plugins.json` | Enabled/disabled core plugins |
| `plugins/obsidian-excalidraw-plugin/data.json` | Excalidraw plugin settings |

**Ignored files** (device-specific or auto-downloaded):

| File | Why |
|---|---|
| `workspace.json` | Editor state (open tabs, pane layout, cursor positions) — causes merge conflicts |
| `plugins/*/main.js` | Plugin runtime code — auto-downloaded from community registry |
| `plugins/*/manifest.json` | Plugin metadata — redundant with `community-plugins.json` |
| `plugins/*/styles.css` | Plugin styles — included in plugin download |
| `cache/` | Internal cache — regenerated automatically |

**Gotcha — Obsidian does not auto-install plugins:** When a contributor opens the vault for the
first time, Obsidian reads `community-plugins.json` but silently ignores entries for plugins that
are not installed. There is no installation prompt or error notification. Contributors must
manually install the Excalidraw plugin via **Settings > Community plugins**. Document this in
a setup guide within the repository.

### `.obsidian/plugins/obsidian-excalidraw-plugin/data.json`

```json
{
  "compatibilityMode": true,
  "compress": false,
  "autoexportSVG": false,
  "autoexportPNG": false,
  "embedWikiLink": false
}
```

| Setting | Value | Why |
|---|---|---|
| `compatibilityMode` | `true` | Saves as `.excalidraw` (standard JSON), editable on excalidraw.com. Despite the name, this is the setting that produces the portable format — without it, files are saved as `.excalidraw.md` (Obsidian-specific markdown wrapper) regardless of other settings |
| `compress` | `false` | Prevents zlib compression of drawing data. Compressed data requires the `.excalidraw.md` wrapper format, which is incompatible with `mkdocs-excalidraw` |
| `autoexportSVG` | `false` | Rendering handled client-side by `mkdocs-excalidraw`; no exported SVGs to keep in sync |
| `autoexportPNG` | `false` | Same reasoning — no pre-rendered exports |
| `embedWikiLink` | `false` | When the plugin embeds a drawing into a document, use standard Markdown syntax (`![](drawing.excalidraw)`) instead of Obsidian wiki-link syntax (`![[drawing.excalidraw]]`). Wiki-link embeds are not valid Markdown and break the MkDocs build |

**Gotcha — misleading setting names:** The plugin's setting names are counterintuitive.
`compatibilityMode` sounds like a fallback, but it is the _only_ way to get standard `.excalidraw`
output. `useExcalidrawExtension` (which appears in the plugin's full config) does _not_ control
the `.excalidraw` extension — with `useExcalidrawExtension: true`, files are saved as
`.excalidraw.md` (Obsidian wrapper with the `.excalidraw` extension prefix). The
[source code](https://github.com/zsviczian/obsidian-excalidraw-plugin/blob/2bfb381/src/utils/fileUtils.ts#L133-L145)
confirms this logic.

**Gotcha — compression forces `.excalidraw.md`:** Even with `compatibilityMode: true`, if
`compress` is `true` (the plugin's default), drawing data is zlib-compressed and stored in a
fenced `compressed-json` code block inside an `.excalidraw.md` file. Always set `compress: false`.

A pre-commit hook (`check-excalidraw-settings`) validates these settings on every commit — see
below.

### [`.pre-commit-config.yaml`](https://pre-commit.com/)

[Pre-commit](https://pre-commit.com/) hooks ensure Markdown quality and repository hygiene.
Inspired by the hooks used in the
[running-linux](https://github.com/ftschindler/running-linux) PKB.

```yaml
repos:
  # -- Markdown linting and canonicalisation --

  - repo: https://github.com/DavidAnson/markdownlint-cli2
    rev: v0.18.1
    hooks:
      - id: markdownlint-cli2
        files: \.md$
        args: [--config=.markdownlint-cli2.jsonc, --fix]

  - repo: https://github.com/jackdewinter/pymarkdown
    rev: v0.9.33
    hooks:
      - id: pymarkdown
        name: PyMarkdown linter
        files: \.md$
        args: [fix]
        pass_filenames: true

  # -- Link validation --

  - repo: https://github.com/tcort/markdown-link-check
    rev: v3.12.2
    hooks:
      - id: markdown-link-check
        args: [--quiet, --config=.markdown_link_check_config.json]

  # -- YAML/JSON formatting --

  - repo: https://github.com/google/yamlfmt
    rev: v0.16.0
    hooks:
      - id: yamlfmt

  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.33.0
    hooks:
      - id: check-jsonschema
        name: Validate markdownlint-cli2 config schema
        files: .markdownlint-cli2.jsonc
        args: [--schemafile, 'https://raw.githubusercontent.com/DavidAnson/markdownlint-cli2/main/schema/markdownlint-cli2-config-schema.json']

  # -- GitHub Actions linting --

  - repo: https://github.com/rhysd/actionlint
    rev: v1.7.1
    hooks:
      - id: actionlint

  # -- Custom guards --

  - repo: local
    hooks:
      - id: no-obsidian-embeds
        name: Forbid Obsidian note embeds
        entry: '!\[\['
        language: pygrep
        files: '\.md$'
      - id: check-excalidraw-settings
        name: Check Excalidraw plugin settings for mkdocs compatibility
        entry: uv run --script .scripts/check_excalidraw_settings.py
        language: system
        pass_filenames: false
        files: '^\.obsidian/plugins/obsidian-excalidraw-plugin/data\.json$'

  # -- General file hygiene (should go last as it fixes line endings) --

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: check-added-large-files
      - id: check-case-conflict
      - id: mixed-line-ending
        args: [--fix=lf]
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: pretty-format-json
        args: [--autofix, --no-sort-keys, --indent=4]
      - id: check-symlinks
      - id: fix-byte-order-marker
```

**Purpose of each layer:**

| Layer | Hook | Role |
|---|---|---|
| Markdown lint | [`markdownlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2) | Structural rules (headings, lists, spacing) with auto-fix |
| Markdown lint | [`pymarkdown`](https://github.com/jackdewinter/pymarkdown) | Complementary rules (tab handling, heading increments) with auto-fix |
| Link validation | [`markdown-link-check`](https://github.com/tcort/markdown-link-check) | Catches broken internal links before they reach the site |
| Format | [`yamlfmt`](https://github.com/google/yamlfmt) | Canonical YAML formatting (configs, frontmatter) |
| Schema | [`check-jsonschema`](https://github.com/python-jsonschema/check-jsonschema) | Validates linter config against upstream schema |
| CI lint | [`actionlint`](https://github.com/rhysd/actionlint) | Catches GitHub Actions workflow errors |
| Guard | `no-obsidian-embeds` (local) | Prevents `![[embed]]` syntax entering the repo |
| Guard | `check-excalidraw-settings` (local) | Validates Excalidraw plugin settings (`compatibilityMode`, `compress`, `autoexportSVG`, `autoexportPNG`, `embedWikiLink`) against required values for `mkdocs-excalidraw` compatibility |
| Hygiene | [`pre-commit-hooks`](https://github.com/pre-commit/pre-commit-hooks) | Trailing whitespace, LF line endings, large files, BOM removal |

**Configuration files to ship:**

- `.markdownlint-cli2.jsonc` — markdownlint rules (disable line length, allow frontmatter title)
- `.pymarkdown.json` — pymarkdown rules (heading increments, list spacing)
- `.markdown_link_check_config.json` — link checker config (skip external URLs to avoid flaky
  checks, skip `.excalidraw` references)

### `.markdownlint-cli2.jsonc`

```jsonc
{
  "config": {
    "default": true,
    // MD013: Line length — disabled; prose wraps naturally, enforcing length hurts readability
    "MD013": false,
    // MD028: Blank line inside blockquote — disabled; Obsidian callouts use this pattern
    "MD028": false,
    // MD029: Ordered list item prefix — allow both 1. 1. 1. and 1. 2. 3. styles
    "MD029": { "style": "one_or_ordered" },
    // MD033: No inline HTML — disabled elements can be added here if needed
    "MD033": { "allowed_elements": [] },
    // MD041: First line should be a top-level heading — recognise frontmatter title field
    "MD041": { "level": 1, "front_matter_title": "^\\s*title\\s*[:=]" }
  }
}
```

**Rationale for each override:**

| Rule | Override | Why |
|---|---|---|
| MD013 | disabled | Prose-heavy PKB content should wrap naturally; hard line breaks create noisy diffs |
| MD028 | disabled | Obsidian callouts (`> [!note]`) produce blank lines inside blockquotes |
| MD029 | `one_or_ordered` | Both `1. 1. 1.` (easy reordering) and `1. 2. 3.` (explicit) are acceptable |
| MD033 | empty allow list | No inline HTML by default; add elements as needed |
| MD041 | frontmatter-aware | Files use YAML frontmatter `title:` instead of a `#` heading on line 1 |

### `.pymarkdown.json`

```json
{
    "plugins": [],
    "extensions": [],
    "config": {
        "line-length": {
            "enabled": false
        },
        "no-hard-tabs": {
            "enabled": true
        },
        "spaces-after-list-marker": {
            "enabled": true,
            "punctuation": "consistent"
        },
        "list-marker-space": {
            "enabled": true
        },
        "ol-prefix": {
            "enabled": true,
            "style": "ordered"
        },
        "blanks-around-headings": {
            "enabled": true
        },
        "heading-increment": {
            "enabled": true
        }
    }
}
```

**Rationale for each rule:**

| Rule | Setting | Why |
|---|---|---|
| `line-length` | disabled | Same reasoning as MD013 — prose wraps naturally |
| `no-hard-tabs` | enabled | Spaces only; tabs render inconsistently across tools |
| `spaces-after-list-marker` | consistent | Enforces uniform spacing within a document |
| `list-marker-space` | enabled | Requires space after list markers (`- item`, not `-item`) |
| `ol-prefix` | ordered | Ordered lists use `1. 2. 3.` (matches MD029 allowing both) |
| `blanks-around-headings` | enabled | Headings must have blank lines above/below for readability |
| `heading-increment` | enabled | No skipping heading levels (e.g., `##` directly after `####`) |

### `.markdown_link_check_config.json`

```json
{
    "ignorePatterns": [
        {
            "pattern": "^https?://",
            "comment": "Skip external URLs — avoids flaky failures from network issues and rate limiting"
        },
        {
            "pattern": "^mailto:"
        },
        {
            "pattern": ".*\\.excalidraw$",
            "comment": "Excalidraw files are rendered client-side, not resolvable as link targets"
        }
    ],
    "timeout": "100ms"
}
```

**Rationale:**

- **External URLs skipped:** External link checking is inherently flaky (rate limits, transient
  downtime, geo-blocking). Internal link integrity is what matters for a PKB — broken cross-
  references between pages are the real risk.
- **`.excalidraw` ignored:** These are referenced as image sources (`![](file.excalidraw)`) and
  rendered client-side by the plugin. The link checker cannot resolve them as document targets.
- **100ms timeout:** Fast-fail for any remaining checks; internal file lookups should be instant.

### GitHub Actions (`deploy.yml`)

```yaml
name: Build and Deploy
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true

      - uses: astral-sh/setup-uv@v5
        # https://github.com/astral-sh/setup-uv

      - name: Build site
        run: uv run mkdocs build --strict

      - uses: actions/upload-pages-artifact@v3
        with:
          path: site/

  deploy:
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
```

## Licensing Summary

| Component | Licence | Commercial Use |
|---|---|---|
| [MkDocs](https://github.com/mkdocs/mkdocs) | BSD-2-Clause | Free |
| [Material for MkDocs](https://github.com/squidfunk/mkdocs-material) | MIT | Free |
| [mkdocs-excalidraw](https://github.com/qdeli187/mkdocs-excalidraw) | MIT | Free |
| [mkdocs-obsidian-support-plugin](https://github.com/ndy2/mkdocs-obsidian-support-plugin) | MIT | Free |
| [mkdocs-backlinks-section-plugin](https://github.com/six-two/mkdocs-backlinks-section-plugin) | MIT | Free |
| [mkdocs-glightbox](https://github.com/blueswen/mkdocs-glightbox) | MIT | Free |
| [Obsidian](https://obsidian.md) (optional editor) | Proprietary | Free (since Feb 2025) |
| [Obsidian Excalidraw Plugin](https://github.com/zsviczian/obsidian-excalidraw-plugin) | MIT | Free |

## Open Questions

- **MkDocs → Zensical migration:** Monitor [Zensical](https://zensical.org/) compatibility with
  our plugins. When Zensical reaches stable and supports our plugin set, swap `mkdocs` for
  `zensical` in `pyproject.toml`. This should be a one-line dependency change if MkDocs 1.x API
  compatibility holds. Track progress via the
  [Zensical compatibility table](https://zensical.org/compatibility/features/).
- **MkDocs 1.x security:** MkDocs 1.x is unmaintained. No known vulnerabilities today, but
  monitor. If a security issue arises before Zensical is ready, evaluate pinning or patching.
- **mkdocs-excalidraw maturity:** Small project. Consider vendoring or forking if it becomes
  unmaintained.
- **Graph view:** Not available with this stack. Accept that this is a Quartz/Obsidian Publish
  feature we consciously trade away for simplicity and portability.
