---
title: Editing on GitHub
---

You can contribute to this site directly from your browser — no local tooling required.

## Edit an existing page

Every page on the site has an **edit** icon (pencil) in the top right. Clicking it opens the
source file in the GitHub web editor, where you can make changes and submit a pull request in
one step.

You can also press ++period++ on any repository page on GitHub to open the full
[github.dev](https://github.dev) editor (VS Code in the browser) for multi-file edits.

## Create a new page

1. Navigate to the target folder in the
   [repository](https://github.com/ftschindler/running-linux) on GitHub.
2. Click **Add file > Create new file**.
3. Name the file with a `.md` extension (lowercase, no spaces — see
   [Editing Conventions](editing_conventions.md#file-naming)).
4. Write your content following the [Editing Conventions](editing_conventions.md).
5. Commit and open a pull request.

## Limitations

- **No local preview** — you cannot run `mkdocs serve` in the browser. Use the
  [local dev environment](local_dev_environment.md) if you need to preview before pushing.
- **No pre-commit hooks** — the automatic linters and link checks only run locally. CI will
  catch issues on push, but feedback is slower.
- **Excalidraw diagrams** cannot be created in the GitHub editor. Create them on
  [excalidraw.com](https://excalidraw.com) and upload the `.excalidraw` file.
