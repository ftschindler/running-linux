# Felix' knowledge-base on running Linux

This repository contains my personal notes on running Linux in various circumstances.

The underlying knowledge base is realised as a set of markdown files in the [content/](content/)
subdirectory, that are converted into a site using [Quartz 4](https://quartz.jzhao.xyz/)
(or rather [this fork](https://github.com/ftschindler/quartz)).

## contributing

Add markdown files to [content/](https://github.com/ftschindler/running-linux/tree/main/content) and create a pull request.

## building the site locally

You need `git`, `npm` and `npx` in your `$PATH`,
and [git lfs](https://github.com/git-lfs/git-lfs/wiki/Tutorial) installed.

1. Clone the repository and bootstrap the environment:

   ```bash
   git clone https://github.com/ftschindler/running-linux.git
   cd running-linux
   # git checkout <existing_branch>  # optional
   make bootstrap
   ```

2. Build and serve the site with

   ```bash
   make serve
   ```

   (or only build the site with `make build`).
