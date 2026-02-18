"""Edge-case/quirk unit tests for ContextLang tag parsing.

These tests lock in current implementation quirks and error-path behavior so we can
refactor later with confidence (or update expected behavior intentionally).
"""

from __future__ import annotations

from pathlib import Path

from conftest import read_fixture, write_file

from context.tag_parser import parse_tags


def test_parse_tags_simple_global_context_and_single_prompt(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "simple_global_and_prompt.py", read_fixture("simple_global_and_prompt.py"))

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
    file_path = write_file(tmp_path, "named_context_duplicates.txt", read_fixture("named_context_duplicates.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    task = tasks[0]

    assert task.context_dict.get("FOO") == "foo-value"
    assert task.context_dict.get("BAR") == "bar-value"

    # Duplicate FOO should be reported as an error but should not crash parsing.
    assert any("Context_Variables" in e and "FOO" in e for e in errors)


def test_parse_tags_duplicate_prompts_reported(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "duplicate_prompts.txt", read_fixture("duplicate_prompts.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    task = tasks[0]

    assert task.prompts.get("Build") == "first"
    assert any("Prompts" in e and "Build" in e for e in errors)


def test_parser_is_robust_to_whitespace_newlines_tabs_in_tag_bodies(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "whitespace_tabs.txt", read_fixture("whitespace_tabs.txt"))

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

    template = read_fixture("long_names_template.txt")
    content = template.replace("{LONG_NAME}", long_name)
    file_path = write_file(tmp_path, "long_names.txt", content)

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
    file_path = write_file(tmp_path, "invalid_names.txt", read_fixture("invalid_names.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    # No valid prompts => no Task should be created.
    assert tasks == []

    # Even if we don't parse tags, we also shouldn't crash.
    assert errors == []


def test_parse_tags_multiple_global_tags_reports_error(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "multiple_global_tags.txt", read_fixture("multiple_global_tags.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    # Task still created because prompts exist.
    assert len(tasks) == 1

    assert any("Multiple Global tags" in e for e in errors)


def test_parse_tags_placeholder_only_inside_prompt_body_is_skipped(tmp_path: Path) -> None:
    file_path = write_file(
        tmp_path, "placeholder_only_inside_prompt.txt", read_fixture("placeholder_only_inside_prompt.txt")
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert "Inner" in task.prompts
    assert task.prompt_outputs == []


def test_parse_tags_import_specific_context_variable_missing_reports_error(tmp_path: Path) -> None:
    imported = write_file(
        tmp_path,
        "import_specific_missing_var_imported.txt",
        read_fixture("import_specific_missing_var_imported.txt"),
    )

    main_template = read_fixture("import_specific_missing_var_main.txt")
    main_content = main_template.replace("__IMPORTED_PATH__", str(imported))
    main = write_file(tmp_path, "import_specific_missing_var_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert len(tasks) == 1

    # Current behavior: missing var produces an error string.
    assert any("does not exists" in e and "MISSING" in e for e in errors)


def test_parse_tags_import_all_duplicate_var_reports_error_and_imported_value_wins(tmp_path: Path) -> None:
    imported = write_file(
        tmp_path,
        "import_all_duplicate_var_imported.txt",
        read_fixture("import_all_duplicate_var_imported.txt"),
    )

    main_template = read_fixture("import_all_duplicate_var_main.txt")
    main_content = main_template.replace("__IMPORTED_PATH__", str(imported))
    main = write_file(tmp_path, "import_all_duplicate_var_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert len(tasks) == 1

    task = tasks[0]

    # Current behavior (due to processing order): the <import> runs before the main file's
    # own <context:...> tags, so the imported value wins and the in-file declaration is
    # treated as a duplicate.
    assert task.context_dict["ONE"] == "imported"
    assert any("Context_Variables" in e and "ONE" in e for e in errors)


def test_parse_tags_file_import_missing_payload_reports_error(tmp_path: Path) -> None:
    # Use a non-existent path on purpose.
    missing_payload_path = str(tmp_path / "does_not_exist_payload.txt")

    main_template = read_fixture("file_import_missing_payload_main.txt")
    main_content = main_template.replace("__PAYLOAD_PATH__", missing_payload_path)
    main = write_file(tmp_path, "file_import_missing_payload_main.txt", main_content)

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert len(tasks) == 1

    # Current behavior: the error string includes the main file's relative path and the underlying
    # FileNotFoundError message.
    assert any("No such file" in e or "Errno" in e for e in errors)


def test_parse_tags_prompt_output_tag_name_collision_with_context_variable_reports_error(tmp_path: Path) -> None:
    file_path = write_file(
        tmp_path,
        "prompt_output_tag_collides_with_context.txt",
        read_fixture("prompt_output_tag_collides_with_context.txt"),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    assert any("already declared" in e and "Alpha" in e for e in errors)


def test_parse_tags_file_with_only_context_tags_creates_no_task(tmp_path: Path) -> None:
    file_path = write_file(tmp_path, "only_context_no_prompts.txt", read_fixture("only_context_no_prompts.txt"))

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert tasks == []
    assert errors == []


def test_parse_tags_prompt_output_target_duplicate_prompt_reports_error(tmp_path: Path) -> None:
    file_path = write_file(
        tmp_path,
        "prompt_output_target_duplicate_prompt.txt",
        read_fixture("prompt_output_target_duplicate_prompt.txt"),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    # Task still created, but duplicate prompt name should be reported.
    assert len(tasks) == 1
    assert any("Prompts" in e and "Prompt 'C'" in e for e in errors)


def test_parse_tags_prompt_output_target_invalid_syntax_is_ignored_without_crashing(tmp_path: Path) -> None:
    file_path = write_file(
        tmp_path,
        "prompt_output_target_invalid_syntax_not_parsed.txt",
        read_fixture("prompt_output_target_invalid_syntax_not_parsed.txt"),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    # Invalid prompt tag should not match the regex => no prompts => no Task.
    assert tasks == []
    assert errors == []


def test_parse_tags_prompt_output_target_double_arrow_is_ignored_without_crashing(tmp_path: Path) -> None:
    file_path = write_file(
        tmp_path,
        "prompt_output_target_double_arrow_not_parsed.txt",
        read_fixture("prompt_output_target_double_arrow_not_parsed.txt"),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    # Invalid prompt tag should not match the regex => no prompts => no Task.
    assert tasks == []
    assert errors == []
