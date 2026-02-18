from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import load_dotenv

from context.config import Config
from context.graph import run_generation_graph

pytestmark = pytest.mark.llm


def _snapshot_config() -> tuple[str, str]:
    return (Config.Api_Key, Config.Model)


def _restore_config(snapshot: tuple[str, str]) -> None:
    Config.Api_Key, Config.Model = snapshot


def _load_env() -> None:
    # Ensure local .env is loaded for LLM tests.
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env")


def test_run_generation_graph_openrouter_smoke() -> None:
    snapshot = _snapshot_config()
    try:
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
        assert out.strip() == "OK"
    finally:
        _restore_config(snapshot)


def test_run_generation_graph_raises_on_invalid_api_key() -> None:
    """True integration test: exercise real provider auth failure (no mocking)."""

    snapshot = _snapshot_config()
    try:
        _load_env()

        real_key = Config.Api_Key or __import__("os").getenv("CONTEXT_CONFIG_Open_Router_Api_Key")
        if not real_key:
            pytest.skip("Missing CONTEXT_CONFIG_Open_Router_Api_Key")

        Config.Api_Key = "sk-invalid"  # deliberately invalid

        prompt_name = "InvalidKey"
        prompt = "Reply with exactly: OK"

        with pytest.raises(Exception):  # noqa: B017 (integration test: provider-specific exception)
            run_generation_graph(prompt=prompt, prompt_name=prompt_name)
    finally:
        _restore_config(snapshot)
