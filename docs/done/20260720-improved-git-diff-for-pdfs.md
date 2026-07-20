---
title: A more informative git diff for pdfs
---

**Context:** PDFs stored in git (commonly via [git-lfs](https://git-lfs.com/)) diff as opaque binaries. This entry wires up a custom Git diff driver so `git diff` reports how many pixels changed per page, and an opt-in `PDF_VIEW=1 git diff` opens a visual GUI comparison — with graceful fallbacks when the tools or a display are unavailable.

## Goal

Three behaviours for PDF diffs, all machine-global (no per-collaborator config shared):

1. **`git diff file.pdf`** → if [`diff-pdf`](https://vslavik.github.io/diff-pdf/) is available, show per-page pixel-change counts.
2. **`PDF_VIEW=1 git diff file.pdf`** → open a GUI: [`diffpdf`](https://gitlab.com/eang/diffpdf) if present, else `diff-pdf --view`.
3. **Neither tool / no display / added-or-deleted file** → fall back to Git's standard binary-differ message.

## Prerequisites

Install the two comparison tools (Arch/Manjaro package names shown):

```bash
sudo pacman -S diff-pdf diffpdf
```

`diff-pdf` provides both the pixel-count text mode (`-v`) and a GUI (`--view`); `diffpdf` is a separate, more feature-rich Qt comparison GUI. Only `diff-pdf` is strictly required — `diffpdf` is optional and used preferentially for view mode.

## How Git wiring works

Git lets an attribute route a path to a named external diff driver. Three pieces connect them:

- A **global attributes file** maps `*.pdf` to a driver named `pdf` — kept in `~/.config/git/attributes` so it applies to every repository without committing anything to any repo.
- The **driver command** for `pdf` is registered in `~/.gitconfig`.
- The **driver script** receives both file versions and does the work.

Git invokes an external diff command with seven positional arguments:

```text
$1 path  $2 old-file  $3 old-hex  $4 old-mode  $5 new-file  $6 new-hex  $7 new-mode
```

The script uses `$2` (old) and `$5` (new). For an added or deleted file, Git passes `/dev/null` for the missing side.

### Keeping it private across many repos

Using a committed `.gitattributes` would share this behaviour with collaborators. Instead, Git's [`core.attributesFile`](https://git-scm.com/docs/gitattributes#_description) points at a **global** attributes file applied to every repository on the machine, committed to none. Attribute precedence is: in-tree `.gitattributes` → `.git/info/attributes` → `core.attributesFile`. Since no repo commits a `*.pdf` diff rule, the global file governs everywhere.

## Solution (Implemented)

### 1. Global attributes file

`~/.config/git/attributes`:

```text
*.pdf diff=pdf
```

### 2. Register the driver in `~/.gitconfig`

```ini
[core]
    attributesFile = ~/.config/git/attributes
[diff "pdf"]
    command = ~/.local/bin/git-pdf-diff.sh
```

### 3. The driver script

`~/.local/bin/git-pdf-diff.sh` (make it executable with `chmod +x`):

```bash
#!/usr/bin/env bash
# git external diff driver for PDF files.
#
# Wired up via ~/.gitconfig:
#     [core]
#         attributesFile = ~/.config/git/attributes   # contains: *.pdf diff=pdf
#     [diff "pdf"]
#         command = ~/.local/bin/git-pdf-diff.sh
#
# For git-lfs-tracked PDFs the repo's committed .gitattributes must set
#     *.pdf filter=lfs merge=lfs -text
# WITHOUT diff=lfs -- otherwise diff=lfs wins over our global diff=pdf and git
# shows the pointer oid instead of a pixel diff. Git runs the LFS smudge filter
# itself before calling this driver, so both sides arrive as real PDFs already.
#
# Git invokes this with 7 positional args:
#     $1 path  $2 old-file  $3 old-hex  $4 old-mode  $5 new-file  $6 new-hex  $7 new-mode
#
# Behaviour:
#   default            -> if diff-pdf present, show per-page pixel-change counts (diff-pdf -v)
#   PDF_VIEW=1 git diff -> open a GUI: diffpdf, else diff-pdf --view
#   neither / no display / edge cases -> git's standard "Binary files differ" message
#
# Always exits 0: git aborts the whole diff on a non-zero external diff command,
# and diff-pdf returns non-zero whenever pages differ, so we must swallow it.

set -u

path="$1"
old="$2"
new="$5"

have() { command -v "$1" >/dev/null 2>&1; }

has_display() {
    [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]
}

# git passes /dev/null for the missing side of an add or delete.
is_null() { [ "$1" = "/dev/null" ]; }

default_message() {
    if is_null "$old"; then
        echo "PDF added: b/$path (binary, no textual diff)"
    elif is_null "$new"; then
        echo "PDF deleted: a/$path (binary, no textual diff)"
    else
        echo "Binary files a/$path and b/$path differ"
    fi
}

text_diff() {
    if is_null "$old" || is_null "$new" || ! have diff-pdf; then
        default_message
        return 0
    fi
    echo "diff --pdf a/$path b/$path"
    # diff-pdf -v prints "page N has M pixels that differ" + a summary line on stdout.
    # It also tries to init GTK and warns on stderr when no display is present; that
    # warning is irrelevant to the pixel comparison, so drop stderr here.
    diff-pdf -v "$old" "$new" 2>/dev/null || true
}

view_diff() {
    # Cannot open a GUI without a display, or for add/delete (nothing to compare).
    if ! has_display || is_null "$old" || is_null "$new"; then
        text_diff
        return 0
    fi

    local gui
    if have diffpdf; then
        gui=(diffpdf)
        echo "Opened diffpdf for $path"
    elif have diff-pdf; then
        gui=(diff-pdf --view)
        echo "Opened diff-pdf --view for $path"
    else
        text_diff
        return 0
    fi

    # git deletes the temp files it passed (e.g. /tmp/git-blob-XXX/) as soon as
    # this driver returns, but the GUI is detached and reads them asynchronously.
    # Copy both sides to our own temps and let a detached subshell launch the GUI
    # and delete those copies only after it exits.
    local a b
    if ! a=$(mktemp --suffix=.pdf) || ! b=$(mktemp --suffix=.pdf); then
        rm -f "${a:-}" "${b:-}"
        text_diff
        return 0
    fi
    if ! cp -- "$old" "$a" || ! cp -- "$new" "$b"; then
        rm -f "$a" "$b"
        text_diff
        return 0
    fi
    ( setsid "${gui[@]}" "$a" "$b" >/dev/null 2>&1; rm -f "$a" "$b" ) &
}

if [ "${PDF_VIEW:-}" = "1" ]; then
    view_diff
else
    text_diff
fi

exit 0
```

The comment header mirrors the `~/.gitconfig` wiring for reference; the functional `command =` line in `~/.gitconfig` is what actually matters. Git expands `~` in the `command` value, so no absolute path is required.

## The git-lfs interaction

Two non-obvious points make this work with LFS-tracked PDFs:

### Attribute precedence trap

`git lfs track '*.pdf'` writes `*.pdf filter=lfs diff=lfs merge=lfs -text` into the repo's **committed** `.gitattributes`. That in-tree `diff=lfs` **overrides** the global `diff=pdf`, so Git would show the LFS pointer oid instead of a pixel diff. The committed line must therefore drop only the `diff=lfs` token:

```text
*.pdf filter=lfs merge=lfs -text
```

LFS storage is unaffected — only the diff attribute changes. Collaborators are unaffected: they simply do not receive a `diff=lfs` rule.

### Git smudges before diffing

Git runs the LFS smudge filter **itself** before invoking the diff driver, on every side — working tree, staged and committed blobs alike. Both `$2` and `$5` therefore always arrive as real, rasterisable PDFs, never pointers. No manual `git lfs smudge` is needed in the driver.

## Troubleshooting: `git diff` still shows "Binary files differ"

If a repository still reports `Binary files a/file.pdf and b/file.pdf differ`, an in-tree rule is disabling the diff attribute. Check what actually resolves:

```bash
git check-attr -a -- path/to/file.pdf
```

A working setup shows `diff: pdf`. Two failure modes set `diff: unset` instead, and an explicit in-tree rule **always wins** over the global `diff=pdf`:

- `*.pdf diff=lfs` — the [LFS precedence trap](#attribute-precedence-trap) above.
- `*.pdf binary` — very common in LaTeX and paper repositories. `binary` is a built-in Git macro that expands to `-diff -merge -text`; the `-diff` is what disables the driver. `git check-attr -a` reveals this as `binary: set` alongside `diff: unset`.

### Option A: private per-repo override (recommended)

Add the rule to `.git/info/attributes`, which is never committed and invisible to collaborators:

```bash
echo '*.pdf diff=pdf' >> "$(git rev-parse --git-dir)/info/attributes"
```

`git rev-parse --git-dir` resolves the correct location from subdirectories, worktrees and submodules; `>>` appends without clobbering existing entries. Verify:

```bash
git check-attr diff -- path/to/file.pdf   # → diff: pdf
```

`.git/info/attributes` has higher precedence than `core.attributesFile` but lower than committed `.gitattributes` — except that a private `diff=pdf` still overrides a committed `-diff`/`binary`, because a later-read source with an explicit value wins.

### Option B: fix the committed `.gitattributes`

Only if the whole team wants pixel diffs, replace the `binary` macro with `-text` (keeps the file out of textual diffing but lets `diff=pdf` govern):

```text
*.pdf -text
```

This is shared with collaborators and changes their behaviour too.

## Design notes

- **Always exits `0`.** Git aborts the whole diff if an external diff command returns non-zero, and `diff-pdf` exits non-zero whenever pages differ — so the script swallows its exit code.
- **View mode temp-file lifetime.** Git deletes the temp files it passed (`/tmp/git-blob-XXX/`) the instant the driver returns, but the GUI is launched detached and reads them asynchronously. The script copies both sides to its own temps and a detached subshell removes them only after the GUI exits.
- **Headless safety.** Over SSH or otherwise without `$DISPLAY`/`$WAYLAND_DISPLAY`, view mode degrades to the text pixel-count output rather than failing. `diff-pdf`'s spurious GTK init warning on stderr is suppressed in text mode.
- **Env-var trigger.** Git has no real `--view` flag, so view mode is toggled with `PDF_VIEW=1`. This also works with `git show`, `git log -p` and anything else that drives the diff machinery.

## Usage

```bash
# Pixel-change counts
git diff file.pdf

# committed vs committed
git diff HEAD~1 HEAD -- file.pdf

# Visual GUI comparison
PDF_VIEW=1 git diff file.pdf
```

Example text output:

```text
diff --pdf a/file.pdf b/file.pdf
page 0 has 2642 pixels that differ
page 0 differs
1 of 1 pages differ.
```

## Verification

```bash
# Confirm the driver is wired up
git config --global --get core.attributesFile   # → ~/.config/git/attributes
git config --global --get diff.pdf.command       # → ~/.local/bin/git-pdf-diff.sh

# Confirm a tracked PDF resolves to the pdf driver (not lfs)
git check-attr diff filter path/to/file.pdf
# → path/to/file.pdf: diff: pdf
# → path/to/file.pdf: filter: lfs
```

## See Also

- [Git AI Integration with OpenCode](20260624-git-ai-integration-with-opencode.md) — another custom Git tooling integration on this machine
