"""Happy-path unit tests for ContextLang tag parsing.

These tests validate the basic, expected functionality of each supported tag without
forcing error paths or relying on known quirks.
"""

from __future__ import annotations

from pathlib import Path

from conftest import read_fixture, write_file

from context.tag_parser import parse_tags


def test_parse_tags_multiple_prompts_both_captured_and_outputs_detected(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "multiple_prompts_basic.txt", read_fixture("multiple_prompts_basic.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.prompts == {"A": "Alpha", "B": "Beta"}
    assert set(task.prompt_outputs) == {"A", "B"}


def test_parse_tags_prompt_without_placeholder_has_empty_prompt_outputs(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "prompt_without_placeholder.txt", read_fixture("prompt_without_placeholder.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.prompts == {"Lonely": "Do something"}
    assert task.prompt_outputs == []


def test_parse_tags_prompt_output_tags_detected(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "prompt_output_tags.txt", read_fixture("prompt_output_tags.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]

    # Output tag mode: content captured under prompt_outputs_tags
    assert "Alpha" in task.prompt_outputs_tags
    assert task.prompt_outputs_tags["Alpha"] == "old"


def test_parse_tags_prompt_output_target_syntax_captures_mapping(tmp_path: Path) -> None:
    file_path = write_file(
        tmp_path,
        "prompt_output_target_basic.txt",
        read_fixture("prompt_output_target_basic.txt"),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]

    # Prompt name is stored without the target suffix.
    assert set(task.prompts.keys()) == {"A", "B", "C"}
    assert task.prompts["C"] == "Refine HTML using CSS {B}"

    # Target mapping present.
    assert task.prompt_output_targets == {"C": "A"}

    # Ensure the target output tag was still captured as a prompt output tag.
    assert task.prompt_outputs_tags["A"] == "old html"


def test_parse_tags_import_context_variables_from_other_file(tmp_path: Path) -> None:
    imported = write_file(tmp_path, "import_all_imported.txt", read_fixture("import_all_imported.txt"))

    main_template = read_fixture("import_all_main.txt")
    main_content = main_template.replace("__IMPORTED_PATH__", str(imported))
    main = write_file(tmp_path, "import_all_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.context_dict["ONE"] == "1"
    assert task.context_dict["TWO"] == "2"


def test_parse_tags_import_specific_context_variable(tmp_path: Path) -> None:
    imported = write_file(tmp_path, "import_specific_imported.txt", read_fixture("import_specific_imported.txt"))

    main_template = read_fixture("import_specific_main.txt")
    main_content = main_template.replace("__IMPORTED_PATH__", str(imported))
    main = write_file(tmp_path, "import_specific_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.context_dict["ONLY"] == "value"


def test_parse_tags_import_file_context_variables_reads_file_contents(tmp_path: Path) -> None:
    payload = write_file(tmp_path, "payload.txt", read_fixture("payload.txt"))

    main_template = read_fixture("file_import_main.txt")
    main_content = main_template.replace("__PAYLOAD_PATH__", str(payload))
    main = write_file(tmp_path, "file_import_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    # Current behavior: <file:VAR> reads the whole file verbatim (including trailing newline).
    assert task.context_dict["PAYLOAD"] == "payload contents\nline2\n"
