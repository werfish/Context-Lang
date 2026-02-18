from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import load_dotenv

from context.config import Config
from context.graph import run_generation_graph

pytestmark = pytest.mark.llm


def _load_env() -> None:
    # Ensure local .env is loaded for LLM tests.
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env")


def test_run_generation_graph_openrouter_smoke() -> None:
    _load_env()

    api_key = Config.Api_Key or (  # may already be set by other tests
        __import__("os").getenv("CONTEXT_CONFIG_Open_Router_Api_Key")
    )
    if not api_key:
        pytest.skip("Missing CONTEXT_CONFIG_Open_Router_Api_Key")

    Config.Api_Key = api_key

    # Use a cheap-ish model if desired; keep whatever default is configured.
    # Config.Model = "openai/gpt-3.5-turbo"

    prompt_name = "Smoke"
    prompt = "Reply with a single line containing exactly: OK"

    out = run_generation_graph(prompt=prompt, prompt_name=prompt_name)

    assert isinstance(out, str)
    assert out.strip() != ""
    assert "OK" in out
