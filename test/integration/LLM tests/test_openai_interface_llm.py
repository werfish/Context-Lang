from __future__ import annotations

import json
from pathlib import Path

import pytest
from dotenv import load_dotenv

from context.config import Config
from context.log import Log, configure_logger
from context.openai_interface import generate_code_with_chat

pytestmark = pytest.mark.llm


def _load_env() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env")


def test_generate_code_with_chat_returns_json_with_code_field() -> None:
    _load_env()

    api_key = Config.Api_Key or __import__("os").getenv("CONTEXT_CONFIG_Open_Router_Api_Key")
    if not api_key:
        pytest.skip("Missing CONTEXT_CONFIG_Open_Router_Api_Key")

    Config.Api_Key = api_key
    if Log.logger is None:
        Log.logger = configure_logger(debug=False, logToFile=False)

    # Keep the prompt short to reduce cost.
    prompt_name = "Hello"
    prompt = "Return a small Python function named add(a,b) that returns a+b. Output code only."

    response = generate_code_with_chat(prompt, prompt_name)

    parsed = json.loads(response)
    assert isinstance(parsed, dict)
    assert "code" in parsed
    assert isinstance(parsed["code"], str)
    assert parsed["code"].strip() != ""
