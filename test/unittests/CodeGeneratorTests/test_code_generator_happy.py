import json
from types import SimpleNamespace

import pytest

from context import code_generator
from context.config import Config


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


def test_generate_code_replaces_single_line_placeholder(tmp_path: pytest.TempPathFactory, monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", True)

    f = tmp_path / "a.py"
    f.write_text("before\n{MyPrompt}\nafter\n", encoding="utf-8")

    task = _make_task(filepath=str(f), prompts={"MyPrompt": "do stuff"})
    task.prompt_outputs = {"MyPrompt"}

    code_generator.generate_code([task])

    assert f.read_text(encoding="utf-8") == "before\nMOCK_LLM_RESPONSE(MyPrompt)\nafter\n"


def test_generate_code_replaces_between_output_tags(tmp_path: pytest.TempPathFactory, monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", True)

    f = tmp_path / "b.py"
    f.write_text("<MyPrompt>\nOLD\n<MyPrompt/>\n", encoding="utf-8")

    task = _make_task(filepath=str(f), prompts={"MyPrompt": "do stuff"})
    task.prompt_outputs_tags = {"MyPrompt": ""}

    code_generator.generate_code([task])

    assert f.read_text(encoding="utf-8") == "<MyPrompt>\nMOCK_LLM_RESPONSE(MyPrompt)\n<MyPrompt/>\n"


def test_generate_code_output_target_mapping_writes_into_other_tag(tmp_path: pytest.TempPathFactory, monkeypatch):
    monkeypatch.setattr(Config, "MockLLM", True)

    f = tmp_path / "c.py"
    f.write_text("<A>\nOLD_A\n<A/>\n<B>\nOLD_B\n<B/>\n", encoding="utf-8")

    task = _make_task(filepath=str(f), prompts={"C": "do stuff"})
    # Prompt C should write into output tag <A>...</A/>
    task.prompt_output_targets = {"C": "A"}

    code_generator.generate_code([task])

    assert f.read_text(encoding="utf-8") == "<A>\nMOCK_LLM_RESPONSE(C)\n<A/>\n<B>\nOLD_B\n<B/>\n"


def test_generate_code_constructs_prompt_with_context_and_global(monkeypatch, tmp_path: pytest.TempPathFactory):
    monkeypatch.setattr(Config, "MockLLM", False)

    f = tmp_path / "d.py"
    f.write_text("{P}\n", encoding="utf-8")

    task = _make_task(filepath=str(f), prompts={"P": "Do thing. {X} {Prev}"})
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
    assert f.read_text(encoding="utf-8") == "GEN\n"
