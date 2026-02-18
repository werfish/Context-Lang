from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from context.config import Config
from context.Context import configurationProcess, contextProcess
from context.log import Log, configure_logger


def _reset_config() -> None:
    # Config is a class with global state; keep tests isolated.
    Config.Api_Key = ""
    Config.FilePathProvided = False
    Config.FilePath = ""
    Config.Debug = False
    Config.Log = False
    Config.ParserOnly = False
    Config.MockLLM = False


@pytest.fixture(autouse=True)
def _reset_between_tests() -> None:
    _reset_config()
    if Log.logger is None:
        Log.logger = configure_logger(debug=False, logToFile=False)


def test_configuration_process_allows_mock_llm_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_CONFIG_Open_Router_Api_Key", raising=False)

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=True,
        mock_llm=True,
        filepath=None,
        openrouter_key=None,
        model=Config.Model,
    )

    # Should not raise even when API key is missing.
    configurationProcess(args)
    assert Config.MockLLM is True


def test_configuration_process_requires_api_key_when_not_mock_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_CONFIG_Open_Router_Api_Key", raising=False)

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=True,
        mock_llm=False,
        filepath=None,
        openrouter_key=None,
        model=Config.Model,
    )

    with pytest.raises(ValueError, match="OpenRouter API Key is required"):
        configurationProcess(args)


def test_context_process_parser_only_happy_path_on_single_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_CONFIG_Open_Router_Api_Key", raising=False)

    f = tmp_path / "a.txt"
    f.write_text(
        """
<prompt:A>
Do thing
<prompt:A/>

{A}
""".lstrip(),
        encoding="utf-8",
    )

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=True,
        mock_llm=True,
        filepath=str(f),
        openrouter_key=None,
        model=Config.Model,
    )
    configurationProcess(args)
    Log.logger = configure_logger(debug=False, logToFile=False)

    # Should not raise.
    assert contextProcess() is None


def test_context_process_parser_only_prints_formatted_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Duplicate prompt names should produce parse errors.
    f = tmp_path / "bad.txt"
    f.write_text(
        """
<prompt:A>
first
<prompt:A/>

<prompt:A>
second
<prompt:A/>

{A}
""".lstrip(),
        encoding="utf-8",
    )

    args = SimpleNamespace(
        debug=False,
        log=False,
        parser=True,
        mock_llm=True,
        filepath=str(f),
        openrouter_key=None,
        model=Config.Model,
    )
    configurationProcess(args)
    Log.logger = configure_logger(debug=False, logToFile=False)

    contextProcess()

    out = capsys.readouterr().out
    assert "Total errors in" in out
