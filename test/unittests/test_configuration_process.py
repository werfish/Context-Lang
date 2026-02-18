"""Unit tests for CLI configuration processing.

Happy-path coverage for Context.configurationProcess(...):
- Reads configuration from CLI args (debug/log/parser flags, model, filepath).
- Reads OpenRouter API key from an explicit CLI arg.
- Falls back to environment variable when CLI arg is not provided.

Notes
- These tests validate that configurationProcess(...) correctly populates the Config singleton
  in src/context/config.py.
- This module includes both happy-path and selected edge-case tests because
  configurationProcess(...) mutates global singleton state.
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


def test_configuration_process_raises_when_no_api_key_in_args_or_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_CONFIG_Open_Router_Api_Key", raising=False)

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=False,
        filepath=None,
        openrouter_key=None,
        model="openai/gpt-5.2",
    )

    with pytest.raises(ValueError, match="OpenRouter API Key is required"):
        configurationProcess(args)


def test_configuration_process_cli_key_wins_over_env_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_CONFIG_Open_Router_Api_Key", "env-key")

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=False,
        filepath=None,
        openrouter_key="cli-key",
        model="openai/gpt-5.2",
    )

    configurationProcess(args)

    assert Config.Api_Key == "cli-key"


def test_configuration_process_env_key_empty_string_is_accepted_current_behavior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Current behavior: only `None` triggers the error; an empty string is accepted.
    monkeypatch.setenv("CONTEXT_CONFIG_Open_Router_Api_Key", "")

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=False,
        filepath=None,
        openrouter_key=None,
        model="openai/gpt-5.2",
    )

    configurationProcess(args)

    assert Config.Api_Key == ""


def test_configuration_process_accepts_unvalidated_model_value_when_called_directly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # entryArguments() enforces choices via argparse, but configurationProcess() itself
    # does no validation.
    monkeypatch.setenv("CONTEXT_CONFIG_Open_Router_Api_Key", "env-key")

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=False,
        filepath=None,
        openrouter_key=None,
        model="some/unknown-model",
    )

    configurationProcess(args)

    assert Config.Model == "some/unknown-model"


def test_configuration_process_filepath_empty_string_sets_provided_true_current_behavior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CONTEXT_CONFIG_Open_Router_Api_Key", "env-key")

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=False,
        filepath="",
        openrouter_key=None,
        model="openai/gpt-5.2",
    )

    configurationProcess(args)

    assert Config.FilePathProvided is True
    assert Config.FilePath == ""


def test_configuration_process_overwrites_previous_config_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_CONFIG_Open_Router_Api_Key", "env-key")

    args1 = SimpleNamespace(
        debug=True,
        log=True,
        parser=True,
        filepath="a.py",
        openrouter_key=None,
        model="openai/gpt-5.2",
    )
    configurationProcess(args1)
    assert Config.Debug is True
    assert Config.FilePathProvided is True

    args2 = SimpleNamespace(
        debug=False,
        log=False,
        parser=False,
        filepath=None,
        openrouter_key="cli-key",
        model="openai/gpt-5.2",
    )
    configurationProcess(args2)

    assert Config.Debug is False
    assert Config.Log is False
    assert Config.ParserOnly is False
    assert Config.Api_Key == "cli-key"

    # Current behavior: configurationProcess(...) does not reset FilePathProvided/FilePath
    # when filepath=None, so prior state leaks.
    assert Config.FilePathProvided is True
    assert Config.FilePath == "a.py"
