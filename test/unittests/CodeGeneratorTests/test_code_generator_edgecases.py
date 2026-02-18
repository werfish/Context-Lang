import builtins
import io
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from context import code_generator
from context.config import Config

FILES_DIR = Path(__file__).parent / "files"


def _make_task(*, filepath: str, prompts: dict[str, str]):
    return SimpleNamespace(
        filepath=filepath,
        prompts=prompts,
        context_dict={},
        global_context="",
        prompt_outputs=set(),
        prompt_outputs_tags={},
        prompt_output_targets={},
        prompt_order=None,
    )


class _FakeFS:
    """In-memory filesystem for unit testing code_generator file mutations."""

    def __init__(self, files: dict[str, str]):
        self.files = dict(files)

    def open(self, path: str, mode: str = "r", *_args: Any, **_kwargs: Any):
        if "r" in mode:
            if path not in self.files:
                raise FileNotFoundError(path)
            return io.StringIO(self.files[path])

        if "w" in mode:
            buf = io.StringIO()
            original_close = buf.close

            def close_and_persist() -> None:
                self.files[path] = buf.getvalue()
                original_close()

            buf.close = close_and_persist  # type: ignore[method-assign]
            return buf

        raise ValueError(f"Unsupported mode: {mode}")


def test_single_file_flow_raises_on_invalid_llm_json(monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", False)

    fake_path = "memory://invalid_json.txt"
    fs = _FakeFS({fake_path: "{P}\n"})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"P": "x"})
    task.prompt_outputs = {"P"}

    monkeypatch.setattr(code_generator, "generate_code_with_chat", lambda *_: "not-json")

    with pytest.raises(json.JSONDecodeError):
        code_generator.__single_file_flow(task)


def test_single_file_flow_missing_code_key_is_noop(monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", False)

    fake_path = "memory://missing_code_key.txt"
    fs = _FakeFS({fake_path: "before\n{P}\nafter\n"})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"P": "x"})
    task.prompt_outputs = {"P"}

    monkeypatch.setattr(code_generator, "generate_code_with_chat", lambda *_: json.dumps({"nope": ""}))

    code_generator.__single_file_flow(task)

    # Current behavior: missing 'code' -> code=="" -> no write occurs.
    assert fs.files[fake_path] == "before\n{P}\nafter\n"


def test_apply_code_raises_when_start_tag_missing(monkeypatch):
    fake_path = "memory://missing_start_tag.txt"
    fs = _FakeFS({fake_path: "<MyPrompt/>\n"})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"MyPrompt": "x"})
    task.prompt_outputs_tags = {"MyPrompt": ""}

    with pytest.raises(StopIteration):
        code_generator.__apply_code("NEW", task, "MyPrompt")


def test_apply_code_raises_when_end_tag_missing(monkeypatch):
    fake_path = "memory://missing_end_tag.txt"
    fs = _FakeFS({fake_path: "<MyPrompt>\nOLD\n"})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"MyPrompt": "x"})
    task.prompt_outputs_tags = {"MyPrompt": ""}

    with pytest.raises(StopIteration):
        code_generator.__apply_code("NEW", task, "MyPrompt")


def test_apply_code_end_tag_before_start_tag_inserts_at_start_plus_one(monkeypatch):
    fake_path = "memory://end_before_start.txt"
    fs = _FakeFS({fake_path: "<X/>\n<X>\nOLD\n"})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"X": "x"})
    task.prompt_outputs_tags = {"X": ""}

    code_generator.__apply_code("NEW", task, "X")

    # Current behavior: slice assignment with end_line < start_line inserts at start_line+1.
    assert fs.files[fake_path] == "<X/>\n<X>\nNEW\nOLD\n"


def test_apply_code_replaces_all_placeholder_lines(monkeypatch):
    fake_path = "memory://two_placeholders.txt"
    fs = _FakeFS({fake_path: "{P}\nkeep\n{P}\n"})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"P": "x"})
    task.prompt_outputs = {"P"}

    code_generator.__apply_code("NEW", task, "P")

    assert fs.files[fake_path] == "NEW\nkeep\nNEW\n"


def test_apply_code_uses_first_tag_pair_when_multiple_blocks_exist(monkeypatch):
    fake_path = "memory://two_blocks.txt"
    fs = _FakeFS(
        {
            fake_path: "<T>\nOLD1\n<T/>\nmid\n<T>\nOLD2\n<T/>\n",
        }
    )
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"T": "x"})
    task.prompt_outputs_tags = {"T": ""}

    code_generator.__apply_code("NEW", task, "T")

    assert fs.files[fake_path] == "<T>\nNEW\n<T/>\nmid\n<T>\nOLD2\n<T/>\n"


def test_prompt_order_controls_last_write_when_two_prompts_target_same_tag(monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", False)

    fake_path = "memory://collisions.txt"
    fs = _FakeFS({fake_path: (FILES_DIR / "output_target.txt").read_text(encoding="utf-8")})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"P1": "x", "P2": "x"})
    task.prompt_output_targets = {"P1": "A", "P2": "A"}
    task.prompt_order = ["P1", "P2"]

    def fake_generate(prompt: str, prompt_name: str) -> str:
        return json.dumps({"code": f"CODE_{prompt_name}"})

    monkeypatch.setattr(code_generator, "generate_code_with_chat", fake_generate)

    code_generator.__single_file_flow(task)

    assert fs.files[fake_path].startswith("<A>\nCODE_P2\n<A/>\n")


def test_process_prompt_leaves_unknown_placeholders_intact():
    task = _make_task(filepath="x", prompts={"P": "Use {KNOWN} and {UNKNOWN}."})
    task.context_dict = {"KNOWN": "k"}

    out = code_generator.__process_prompt(task.prompts["P"], task)

    assert "KNOWN:\nk" in out
    assert "{UNKNOWN}" in out
