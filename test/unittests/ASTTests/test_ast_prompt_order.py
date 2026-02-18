"""Unit tests for prompt dependency ordering (AST-like layering).

ContextLang prompt ordering goal
- Prompts can reference other prompt outputs via `{OtherPromptName}` placeholders.
- Prompts that depend on other prompts must run after their dependencies.
- ContextLang can have *multiple entry points* (multiple independent dependency trees).
- A single prompt may be depended on by many prompts (fan-out), and a prompt may depend on
  many prompts (fan-in).

Coverage
- No dependencies (preserves original prompt order, single layer).
- Simple chains (A -> B -> C).
- Fan-in (C depends on A and B).
- Fan-out + multiple roots (Root depended on by D1/D2; plus Solo independent).
- Ignores unknown placeholders and self-references.
- Cycles are handled gracefully (falls back to original order for remaining prompts).

These tests validate build_prompt_order(...) populates task.prompt_order and task.prompt_layers.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import read_fixture, write_file

from context.ast import PromptDependencyCycleError, build_prompt_order
from context.tag_parser import parse_tags


def _parse_single_task(tmp_path: Path, fixture_name: str) -> object:
    file_path = write_file(tmp_path, fixture_name, read_fixture(fixture_name))
    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])
    assert errors == []
    assert len(tasks) == 1
    return tasks[0]


def test_ast_no_dependencies_preserves_order_and_single_layer(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "no_dependencies.txt")

    build_prompt_order([task])

    assert task.prompt_order == ["A", "B"]
    assert task.prompt_layers == [["A", "B"]]


def test_ast_simple_chain_orders_by_dependencies(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "simple_chain.txt")

    build_prompt_order([task])

    assert task.prompt_order == ["A", "B", "C"]
    assert task.prompt_layers == [["A"], ["B"], ["C"]]


def test_ast_fan_in_c_after_a_and_b(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "fan_in.txt")

    build_prompt_order([task])

    # A and B have no deps, C depends on both.
    assert task.prompt_layers[0] == ["A", "B"]
    assert task.prompt_layers[1] == ["C"]
    assert task.prompt_order.index("C") > task.prompt_order.index("A")
    assert task.prompt_order.index("C") > task.prompt_order.index("B")


def test_ast_multiple_roots_and_fanout_layers(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "multiple_roots_and_fanout.txt")

    build_prompt_order([task])

    # Roots should be in the first layer: Root + Solo
    assert set(task.prompt_layers[0]) == {"Root", "Solo"}

    # D1 and D2 depend on Root => next layer
    assert set(task.prompt_layers[1]) == {"D1", "D2"}

    # Ensure dependency ordering holds.
    assert task.prompt_order.index("Root") < task.prompt_order.index("D1")
    assert task.prompt_order.index("Root") < task.prompt_order.index("D2")


def test_ast_fan_out_one_prompt_depended_on_by_three(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "fan_out_three.txt")

    build_prompt_order([task])

    assert task.prompt_layers[0] == ["Root"]
    assert set(task.prompt_layers[1]) == {"D1", "D2", "D3"}

    assert task.prompt_order.index("Root") < task.prompt_order.index("D1")
    assert task.prompt_order.index("Root") < task.prompt_order.index("D2")
    assert task.prompt_order.index("Root") < task.prompt_order.index("D3")


def test_ast_fan_in_three_prompts_depended_on_by_one(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "fan_in_three.txt")

    build_prompt_order([task])

    assert task.prompt_layers[0] == ["A", "B", "C"]
    assert task.prompt_layers[1] == ["D"]

    assert task.prompt_order.index("D") > task.prompt_order.index("A")
    assert task.prompt_order.index("D") > task.prompt_order.index("B")
    assert task.prompt_order.index("D") > task.prompt_order.index("C")


def test_ast_two_prompts_both_depend_on_three_prompts(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "three_roots_two_dependents.txt")

    build_prompt_order([task])

    assert task.prompt_layers[0] == ["A", "B", "C"]
    assert set(task.prompt_layers[1]) == {"D", "E"}

    for root in ["A", "B", "C"]:
        assert task.prompt_order.index(root) < task.prompt_order.index("D")
        assert task.prompt_order.index(root) < task.prompt_order.index("E")


def test_ast_ignores_unknown_and_self_placeholders(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "unknown_and_self_placeholders_ignored.txt")

    build_prompt_order([task])

    # A's self-reference and UNKNOWN should not create dependencies; only B depends on A.
    assert task.prompt_order == ["A", "B"]
    assert task.prompt_layers == [["A"], ["B"]]


def test_ast_cycle_raises_error(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "cycle.txt")

    with pytest.raises(PromptDependencyCycleError):
        build_prompt_order([task])


def test_ast_partial_cycle_raises_error(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "partial_cycle_with_independent.txt")

    with pytest.raises(PromptDependencyCycleError):
        build_prompt_order([task])


def test_ast_cycle_with_dependent_raises_error(tmp_path: Path) -> None:
    """A <-> C cycle, plus B depends on A.

    We fail fast rather than falling back to original order.
    """

    task = _parse_single_task(tmp_path, "cycle_with_dependent.txt")

    with pytest.raises(PromptDependencyCycleError):
        build_prompt_order([task])


def test_ast_workflow_same_target_tag_orders_prompts_by_dependencies(tmp_path: Path) -> None:
    """Workflow-like prompt chain where multiple prompts write into the same output tag.

    Scenario (mirrors Robert's example):
    - A writes into <X>
    - B depends on A
    - C depends on B
    - D depends on C and writes into <X>
    - E writes into <X>

    Expected AST ordering: A -> B -> C -> D -> E.
    """

    task = _parse_single_task(tmp_path, "workflow_same_target_tag.txt")

    build_prompt_order([task])

    assert task.prompt_order == ["A", "B", "C", "D", "E"]
