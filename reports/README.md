# Reports

This folder contains **quality measurement reports** for Context‑Lang.

Context‑Lang is an AI-assisted project and the code may be **100% written by AI** (or heavily AI-generated).
Because of that, we track a small set of code-quality signals to help keep the codebase readable, safe, and maintainable.

## What we track (measurement, not enforcement)

The tools below are currently used in **report-only** mode. The goal is to *measure and observe* trends.
Thresholds / enforcement can be added later.

## Reporting process (TBD)


## Quality tools & metrics

### 1) pytest + pytest-cov

**Purpose:** unit tests + unit test coverage.

**Metrics provided:**
- Test pass/fail status
- Coverage % (statement coverage)
- Missing lines report (per file)

Example:
- `poetry run pytest --cov=context --cov-report=term-missing`

### 2) Radon

**Purpose:** code complexity and maintainability measurements.

**Metrics provided:**
- Cyclomatic complexity (CC) per function/method and average grade (A–F)
- Maintainability Index (MI) per module (letter grade + numeric score)

Examples:
- `poetry run radon cc -s -a src/`
- `poetry run radon mi -s src/`

### 3) Ruff

**Purpose:** linting and style checks.

**Metrics provided (when run in reporting mode):**
- Complexity findings via McCabe complexity warnings (rule group `C90*`, e.g. `C901`)
- Counts/list of violations by rule

Example (report-only):
- `poetry run ruff check src --select C90 --exit-zero`

### 4) jscpd

**Purpose:** code duplication detection.

**Metrics provided:**
- Number of clones found
- Duplicated lines (absolute + %)
- Duplicated tokens (absolute + %)
- Files analyzed

Example:
- `npx jscpd -f python -r console src`

### 5) Dependency / coupling (TBD)

**Purpose:** measure coupling between modules/packages.

**Planned metrics:**
- Import graph / dependency edges
- Cycles (if any)
- Potential layering violations (if/when we define layers)

Candidate tools:
- `grimp` (import graph analysis)
- `import-linter` (architecture contracts; can be run in report-only mode)

---

If you add a new tool or metric, document it here and (optionally) store generated outputs in this folder.
