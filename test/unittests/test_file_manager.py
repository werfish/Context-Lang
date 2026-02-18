"""Unit tests for file discovery and ignore behavior.

Happy-path coverage for context.file_manager.get_file_paths(...):
- Recursively collects file paths under a directory.
- Respects .gitignore rules (ignored files/dirs should not appear in output).
- Respects the built-in ignore_list (e.g., Context_Logs directory).

These tests validate get_file_paths(...) returns the expected set of files for a synthetic
(tmp_path) directory tree.
"""

from __future__ import annotations

from pathlib import Path

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
