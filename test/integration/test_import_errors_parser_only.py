from __future__ import annotations

import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from context.config import Config
from context.Context import configurationProcess, contextProcess
from context.log import Log, configure_logger


def _append_line_if_missing(path: Path, line: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if line in existing.splitlines():
        return

    prefix = ""
    if existing and not existing.endswith("\n"):
        prefix = "\n"

    path.write_text(existing + prefix + line + "\n", encoding="utf-8")


def _remove_lines(path: Path, lines_to_remove: list[str]) -> None:
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if line not in set(lines_to_remove)]
    path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")


def test_import_errors_parser_only_flow_mimics_bat_script(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Integration test (python API) mirroring test/E2E/import_errors_test/run_test.bat.

    We run parser-only mode in a temp copy of the fixture project, while temporarily adding ignore rules
    for IgnoredFiles/ into .gitignore.

    This test does NOT use the real LLM. It uses MockLLM (though parser-only does not call the LLM).
    """

    fixture_dir = Path(__file__).parent / "import_errors_test"
    proj_dir = tmp_path / "import_errors_test"
    shutil.copytree(fixture_dir, proj_dir, dirs_exist_ok=True)

    gitignore_path = proj_dir / ".gitignore"

    add_lines = ["#Ignore the test ignore folder", "**/IgnoredFiles/"]

    old_cwd = os.getcwd()
    try:
        os.chdir(proj_dir)

        # Step 1: Add ignore lines if missing
        _append_line_if_missing(gitignore_path, add_lines[0])
        _append_line_if_missing(gitignore_path, add_lines[1])

        # Step 2: Run Context in parser-only mode (via python API)
        args = SimpleNamespace(
            debug=True,
            log=True,
            parser=True,
            mock_llm=True,
            filepath=None,
            openrouter_key=None,
            model=Config.Model,
        )
        configurationProcess(args)
        Log.logger = configure_logger(debug=True, logToFile=True)

        contextProcess()

        out = capsys.readouterr().out
        # We expect the parser-only run to print a formatted error summary for at least one file.
        assert "Total errors in" in out

    finally:
        # Step 3: Remove our injected .gitignore lines
        _remove_lines(gitignore_path, add_lines)
        os.chdir(old_cwd)
