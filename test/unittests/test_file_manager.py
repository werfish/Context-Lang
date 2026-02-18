"""Unit tests for file discovery and ignore behavior.

Coverage for context.file_manager.get_file_paths(...):
- Recursively collects file paths under a directory.
- Respects .gitignore rules (ignored files/dirs should not appear in output), including negation rules.
- Respects the built-in ignore_list (e.g., Context_Logs directory), including nested occurrences.
- Documents edge-case behavior (ordering is unspecified; .gitignore may be included; behavior on missing paths).

These tests validate get_file_paths(...) returns the expected set of files for a synthetic
(tmp_path) directory tree.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from context.file_manager import get_file_paths


def _touch(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_get_file_paths_recursively_collects_files(tmp_path: Path) -> None:
    _touch(tmp_path / "a.txt")
    _touch(tmp_path / "src" / "b.py")
    _touch(tmp_path / "src" / "nested" / "c.md")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    assert got == {
        (tmp_path / "a.txt").resolve(),
        (tmp_path / "src" / "b.py").resolve(),
        (tmp_path / "src" / "nested" / "c.md").resolve(),
    }


def test_get_file_paths_ignores_context_logs_directory(tmp_path: Path) -> None:
    _touch(tmp_path / "keep.txt")
    _touch(tmp_path / "Context_Logs" / "ignored.log")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    assert (tmp_path / "keep.txt").resolve() in got
    assert (tmp_path / "Context_Logs" / "ignored.log").resolve() not in got


def test_get_file_paths_respects_gitignore_for_files_and_directories(tmp_path: Path) -> None:
    # Ignore a directory and a file pattern.
    (tmp_path / ".gitignore").write_text(
        "ignored_dir/\n*.secret\n",
        encoding="utf-8",
    )

    _touch(tmp_path / "keep.py")
    _touch(tmp_path / "ignored_dir" / "nope.py")
    _touch(tmp_path / "top.secret")
    _touch(tmp_path / "nested" / "also.secret")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    assert (tmp_path / "keep.py").resolve() in got
    assert (tmp_path / "ignored_dir" / "nope.py").resolve() not in got
    assert (tmp_path / "top.secret").resolve() not in got
    assert (tmp_path / "nested" / "also.secret").resolve() not in got


def test_get_file_paths_respects_gitignore_negation_rules(tmp_path: Path) -> None:
    # Ignore all *.log, but explicitly re-include keep.log
    (tmp_path / ".gitignore").write_text(
        "*.log\n!keep.log\n",
        encoding="utf-8",
    )

    _touch(tmp_path / "a.log")
    _touch(tmp_path / "keep.log")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    assert (tmp_path / "a.log").resolve() not in got
    assert (tmp_path / "keep.log").resolve() in got


def test_get_file_paths_gitignore_directory_pattern_matches_nested(tmp_path: Path) -> None:
    # Ensure patterns like "subdir/ignored.txt" work even though get_file_paths passes absolute paths.
    (tmp_path / ".gitignore").write_text(
        "subdir/ignored.txt\n",
        encoding="utf-8",
    )

    _touch(tmp_path / "subdir" / "ignored.txt")
    _touch(tmp_path / "subdir" / "keep.txt")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    assert (tmp_path / "subdir" / "ignored.txt").resolve() not in got
    assert (tmp_path / "subdir" / "keep.txt").resolve() in got


def test_get_file_paths_includes_gitignore_file_current_behavior(tmp_path: Path) -> None:
    # Current behavior: .gitignore itself is returned as a discovered file.
    (tmp_path / ".gitignore").write_text("*.ignoreme\n", encoding="utf-8")
    _touch(tmp_path / "keep.txt")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    assert (tmp_path / ".gitignore").resolve() in got
    assert (tmp_path / "keep.txt").resolve() in got


def test_get_file_paths_ignores_context_logs_directory_when_nested(tmp_path: Path) -> None:
    _touch(tmp_path / "a" / "Context_Logs" / "nested.log")
    _touch(tmp_path / "a" / "keep.txt")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    assert (tmp_path / "a" / "keep.txt").resolve() in got
    assert (tmp_path / "a" / "Context_Logs" / "nested.log").resolve() not in got


def test_get_file_paths_order_is_not_part_of_contract(tmp_path: Path) -> None:
    _touch(tmp_path / "b.txt")
    _touch(tmp_path / "a.txt")

    result = get_file_paths(str(tmp_path))

    assert isinstance(result, list)
    assert {Path(p).resolve() for p in result} == {(tmp_path / "a.txt").resolve(), (tmp_path / "b.txt").resolve()}


def test_get_file_paths_returns_empty_list_for_missing_directory(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"

    assert get_file_paths(str(missing)) == []


def test_get_file_paths_returns_empty_list_when_given_a_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "single.txt"
    _touch(file_path)

    assert get_file_paths(str(file_path)) == []


def test_get_file_paths_permission_error_propagates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Simulate an unreadable directory by forcing os.walk to raise.
    def _raise(*_args, **_kwargs):
        raise PermissionError("nope")

    monkeypatch.setattr(os, "walk", _raise)

    with pytest.raises(PermissionError):
        get_file_paths(str(tmp_path))


def test_get_file_paths_traverses_windows_junction_without_crashing(tmp_path: Path) -> None:
    # Best-effort Windows-only test: create a junction and ensure traversal doesn't crash.
    # If junction creation isn't available, skip.
    if sys.platform != "win32":
        pytest.skip("Windows junction behavior is Windows-only")

    target = tmp_path / "target_dir"
    target.mkdir()
    _touch(target / "t.txt")

    link = tmp_path / "link_dir"

    try:
        # mklink /J <link> <target>
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception as e:
        pytest.skip(f"Could not create junction (mklink /J): {e}")

    got = {Path(p).resolve() for p in get_file_paths(str(tmp_path))}

    # We should at least see the file under the junction path.
    assert (link / "t.txt").resolve() in got
