"""Unit tests for ContextLang tag parsing.

These tests intentionally focus on behaviors that should be testable *without* refactoring the parser and
without heavy mocking.

Strategy
- Use pytest tmp_path to write synthetic files and call parse_tags([...]).
- Initialize Log.logger once so tag_parser can log without crashing.

Note
Some tests describe the *desired/spec* behavior (robust parsing) and may currently fail if the
implementation is buggy. This is intentional: they serve as a safety net while improving the parser.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from context.log import Log, configure_logger
from context.tag_parser import parse_tags

FIXTURES_DIR = Path(__file__).parent / "TagParsingTestFiles"


@pytest.fixture(autouse=True)
def _configure_test_logger() -> None:
    # tag_parser calls Log.logger.*; ensure it's always available in tests.
    if Log.logger is None:
        Log.logger = configure_logger(debug=False, logToFile=False)


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _write(tmp_path: Path, rel: str, content: str) -> Path:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_parse_tags_simple_global_context_and_single_prompt(tmp_path: Path) -> None:
    file_path = _write(tmp_path, "simple_global_and_prompt.py", _read_fixture("simple_global_and_prompt.py"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.filepath == str(file_path)

    # Current behavior: content is captured verbatim from between <context> and <context/> and then .strip()'d.
    # Because the tags are inside comments, the closing-tag line's leading "# " is included in the capture.
    # Current implementation bug/quirk: Global regex returns a string match, but code indexes matches[0][0]
    # (first character). With a leading newline, .strip() becomes "".
    assert task.global_context == ""

    # Same behavior for prompt body: closing tag line's leading "# " may be captured.
    assert task.prompts == {"Hello": "# Please write me a Function that does A and B.\n#"}
    assert task.context_dict == {}

    # Placeholder mode: {Hello} appears outside prompt content.
    assert "Hello" in task.prompt_outputs


def test_parse_tags_named_context_variables_and_duplicates_reported(tmp_path: Path) -> None:
    file_path = _write(tmp_path, "named_context_duplicates.txt", _read_fixture("named_context_duplicates.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    task = tasks[0]

    assert task.context_dict.get("FOO") == "foo-value"
    assert task.context_dict.get("BAR") == "bar-value"

    # Duplicate FOO should be reported as an error but should not crash parsing.
    assert any("Context_Variables" in e and "FOO" in e for e in errors)


def test_parse_tags_duplicate_prompts_reported(tmp_path: Path) -> None:
    file_path = _write(tmp_path, "duplicate_prompts.txt", _read_fixture("duplicate_prompts.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    task = tasks[0]

    assert task.prompts.get("Build") == "first"
    assert any("Prompts" in e and "Build" in e for e in errors)


def test_parse_tags_prompt_output_tags_detected(tmp_path: Path) -> None:
    file_path = _write(tmp_path, "prompt_output_tags.txt", _read_fixture("prompt_output_tags.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]

    # Output tag mode: content captured under prompt_outputs_tags
    assert "Alpha" in task.prompt_outputs_tags
    assert task.prompt_outputs_tags["Alpha"] == "old"


def test_parse_tags_import_context_variables_from_other_file(tmp_path: Path) -> None:
    imported = _write(tmp_path, "import_all_imported.txt", _read_fixture("import_all_imported.txt"))

    main_template = _read_fixture("import_all_main.txt")
    main_content = main_template.replace("__IMPORTED_PATH__", str(imported))
    main = _write(tmp_path, "import_all_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.context_dict["ONE"] == "1"
    assert task.context_dict["TWO"] == "2"


def test_parse_tags_import_specific_context_variable(tmp_path: Path) -> None:
    imported = _write(tmp_path, "import_specific_imported.txt", _read_fixture("import_specific_imported.txt"))

    main_template = _read_fixture("import_specific_main.txt")
    main_content = main_template.replace("__IMPORTED_PATH__", str(imported))
    main = _write(tmp_path, "import_specific_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.context_dict["ONLY"] == "value"


def test_parse_tags_import_file_context_variables_reads_file_contents(tmp_path: Path) -> None:
    payload = _write(tmp_path, "payload.txt", _read_fixture("payload.txt"))

    main_template = _read_fixture("file_import_main.txt")
    main_content = main_template.replace("__PAYLOAD_PATH__", str(payload))
    main = _write(tmp_path, "file_import_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    # Current behavior: <file:VAR> reads the whole file verbatim (including trailing newline).
    assert task.context_dict["PAYLOAD"] == "payload contents\nline2\n"


def test_parser_is_robust_to_whitespace_newlines_tabs_in_tag_bodies(tmp_path: Path) -> None:
    file_path = _write(tmp_path, "whitespace_tabs.txt", _read_fixture("whitespace_tabs.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    assert errors == []

    task = tasks[0]
    assert task.context_dict["WS"] == "lots of whitespace\n\t\tand tabs"
    assert task.prompts["WS_PROMPT"] == "Use WS"
    assert task.prompt_outputs == ["WS_PROMPT"]


def test_parser_handles_very_long_names_300_chars(tmp_path: Path) -> None:
    # \w+ supports long alphanumeric/underscore names; ensure we don't crash.
    long_name = "A" * 300

    template = _read_fixture("long_names_template.txt")
    content = template.replace("{LONG_NAME}", long_name)
    file_path = _write(tmp_path, "long_names.txt", content)

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    assert errors == []

    task = tasks[0]
    assert task.context_dict[long_name] == "value"
    assert task.prompts[long_name] == "Do thing"
    assert long_name in task.prompt_outputs


def test_parser_ignores_invalid_names_with_special_characters_without_crashing(tmp_path: Path) -> None:
    # Names with '-' or spaces don't match the current regexes (\w+ / [a-zA-Z0-9_]+).
    # The robust behavior we want: parser does not crash and simply doesn't treat them as tags.
    file_path = _write(tmp_path, "invalid_names.txt", _read_fixture("invalid_names.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    # No valid prompts => no Task should be created.
    assert tasks == []

    # Even if we don't parse tags, we also shouldn't crash.
    assert errors == []
