import builtins
import io
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from context import code_generator
from context.config import Config

FILES_DIR = Path(__file__).parent / "files"


def _make_task(*, filepath: str, prompts: dict[str, str]):
    """Create a minimal Task-like object required by code_generator.generate_code."""

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
    """A tiny in-memory filesystem so tests can cover file mutation without tmp_path.

    code_generator.__apply_code opens the file twice: once for reading, once for writing.
    """

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


def test_generate_code_replaces_single_line_placeholder(tmp_path: Path, monkeypatch):
    # Inline placeholder path uses real file IO for the simplest happy path.
    monkeypatch.setattr(Config, "MockLLM", True)

    f = tmp_path / "inline.py"
    f.write_text("before\n{MyPrompt}\nafter\n", encoding="utf-8")

    task = _make_task(filepath=str(f), prompts={"MyPrompt": "do stuff"})
    task.prompt_outputs = {"MyPrompt"}

    code_generator.generate_code([task])

    assert f.read_text(encoding="utf-8") == "before\nMOCK_LLM_RESPONSE(MyPrompt)\nafter\n"


def test_generate_code_replaces_between_output_tags_without_tmp_path(monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", True)

    fake_path = "memory://output_tags.txt"
    fs = _FakeFS({fake_path: (FILES_DIR / "output_tags.txt").read_text(encoding="utf-8")})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"MyPrompt": "do stuff"})
    task.prompt_outputs_tags = {"MyPrompt": ""}

    code_generator.generate_code([task])

    assert fs.files[fake_path] == "<MyPrompt>\nMOCK_LLM_RESPONSE(MyPrompt)\n<MyPrompt/>\n"


def test_generate_code_output_target_mapping_writes_into_other_tag_without_tmp_path(monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", True)

    fake_path = "memory://output_target.txt"
    fs = _FakeFS({fake_path: (FILES_DIR / "output_target.txt").read_text(encoding="utf-8")})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"C": "do stuff"})
    # Prompt C should write into output tag <A>...</A/>
    task.prompt_output_targets = {"C": "A"}

    code_generator.generate_code([task])

    assert fs.files[fake_path] == "<A>\nMOCK_LLM_RESPONSE(C)\n<A/>\n<B>\nOLD_B\n<B/>\n"


def test_generate_code_constructs_prompt_with_context_and_global_without_tmp_path(monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", False)

    fake_path = "memory://construct_prompt.txt"
    fs = _FakeFS({fake_path: (FILES_DIR / "construct_prompt.txt").read_text(encoding="utf-8")})
    monkeypatch.setattr(builtins, "open", fs.open)

    task = _make_task(filepath=fake_path, prompts={"P": "Do thing. {X} {Prev}"})
    task.prompt_outputs = {"P"}
    task.context_dict = {"X": "hello"}
    task.prompt_outputs_tags = {"Prev": "previous output"}
    task.global_context = "global"

    captured = {}

    def fake_generate_code_with_chat(prompt: str, prompt_name: str) -> str:
        captured["prompt"] = prompt
        captured["prompt_name"] = prompt_name
        return json.dumps({"code": "GEN"})

    monkeypatch.setattr(code_generator, "generate_code_with_chat", fake_generate_code_with_chat)

    code_generator.generate_code([task])

    assert captured["prompt_name"] == "P"
    # Context variables are expanded as "\n\nNAME:\nVALUE"
    assert "\n\nX:\nhello" in captured["prompt"]
    assert "\n\nPrev:\nprevious output" in captured["prompt"]
    assert captured["prompt"].endswith("\nGLOBAL_CONTEXT:\nglobal")
    assert fs.files[fake_path] == "GEN\n"
