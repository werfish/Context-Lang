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

from conftest import read_fixture, write_file

from context.ast import build_prompt_order
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


def test_ast_ignores_unknown_and_self_placeholders(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "unknown_and_self_placeholders_ignored.txt")

    build_prompt_order([task])

    # A's self-reference and UNKNOWN should not create dependencies; only B depends on A.
    assert task.prompt_order == ["A", "B"]
    assert task.prompt_layers == [["A"], ["B"]]


def test_ast_cycle_falls_back_to_original_order(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "cycle.txt")

    build_prompt_order([task])

    # With a pure cycle, no prompt is ready; remaining prompts are appended in original order.
    assert task.prompt_order == ["A", "B"]
    assert task.prompt_layers == [["A", "B"]]


def test_ast_partial_cycle_preserves_ready_prompts_then_appends_remaining(tmp_path: Path) -> None:
    task = _parse_single_task(tmp_path, "partial_cycle_with_independent.txt")

    build_prompt_order([task])

    # X is ready; A/B are in a cycle and get appended as a fallback layer in original order.
    assert task.prompt_layers[0] == ["X"]
    assert task.prompt_layers[1] == ["A", "B"]
    assert task.prompt_order == ["X", "A", "B"]
