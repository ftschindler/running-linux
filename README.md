# Felix' knowledge-base on running Linux

Welcome to my [personal knowledge base (PKB)](https://en.wikipedia.org/wiki/Personal_knowledge_base) on running Linux in various circumstances.

The underlying knowledge base is realised as a set of markdown files in the [docs/](docs/)
subdirectory, that are converted into a site using [MkDocs](https://www.mkdocs.org/) with
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

See [About](docs/meta/about.md) for details on this site, or [Contributing](CONTRIBUTING.md)
for how to edit.

## building the site locally

See [Local Dev Environment](docs/meta/local_dev_environment.md) for full instructions.

You need `git` and [uv](https://docs.astral.sh/uv/) in your `$PATH`,
and [git lfs](https://github.com/git-lfs/git-lfs/wiki/Tutorial) installed.

1. Clone the repository and bootstrap the environment:

   ```bash
   git clone https://github.com/ftschindler/running-linux.git
   cd running-linux
   make bootstrap
   ```

2. Build and serve the site with

   ```bash
   make serve
   ```

   (or only build the site with `make site`).
