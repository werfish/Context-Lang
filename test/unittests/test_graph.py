"""Unit tests for context.graph.

These tests mock the LangChain ChatOpenAI client. They verify:
- client configuration (api_key/model/base_url)
- message construction (SystemMessage + HumanMessage; prompt_name substitution)
- response normalization (AIMessage vs non-AIMessage)

They do not test the langgraph wiring (graph shape), by design.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from context.config import Config
from context.graph import PROMPTS, _call_openrouter


def _snapshot_config() -> tuple[str, str]:
    return (Config.Api_Key, Config.Model)


def _restore_config(snapshot: tuple[str, str]) -> None:
    Config.Api_Key, Config.Model = snapshot


@dataclass
class _FakeChatOpenAI:
    """A minimal stand-in for langchain_openai.ChatOpenAI."""

    api_key: str
    model: str
    base_url: str

    # captured from invoke
    last_messages: list[Any] | None = None
    response_to_return: Any = field(default_factory=lambda: AIMessage(content="OK"))

    def invoke(self, messages: list[Any]) -> Any:
        self.last_messages = messages
        return self.response_to_return


def test_call_openrouter_constructs_messages_and_configures_client(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _snapshot_config()
    try:
        Config.Api_Key = "KEY"
        Config.Model = "openai/gpt-5.2"

        created: dict[str, Any] = {}

        def _factory(**kwargs: Any) -> _FakeChatOpenAI:
            created["kwargs"] = kwargs
            inst = _FakeChatOpenAI(**kwargs)
            created["inst"] = inst
            return inst

        monkeypatch.setattr("context.graph.ChatOpenAI", _factory)

        state = {"prompt": "Do thing", "prompt_name": "TagX", "response": ""}
        out_state = _call_openrouter(state)

        # client config
        assert created["kwargs"] == {
            "api_key": "KEY",
            "model": "openai/gpt-5.2",
            "base_url": "https://openrouter.ai/api/v1",
        }

        inst: _FakeChatOpenAI = created["inst"]
        assert inst.last_messages is not None
        assert len(inst.last_messages) == 2

        sys_msg, human_msg = inst.last_messages
        assert isinstance(sys_msg, SystemMessage)
        assert isinstance(human_msg, HumanMessage)

        expected_sys = PROMPTS["System"].replace("<<<TAGNAME>>>", "TagX")
        assert sys_msg.content == expected_sys
        assert human_msg.content == "Do thing"

        assert out_state["response"] == "OK"
    finally:
        _restore_config(snapshot)


def test_call_openrouter_normalizes_non_aimessage_response(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _snapshot_config()
    try:
        Config.Api_Key = "KEY"
        Config.Model = "openai/gpt-5.2"

        class _WeirdResponse:
            def __str__(self) -> str:
                return "WEIRD"

        def _factory(**kwargs: Any) -> _FakeChatOpenAI:
            inst = _FakeChatOpenAI(**kwargs)
            inst.response_to_return = _WeirdResponse()
            return inst

        monkeypatch.setattr("context.graph.ChatOpenAI", _factory)

        state = {"prompt": "x", "prompt_name": "T", "response": ""}
        out_state = _call_openrouter(state)

        assert out_state["response"] == "WEIRD"
    finally:
        _restore_config(snapshot)
