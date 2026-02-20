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

## Quality metrics (measurement only)

These commands are for **measuring** code quality signals locally/CI.
They are intentionally **not wired as failing checks** (no enforcement) — treat them as reporting.

### 1) Unit test coverage

```bash
poetry run pytest --cov=context --cov-report=term-missing
```

### 2) Cyclomatic complexity

Using **Radon** (added as a Poetry dev dependency):

```bash
poetry run radon cc -s -a src/
```

Note: Radon may exit with a non-zero code depending on what it finds / how your shell treats warnings.
For *measurement-only*, you can ignore the exit code.

Machine-readable (JSON) output:

```bash
poetry run radon cc -j src/ > radon-cc.json
```

### 3) Cohesion / maintainability signal

Radon does not compute a perfect, universal “cohesion score” for Python, but it provides a practical
**Maintainability Index (MI)** signal (a proxy many teams use alongside complexity/coupling).

```bash
poetry run radon mi -s src/
```

Machine-readable (JSON) output:

```bash
poetry run radon mi -j src/ > radon-mi.json
```

### 4) Coupling / dependencies (import graph)

For dependency/coupling visibility, generate an import graph with **pydeps**:

```bash
# one-time install (not managed by Poetry in this repo yet)
python -m pip install pydeps

# generate a dependency graph (SVG/PNG depending on your setup)
pydeps context --max-bacon=2
```

If you want a stricter “architecture contract” tool later, we can add `import-linter`, but that tends to
be used for *enforcing* rules (even if you can run it in report-only mode).

### 5) Duplication (copy/paste)

Use **jscpd** (language-agnostic copy/paste detector):

```bash
# one-time install (choose one)
# npm i -g jscpd
# or (recommended) in the repo:
# npm i -D jscpd

# run (local install):
npx jscpd --languages python --path src --reporters console
```

Machine-readable (JSON) output:

```bash
npx jscpd --languages python --path src --reporters json --output .jscpd-report
```

### Optional: Ruff “complexity” findings (report-only)

Ruff can report McCabe complexity findings (`C901`). To avoid enforcement, run with `--exit-zero`:

```bash
poetry run ruff check src --select C90 --exit-zero
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
