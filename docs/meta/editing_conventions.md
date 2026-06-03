---
title: Editing Conventions
---

These conventions keep content consistent and ensure the site builds correctly. Most are
enforced automatically by [pre-commit hooks](local_dev_environment.md#pre-commit-hooks)
and CI.

## Page structure

Every Markdown file should start with a YAML front matter block containing at least a
`title`:

```markdown
---
title: My Page Title
---

Page content starts here.
```

The title is used in the browser tab, the site navigation and search results. Without it,
MkDocs derives a title from the first heading or filename, which is often less readable.
There must thus be no other 1st level heading (`#`) on a page, the top-most Markdown header level is thus `##`.

## File naming

Filenames must be **lowercase** with **no whitespace**. Use underscores to separate words:

```text
local_dev_environment.md    ✓
Local Dev Environment.md    ✗
localDevEnvironment.md      ✗
```

This is enforced by the `lowercase-no-whitespace-filenames` pre-commit hook.

## Links

### Standard Markdown links

Use standard Markdown links with relative paths:

```markdown
[link text](path/to/page.md)
[section link](other_page.md#some-heading)
```

### What to avoid

- **Wiki-links** (`[[page]]`) — not standard Markdown. The shipped
  [Obsidian settings](using_obsidian.md#what-is-shipped-in-the-repository) configure link
  autocomplete to use standard Markdown format by default.
- **Note embeds** (exclamation mark followed by `[[file]]`) — no standard Markdown
  equivalent. Rejected by the `no-obsidian-embeds` pre-commit hook.
- **Absolute paths** (`/docs/meta/about.md`) — use relative paths so links work both on the
  rendered site and when browsing files on GitHub.

## Excalidraw diagrams

Diagrams are stored as standard `.excalidraw` JSON files (not the Obsidian-specific
`.excalidraw.md` wrapper). This is enforced by the `check-excalidraw-settings` pre-commit
hook and the shipped [Obsidian Excalidraw plugin settings](using_obsidian.md).
Diagrams (and images) should reside beside the page they are embedded in:

```text
some_page.md
some_page_diagram.excalidraw
```

Consider grouping multiple diagrams in a subdir with the pages name:

```text
some_page.md
some_page/
    diagram_1.excalidraw
    diagram_2.excalidraw
    ...
```

### Creating diagrams

- **In Obsidian** — use the
  [Excalidraw plugin](https://github.com/zsviczian/obsidian-excalidraw-plugin). The shipped
  plugin settings ensure the correct file format.
- **On the web** — create diagrams on [excalidraw.com](https://excalidraw.com) and save the
  `.excalidraw` file into the repository.

### Referencing diagrams

Embed a diagram in Markdown with:

```markdown
![](diagram.excalidraw)
```

The [mkdocs-excalidraw](tech_stack.md) plugin renders diagrams client-side with automatic
light/dark mode support.

### No pre-rendered exports

Do **not** commit SVG or PNG exports of diagrams. Rendering is handled client-side from the
`.excalidraw` source files.
