---
title: Local Dev Environment
---

A local environment lets you preview the site, run linters before pushing, and work with
any text editor. If you only need to make quick edits, see
[Editing on GitHub](editing_on_github.md) instead.

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) — the only global
dependency. uv manages the Python version and all Python packages for this project.

## Clone and preview

```bash
git clone https://github.com/ftschindler/running-linux.git
cd running-linux
uv run mkdocs serve
```

Open <http://127.0.0.1:8000> to see the site. Changes to Markdown files are reflected
immediately.

!!! tip

    A `Makefile` is included as an optional convenience. `make serve` is equivalent to the
    command above, and `make bootstrap` installs dependencies and pre-commit hooks in one step.
    Run `make` with no arguments to see all available targets.

## Pre-commit hooks

We use [prek](https://prek.j178.dev/) (a fast, drop-in replacement for
[pre-commit](https://pre-commit.com/)) to automatically run code quality checks (formatters,
linters, link checker). See
[`.pre-commit-config.yaml`](https://github.com/ftschindler/running-linux/blob/main/.pre-commit-config.yaml)
for the full list of checks.

prek is installed as a dev dependency via uv — no extra global tools required.

### Install hooks for this repository

```bash
uv run prek install
```

Or use the Makefile shortcut, which also syncs dependencies:

```bash
make bootstrap
```

## Pull request workflow

All changes are made via
[pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

If you are new to pull requests, see GitHub's guide on
[creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request),
or use the [GitHub web editor](editing_on_github.md) for a simpler workflow.
