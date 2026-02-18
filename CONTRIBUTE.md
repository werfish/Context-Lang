# Contributing Guide

## Development toolchain

This project uses **Poetry** for dependency management and local development.

1. Install Poetry (if not already installed).
2. Install project dependencies:

```bash
poetry install
```

3. Activate the virtual environment shell (optional):

```bash
poetry shell
```

Or run commands directly with `poetry run ...`.

## Pre-commit checks

This project uses pre-commit hooks to enforce formatting, linting, and basic security checks.

Install the hooks once after `poetry install`:

```bash
poetry run pre-commit install
```

Run the hooks manually on all files:

```bash
poetry run pre-commit run --all-files
```

## Required checks before opening a PR

Your code should pass all configured pre-commit hooks before you open a pull request.

Current hooks include:
- `ruff` (linting)
- `ruff-format` (formatting)
- `bandit` (security scanning)

If a hook reports issues, fix them and re-run:

```bash
poetry run pre-commit run --all-files
```

## Packaging notes

The project metadata and dependencies are configured in `pyproject.toml` using Poetry.
