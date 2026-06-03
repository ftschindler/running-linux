.PHONY: help bootstrap site serve

## Show available targets
help:
	@grep -B1 '^[a-z]' $(MAKEFILE_LIST) | grep '^##' | sed 's/## /  /'

## Install dependencies and pre-commit hooks
bootstrap:
	uv sync
	uv run prek install

## Build the static site into site/
site:
	NO_MKDOCS_2_WARNING=true uv run mkdocs build --strict

## Start the live-reloading dev server
serve:
	NO_MKDOCS_2_WARNING=true uv run mkdocs serve
