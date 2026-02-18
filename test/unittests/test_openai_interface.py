"""Unit tests for context.openai_interface.

These are *unit* tests: they do not hit the network.
They validate the wrapper contract and branching behavior.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from context.config import Config
from context.openai_interface import generate_code_with_chat


class _DummyLogger:
    def debug(self, *args: Any, **kwargs: Any) -> None:
        return None

    def error(self, *args: Any, **kwargs: Any) -> None:
        return None


def _ensure_logger(monkeypatch: pytest.MonkeyPatch) -> None:
    # openai_interface assumes Log.logger is initialized.
    monkeypatch.setattr("context.openai_interface.Log.logger", _DummyLogger(), raising=False)


def _snapshot_config() -> tuple[str, str, bool]:
    return (Config.Api_Key, Config.Model, Config.MockLLM)


def _restore_config(snapshot: tuple[str, str, bool]) -> None:
    Config.Api_Key, Config.Model, Config.MockLLM = snapshot


def test_generate_code_with_chat_mock_llm_does_not_call_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _snapshot_config()
    try:
        Config.MockLLM = True
        _ensure_logger(monkeypatch)

        def _boom(*args: Any, **kwargs: Any) -> str:  # pragma: no cover
            raise AssertionError("run_generation_graph should not be called when MockLLM=True")

        # Patch where it is imported/used.
        monkeypatch.setattr("context.openai_interface.run_generation_graph", _boom)

        out = generate_code_with_chat(prompt="hi", prompt_name="P")
        parsed = json.loads(out)
        assert parsed == {"code": "MOCK_LLM_RESPONSE(P)"}
    finally:
        _restore_config(snapshot)


def test_generate_code_with_chat_wraps_graph_response_in_json(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _snapshot_config()
    try:
        Config.MockLLM = False
        _ensure_logger(monkeypatch)

        monkeypatch.setattr(
            "context.openai_interface.run_generation_graph",
            lambda prompt, prompt_name: "SOME_CODE",
        )

        out = generate_code_with_chat(prompt="anything", prompt_name="Hello")
        parsed = json.loads(out)
        assert set(parsed.keys()) == {"code"}
        assert parsed["code"] == "SOME_CODE"
    finally:
        _restore_config(snapshot)


def test_generate_code_with_chat_reraises_graph_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _snapshot_config()
    try:
        Config.MockLLM = False
        _ensure_logger(monkeypatch)

        def _raise(prompt: str, prompt_name: str) -> str:
            raise RuntimeError("boom")

        monkeypatch.setattr("context.openai_interface.run_generation_graph", _raise)

        with pytest.raises(RuntimeError, match="boom"):
            generate_code_with_chat(prompt="x", prompt_name="Y")
    finally:
        _restore_config(snapshot)
