---
title: Converting Markdown to PDF for Printing
---

Findings from evaluating ways to convert this PKB's markdown notes into nicely printed PDFs on Manjaro. The chosen route (Pandoc + XeLaTeX) has a reusable defaults file and a thin `md-to-pdf` wrapper script so any single note can be turned into an A4 PDF with one command.

## Tech Stack: Pandoc + XeLaTeX

Pandoc converts markdown to LaTeX, and XeLaTeX renders it to PDF. XeLaTeX was preferred over the lighter Tectonic engine specifically because it can select fonts already installed on the system (via `fontspec`), giving control over body, sans and monospace typefaces without shipping LaTeX font packages.

### Installed Packages

```bash
sudo pacman -S --needed pandoc-cli texlive-latex \
  texlive-latexrecommended texlive-latexextra \
  texlive-fontsrecommended texlive-xetex
```

Notes from the install:

- The pandoc package is **`pandoc-cli`**, not `pandoc`.
- `texlive-xetex` is **required and easy to miss** — without it, XeLaTeX errors with `I can't find the format file 'xelatex.fmt'!` even though the `xelatex` binary exists. Installing the package triggers the `texlive` post-transaction hook that builds the format file.

### Configuration

Pandoc supports _defaults files_ — reusable YAML that bundles engine, layout and typography settings so they need not be repeated on the command line. The active file lives at:

```text
~/.local/share/pandoc/defaults/md_to_pdf.yaml
```

Current `md_to_pdf.yaml`:

```yaml
pdf-engine: xelatex

from: markdown
standalone: true
toc: true
toc-depth: 3
number-sections: false
highlight-style: tango

variables:
  documentclass: article
  papersize: a4
  geometry:
    - margin=2.2cm
  fontsize: 11pt
  linestretch: 1.15
  colorlinks: true
  linkcolor: RoyalBlue
  urlcolor: RoyalBlue
  mainfont: "Noto Serif"
  sansfont: "Noto Sans"
  monofont: "DejaVu Sans Mono"
  monofontoptions:
    - Scale=0.85

wrap: auto
```

Everything here is tunable:

- **Fonts:** `mainfont` / `sansfont` / `monofont` accept any family listed by `fc-list`. The fonts above were verified present on this install. `monofontoptions: Scale=0.85` shrinks code so long lines and URLs fit the text width.
- **Page:** `papersize`, `geometry` (margins), `fontsize`, `linestretch`.
- **Structure:** `toc`, `toc-depth`, `number-sections`.
- **Code highlighting:** `highlight-style` (e.g. `tango`, `kate`, `pygments`, `zenburn`).
- **Links:** `colorlinks` with `linkcolor` / `urlcolor`.

### Wrapper Script

A small wrapper at `~/.local/bin/md-to-pdf` (on `$PATH`) is the day-to-day interface. It takes the input note and an optional output name, validates the toolchain and defaults file up front, runs pandoc, and prints only `Wrote <file>.pdf` on success.

```bash
#!/usr/bin/env bash
set -euo pipefail

DEFAULTS_FILE="${HOME}/.local/share/pandoc/defaults/md_to_pdf.yaml"

die() {
 printf 'md-to-pdf: %s\n' "$1" >&2
 exit 1
}

usage() {
 printf 'Usage: md-to-pdf INPUT.md [OUTPUT.pdf] [-- PANDOC_ARGS...]\n' >&2
 exit 2
}

positional=()
passthrough=()
while [ "$#" -gt 0 ]; do
 if [ "$1" = "--" ]; then
  shift
  passthrough=("$@")
  break
 fi
 positional+=("$1")
 shift
done

[ "${#positional[@]}" -ge 1 ] && [ "${#positional[@]}" -le 2 ] || usage

input="${positional[0]}"
[ -f "$input" ] || die "input file not found: ${input}"

if [ "${#positional[@]}" -eq 2 ]; then
 output="${positional[1]}"
else
 output="${input%.*}.pdf"
fi

command -v pandoc >/dev/null 2>&1 || die "pandoc not found on PATH (install: pacman -S pandoc-cli)"
command -v xelatex >/dev/null 2>&1 || die "xelatex not found on PATH (install: pacman -S texlive-xetex)"
[ -f "$DEFAULTS_FILE" ] || die "pandoc defaults file missing: ${DEFAULTS_FILE}"

pandoc "$input" -d "$DEFAULTS_FILE" -o "$output" ${passthrough[@]+"${passthrough[@]}"}

printf 'Wrote %s\n' "$output"
```

