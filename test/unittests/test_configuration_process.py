"""Unit tests for CLI configuration processing.

Happy-path coverage for Context.configurationProcess(...):
- Reads configuration from CLI args (debug/log/parser flags, model, filepath).
- Reads OpenRouter API key from an explicit CLI arg.
- Falls back to environment variable when CLI arg is not provided.

Notes
- These tests validate that configurationProcess(...) correctly populates the Config singleton
  in src/context/config.py.
- Error-path tests (missing API key) are intentionally out of scope here.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from context.config import Config
from context.Context import configurationProcess


@pytest.fixture(autouse=True)
def _reset_config() -> None:
    # Reset to known defaults so tests don't leak state across each other.
    Config.Api_Key = ""
    Config.FilePathProvided = False
    Config.FilePath = ""
    Config.Debug = False
    Config.Log = False
    Config.ParserOnly = False
    Config.Model = "openai/gpt-5.2"


def test_configuration_process_reads_cli_args_and_sets_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_CONFIG_Open_Router_Api_Key", raising=False)

    args = SimpleNamespace(
        debug=True,
        log=True,
        parser=True,
        filepath="./some/path.py",
        openrouter_key="test-key",
        model="openai/gpt-5.2",
    )

    configurationProcess(args)

    assert Config.Debug is True
    assert Config.Log is True
    assert Config.ParserOnly is True

    assert Config.Api_Key == "test-key"
    assert Config.Model == "openai/gpt-5.2"

    assert Config.FilePathProvided is True
    assert Config.FilePath == "./some/path.py"


def test_configuration_process_falls_back_to_env_key_when_cli_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_CONFIG_Open_Router_Api_Key", "env-key")

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=False,
        filepath=None,
        openrouter_key=None,
        model="openai/gpt-5.2",
    )

    configurationProcess(args)

    assert Config.Api_Key == "env-key"
    assert Config.FilePathProvided is False
    assert Config.FilePath == ""
