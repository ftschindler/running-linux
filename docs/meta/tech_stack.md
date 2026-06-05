---
title: Tech Stack
---

This site is a git-backed static site built from Markdown files and
[Excalidraw](https://excalidraw.com) diagrams. For the full design rationale, see the
[PKB Tech Stack](../done/20260520-pkb-tech-stack.md) document.

## Static site generator

- **[MkDocs](https://www.mkdocs.org/)** with
  **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** as the theme

## MkDocs plugins

- **[mkdocs-awesome-pages-plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)** —
  flexible navigation ordering without maintaining a full nav tree
- **[mkdocs-excalidraw](https://github.com/qdeli187/mkdocs-excalidraw)** — client-side rendering
  of `.excalidraw` diagrams with automatic light/dark mode support
- **[mkdocs-obsidian-support-plugin](https://github.com/ndy2/mkdocs-obsidian-support-plugin)** —
  converts Obsidian callouts to Material admonitions
- **[mkdocs-backlinks-section-plugin](https://github.com/six-two/mkdocs-backlinks-section-plugin)**
  — automatic backlink sections
- **[mkdocs-glightbox](https://github.com/blueswen/mkdocs-glightbox)** — image lightbox support

## Tooling

- **[uv](https://docs.astral.sh/uv/)** — Python toolchain (manages Python version and
  dependencies)
- **Git LFS** — large file storage for `.excalidraw` files
- **[Pre-commit](https://pre-commit.com/)** — enforces markdown quality, link integrity and
  repository hygiene (see [Editing Conventions](editing_conventions.md) and
  [Local Dev Environment](local_dev_environment.md) for setup)

## CI / CD

On push to `main`, a GitHub Actions workflow builds the site with
`uv run mkdocs build --strict` and deploys it to GitHub Pages.
