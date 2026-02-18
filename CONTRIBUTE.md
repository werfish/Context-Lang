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

## Testing

### Unit tests

Run the unit test suite:

```bash
poetry run pytest
```

Run unit tests with coverage (and show missing lines):

```bash
poetry run pytest --cov=context --cov-report=term-missing
```

### Integration tests

Integration tests live under `test/integration/` and are intended to exercise multi-module flows.

By default, integration tests must run with the **Mock LLM enabled** (i.e. they must not require API keys and must not make network calls).

### LLM integration tests (opt-in)

Real provider/LLM smoke tests live under `test/integration/LLM tests/` and are marked with `@pytest.mark.llm`.

They are **not** run by default because they require network access/credentials and can be flaky/cost money.

To run LLM tests explicitly:

```bash
poetry run pytest -m llm
```

## Packaging notes

The project metadata and dependencies are configured in `pyproject.toml` using Poetry.