Behaviour:

- **Output name is optional.** `md-to-pdf note.md` writes `note.pdf` alongside the input (derived by swapping the extension); `md-to-pdf note.md /tmp/out.pdf` writes to the given path.
- **Passthrough after `--`.** Anything following a `--` separator is forwarded verbatim to pandoc, appended after the wrapper's own flags (so a user flag wins on conflict). This exposes pandoc's full option set without the wrapper needing to know about each flag.
- **Preflight checks** fail fast with a clear message if `pandoc`, `xelatex` or the defaults file is missing, each pointing at the fix.
- **Quiet on success** — a single `Wrote <path>` line, nothing else.
- **Exit codes:** `0` success, `1` a missing file/tool, `2` wrong argument count (usage).

The `${passthrough[@]+"${passthrough[@]}"}` expansion is the safe way to expand a possibly-empty array under `set -u`; a plain `"${passthrough[@]}"` errors on an empty array in older bash.

### Usage

```bash
# Deduced output name (writes note.pdf next to the input)
md-to-pdf docs/done/20260711-ssh-key-unlocking-plasma.md

# Explicit output path
md-to-pdf note.md /tmp/note.pdf

# Override a defaults setting for one run, via passthrough
md-to-pdf note.md -- --toc=false

# Explicit output plus passthrough
md-to-pdf note.md /tmp/note.pdf -- -V mainfont="TeX Gyre Termes"
```

Note the override syntax: `toc` is a **top-level setting** in the defaults file, so it is switched off with the `--toc=false` flag, **not** `-V toc=false`. The `-V key=value` form sets template _variables_ (e.g. `mainfont`, `fontsize`, `geometry`), which is a different namespace — using `-V` on a top-level setting silently does nothing.

To bypass the wrapper entirely and drive pandoc directly:

```bash
pandoc note.md -d md_to_pdf -o note.pdf --toc=false
```

Per-document overrides are also possible via YAML frontmatter in the note itself.

## Trade-offs and Gotchas

- **Long unbreakable strings** (very long URLs inside code blocks) can still overflow the right margin — a LaTeX limitation, not a config fault. The `Scale=0.85` monospace setting mitigates it; manual line breaks fix the rest.
- **First run is slow.** The initial XeLaTeX invocation builds format files and caches; subsequent conversions are fast.

## Other Options Considered

All packages below are in the official Arch/Manjaro repositories unless noted.

| Option | Install | Print quality | Configurability | Notes |
| --- | --- | --- | --- | --- |
| **Pandoc + LaTeX** | `pandoc-cli` + `texlive-*` (~1-2 GB) | Excellent | Excellent | Gold standard typography; heaviest install |
| **Pandoc + Tectonic** | `pandoc-cli` + `tectonic` (~200 MB) | Excellent | Excellent | Same output, self-contained LaTeX engine that fetches packages on demand; no system-font selection |
| **Pandoc + XeLaTeX** | `pandoc-cli` + `texlive-latex*` + `texlive-xetex` | Excellent | Excellent | **Chosen** — LaTeX quality _plus_ system fonts via `fontspec` |
| **Typst** | `typst` (~30 MB) | Very good | Good | Modern, fast, tiny; younger ecosystem; pair with pandoc via `--pdf-engine=typst` |
| **WeasyPrint** | `python-weasyprint` (~100 MB) | Very good | Good (CSS `@page`) | MD→HTML→PDF; style with plain CSS; two-step pipeline |
| **md-to-pdf / Chromium** | `npm i -g md-to-pdf` (Chromium already present) | Good | Moderate | Zero-effort; Chromium's print engine less precise on page breaks |

## References

- [Pandoc Manual: Creating a PDF](https://pandoc.org/MANUAL.html#creating-a-pdf)
- [Pandoc Manual: Defaults files](https://pandoc.org/MANUAL.html#defaults-files)
- [Arch Wiki: TeX Live](https://wiki.archlinux.org/title/TeX_Live)
