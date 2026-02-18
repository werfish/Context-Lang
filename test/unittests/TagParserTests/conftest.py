"""Shared fixtures/helpers for TagParser unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from context.log import Log, configure_logger

FIXTURES_DIR = Path(__file__).parent / "TagParsingTestFiles"


@pytest.fixture(autouse=True)
def _configure_test_logger() -> None:
    # tag_parser calls Log.logger.*; ensure it's always available in tests.
    if Log.logger is None:
        Log.logger = configure_logger(debug=False, logToFile=False)


def read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def write_file(tmp_path: Path, rel: str, content: str) -> Path:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
