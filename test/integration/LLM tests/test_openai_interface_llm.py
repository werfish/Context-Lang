from __future__ import annotations

import json
from pathlib import Path

import pytest
from dotenv import load_dotenv

from context.config import Config
from context.log import Log, configure_logger
from context.openai_interface import generate_code_with_chat

pytestmark = pytest.mark.llm


def _snapshot_config() -> tuple[str, str, bool]:
    return (Config.Api_Key, Config.Model, Config.MockLLM)


def _restore_config(snapshot: tuple[str, str, bool]) -> None:
    Config.Api_Key, Config.Model, Config.MockLLM = snapshot


def _load_env() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env")


def test_generate_code_with_chat_returns_json_with_code_field() -> None:
    snapshot = _snapshot_config()
    try:
        _load_env()

        api_key = Config.Api_Key or __import__("os").getenv("CONTEXT_CONFIG_Open_Router_Api_Key")
        if not api_key:
            pytest.skip("Missing CONTEXT_CONFIG_Open_Router_Api_Key")

        Config.Api_Key = api_key
        Config.MockLLM = False

        if Log.logger is None:
            Log.logger = configure_logger(debug=False, logToFile=False)

        # Keep the prompt short to reduce cost.
        prompt_name = "Hello"
        prompt = "Return a small Python function named add(a,b) that returns a+b. Output code only."

        response = generate_code_with_chat(prompt, prompt_name)

        parsed = json.loads(response)
        assert isinstance(parsed, dict)
        # API contract: always a JSON object with a single 'code' field (string).
        assert set(parsed.keys()) == {"code"}
        assert isinstance(parsed["code"], str)
        assert parsed["code"].strip() != ""
    finally:
        _restore_config(snapshot)


def test_generate_code_with_chat_raises_on_invalid_api_key() -> None:
    """True integration test: exercise real provider auth failure (no mocking)."""

    snapshot = _snapshot_config()
    try:
        _load_env()

        # Ensure we have network credentials configured at all; otherwise skip.
        real_key = Config.Api_Key or __import__("os").getenv("CONTEXT_CONFIG_Open_Router_Api_Key")
        if not real_key:
            pytest.skip("Missing CONTEXT_CONFIG_Open_Router_Api_Key")

        Config.MockLLM = False
        Config.Api_Key = "sk-invalid"  # deliberately invalid

        if Log.logger is None:
            Log.logger = configure_logger(debug=False, logToFile=False)

        prompt_name = "InvalidKey"
        prompt = "Reply with exactly: OK"

        with pytest.raises(Exception):  # noqa: B017 (integration test: provider-specific exception)
            generate_code_with_chat(prompt, prompt_name)
    finally:
        _restore_config(snapshot)
