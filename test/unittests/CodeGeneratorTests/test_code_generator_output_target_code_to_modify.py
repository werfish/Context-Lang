import json

import pytest

from context import code_generator
from context.ast import build_prompt_order
from context.tag_parser import parse_tags


def test_output_target_prompt_includes_code_to_modify_and_is_up_to_date(tmp_path: pytest.TempPathFactory, monkeypatch):
    """Regression test for workflow prompts that overwrite an existing output tag via ->.

    Desired behavior (NOT implemented yet):
    When a prompt uses output-target syntax (e.g. <prompt:D->A>), the prompt sent to the LLM should
    automatically include the up-to-date code currently inside the target tag, appended as:

        CODE_TO_MODIFY:\n<code>

    This enables multi-step revision workflows where each step sees the latest code.
    """

    f = tmp_path / "workflow.txt"
    f.write_text(
        """
<prompt:A>
Seed A
<prompt:A/>

<prompt:B>
Use {A}
<prompt:B/>

<prompt:C>
Use {B}
<prompt:C/>

<prompt:D->A>
Refine A using {C}
<prompt:D->A/>

<prompt:E->A>
Final polish of A using {D}
<prompt:E->A/>

<A>
initial
<A/>
""".lstrip(),
        encoding="utf-8",
    )

    tasks, errors = parse_tags([str(f)], in_comment_signs=[])
    assert errors == []
    assert len(tasks) == 1
    task = tasks[0]

    build_prompt_order([task])
    assert task.prompt_order == ["A", "B", "C", "D", "E"]

    seen_prompts: dict[str, str] = {}

    def fake_generate_code_with_chat(prompt: str, prompt_name: str) -> str:
        seen_prompts[prompt_name] = prompt
        return json.dumps({"code": f"CODE_{prompt_name}"})

    monkeypatch.setattr(code_generator, "generate_code_with_chat", fake_generate_code_with_chat)

    code_generator.generate_code([task])

    # Expectations for output-target prompts:
    # - D targets A, so D should receive the current contents of <A> (after A ran => CODE_A)
    assert "CODE_TO_MODIFY:" in seen_prompts["D"]
    assert "CODE_A" in seen_prompts["D"]

    # - E targets A and runs after D, so it should receive CODE_D as the latest version.
    assert "CODE_TO_MODIFY:" in seen_prompts["E"]
    assert "CODE_D" in seen_prompts["E"]


def test_output_target_code_to_modify_uses_latest_over_initial_value(tmp_path: pytest.TempPathFactory, monkeypatch):
    """If <A> already had content, CODE_TO_MODIFY should still use the up-to-date version.

    In this scenario, A runs first and overwrites <A> with CODE_A. D->A should therefore see CODE_A
    (not the original 'initial').
    """

    f = tmp_path / "workflow_initial.txt"
    f.write_text(
        """
<prompt:A>
Seed A
<prompt:A/>

<prompt:D->A>
Refine A
<prompt:D->A/>

{A}
{D}

<A>
initial
<A/>
""".lstrip(),
        encoding="utf-8",
    )

    tasks, errors = parse_tags([str(f)], in_comment_signs=[])
    assert errors == []
    task = tasks[0]

    build_prompt_order([task])
    assert task.prompt_order == ["A", "D"]

    seen_prompts: dict[str, str] = {}

    def fake_generate_code_with_chat(prompt: str, prompt_name: str) -> str:
        seen_prompts[prompt_name] = prompt
        return json.dumps({"code": f"CODE_{prompt_name}"})

    monkeypatch.setattr(code_generator, "generate_code_with_chat", fake_generate_code_with_chat)

    code_generator.generate_code([task])

    assert "CODE_TO_MODIFY:" in seen_prompts["D"]
    assert "CODE_A" in seen_prompts["D"]
    assert "initial" not in seen_prompts["D"]


def test_output_target_code_to_modify_includes_multiline_tag_content(tmp_path: pytest.TempPathFactory, monkeypatch):
    """CODE_TO_MODIFY should include multi-line code blocks, not just a single line."""

    f = tmp_path / "workflow_multiline.txt"
    f.write_text(
        """
<prompt:D->A>
Refine A
<prompt:D->A/>

{D}

<A>
line1
line2
line3
<A/>
""".lstrip(),
        encoding="utf-8",
    )

    tasks, errors = parse_tags([str(f)], in_comment_signs=[])
    assert errors == []
    task = tasks[0]

    build_prompt_order([task])
    assert task.prompt_order == ["D"]

    seen_prompts: dict[str, str] = {}

    def fake_generate_code_with_chat(prompt: str, prompt_name: str) -> str:
        seen_prompts[prompt_name] = prompt
        return json.dumps({"code": f"CODE_{prompt_name}"})

    monkeypatch.setattr(code_generator, "generate_code_with_chat", fake_generate_code_with_chat)

    code_generator.generate_code([task])

    assert "CODE_TO_MODIFY:" in seen_prompts["D"]
    assert "line1" in seen_prompts["D"]
    assert "line2" in seen_prompts["D"]
    assert "line3" in seen_prompts["D"]


def test_non_target_prompts_do_not_get_code_to_modify_appended(tmp_path: pytest.TempPathFactory, monkeypatch):
    """Only -> prompts should get CODE_TO_MODIFY; normal prompts should not."""

    f = tmp_path / "workflow_non_target.txt"
    f.write_text(
        """
<prompt:A>
Seed A
<prompt:A/>

<prompt:B>
Use {A}
<prompt:B/>

{A}
{B}

<A>
initial
<A/>
""".lstrip(),
        encoding="utf-8",
    )

    tasks, errors = parse_tags([str(f)], in_comment_signs=[])
    assert errors == []
    task = tasks[0]

    build_prompt_order([task])
    assert task.prompt_order == ["A", "B"]

    seen_prompts: dict[str, str] = {}

    def fake_generate_code_with_chat(prompt: str, prompt_name: str) -> str:
        seen_prompts[prompt_name] = prompt
        return json.dumps({"code": f"CODE_{prompt_name}"})

    monkeypatch.setattr(code_generator, "generate_code_with_chat", fake_generate_code_with_chat)

    code_generator.generate_code([task])

    assert "CODE_TO_MODIFY:" not in seen_prompts["A"]
    assert "CODE_TO_MODIFY:" not in seen_prompts["B"]
