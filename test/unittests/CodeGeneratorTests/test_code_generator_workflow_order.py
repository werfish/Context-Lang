import json
from types import SimpleNamespace

import pytest

from context import code_generator
from context.ast import build_prompt_order


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


def test_code_generation_workflow_runs_prompts_in_ast_order_and_overwrites_target_tag(
    tmp_path: pytest.TempPathFactory, monkeypatch
):
    """End-to-end-ish unit test (no real LLM): prompt A->E workflow executes in AST order.

    Uses the same dependency chain as the AST workflow test:
    A -> B -> C -> D -> E, where A/D/E write into <A>.
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
old
<A/>

<B>
old
<B/>

<C>
old
<C/>

<D>
old
<D/>
""".lstrip(),
        encoding="utf-8",
    )

    # Parse tags -> build AST order -> run code generation
    from context.tag_parser import parse_tags

    tasks, errors = parse_tags([str(f)], in_comment_signs=[])
    assert errors == []
    assert len(tasks) == 1
    task = tasks[0]

    build_prompt_order([task])
    assert task.prompt_order == ["A", "B", "C", "D", "E"]

    call_order = []

    def fake_generate_code_with_chat(prompt: str, prompt_name: str) -> str:
        call_order.append(prompt_name)
        return json.dumps({"code": f"CODE_{prompt_name}"})

    monkeypatch.setattr(code_generator, "generate_code_with_chat", fake_generate_code_with_chat)

    code_generator.generate_code([task])

    assert call_order == ["A", "B", "C", "D", "E"]

    # Since A/D/E target <A>, final write should be from E.
    final = f.read_text(encoding="utf-8")
    assert "<A>" in final
    assert "<A/>" in final

    start = final.index("<A>")
    end = final.index("<A/>")
    a_block = final[start:end]

    assert "CODE_E" in a_block
    assert "CODE_A" not in a_block
    assert "CODE_D" not in a_block
