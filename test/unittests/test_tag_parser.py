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


@pytest.fixture(autouse=True)
def _configure_test_logger() -> None:
    # tag_parser calls Log.logger.*; ensure it's always available in tests.
    if Log.logger is None:
        Log.logger = configure_logger(debug=False, logToFile=False)


def _write(tmp_path: Path, rel: str, content: str) -> Path:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_parse_tags_simple_global_context_and_single_prompt(tmp_path: Path) -> None:
    file_path = _write(
        tmp_path,
        "main.py",
        """
# <context>
# You are a helpful assistant.
# <context/>

# <prompt:Hello>
# Say hi
# <prompt:Hello/>

print({Hello})
""".strip(),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.filepath == str(file_path)

    # Desired behavior: global context is the full captured body (trimmed)
    assert (
        task.global_context == "# You are a helpful assistant." or task.global_context == "You are a helpful assistant."
    )

    assert task.prompts == {"Hello": "# Say hi"} or task.prompts == {"Hello": "Say hi"}
    assert task.context_dict == {}

    # Placeholder mode: {Hello} appears outside prompt content.
    assert "Hello" in task.prompt_outputs


def test_parse_tags_named_context_variables_and_duplicates_reported(tmp_path: Path) -> None:
    file_path = _write(
        tmp_path,
        "main.txt",
        """
<context:FOO>
foo-value
<context:FOO/>

<context:BAR>
bar-value
<context:BAR/>

<context:FOO>
duplicate
<context:FOO/>

<prompt:P1>
Use {FOO} and {BAR}
<prompt:P1/>

{P1}
""".strip(),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    task = tasks[0]

    assert task.context_dict.get("FOO") == "foo-value"
    assert task.context_dict.get("BAR") == "bar-value"

    # Duplicate FOO should be reported as an error but should not crash parsing.
    assert any("Context_Variables" in e and "FOO" in e for e in errors)


def test_parse_tags_duplicate_prompts_reported(tmp_path: Path) -> None:
    file_path = _write(
        tmp_path,
        "main.txt",
        """
<prompt:Build>
first
<prompt:Build/>

<prompt:Build>
second
<prompt:Build/>

{Build}
""".strip(),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    task = tasks[0]

    assert task.prompts.get("Build") == "first"
    assert any("Prompts" in e and "Build" in e for e in errors)


def test_parse_tags_prompt_output_tags_detected(tmp_path: Path) -> None:
    file_path = _write(
        tmp_path,
        "main.txt",
        """
<prompt:Alpha>
Generate code
<prompt:Alpha/>

<Alpha>
old
<Alpha/>
""".strip(),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]

    # Output tag mode: content captured under prompt_outputs_tags
    assert "Alpha" in task.prompt_outputs_tags
    assert task.prompt_outputs_tags["Alpha"] == "old"


def test_parse_tags_import_context_variables_from_other_file(tmp_path: Path) -> None:
    imported = _write(
        tmp_path,
        "imported.txt",
        """
<context:ONE>
1
<context:ONE/>

<context:TWO>
2
<context:TWO/>
""".strip(),
    )
    main = _write(
        tmp_path,
        "main.txt",
        f"""
<import>
{imported}
<import/>

<prompt:P>
Use ONE and TWO
<prompt:P/>

{{P}}
""".strip(),
    )

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.context_dict["ONE"] == "1"
    assert task.context_dict["TWO"] == "2"


def test_parse_tags_import_specific_context_variable(tmp_path: Path) -> None:
    imported = _write(
        tmp_path,
        "imported.txt",
        """
<context:ONLY>
value
<context:ONLY/>
""".strip(),
    )
    main = _write(
        tmp_path,
        "main.txt",
        f"""
<import:ONLY>
{imported}
<import:ONLY/>

<prompt:P>
Use ONLY
<prompt:P/>

{{P}}
""".strip(),
    )

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.context_dict["ONLY"] == "value"


def test_parse_tags_import_file_context_variables_reads_file_contents(tmp_path: Path) -> None:
    payload = _write(tmp_path, "payload.txt", "payload contents\nline2\n")
    main = _write(
        tmp_path,
        "main.txt",
        f"""
<file:PAYLOAD>
{payload}
<file:PAYLOAD/>

<prompt:P>
Use file payload
<prompt:P/>

{{P}}
""".strip(),
    )

    tasks, errors = parse_tags([str(main)], in_comment_signs=[])

    assert errors == []
    assert len(tasks) == 1

    task = tasks[0]
    assert task.context_dict["PAYLOAD"] == "payload contents\nline2"


def test_parser_is_robust_to_whitespace_newlines_tabs_in_tag_bodies(tmp_path: Path) -> None:
    file_path = _write(
        tmp_path,
        "main.txt",
        """
<context:WS>
\n\n\t  lots of whitespace\n\t\tand tabs\n\n<context:WS/>

<prompt:WS_PROMPT>
\tUse WS\n\n<prompt:WS_PROMPT/>

{WS_PROMPT}
""".strip(),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    assert errors == []

    task = tasks[0]
    assert "WS" in task.context_dict
    assert "WS_PROMPT" in task.prompts
    assert "WS_PROMPT" in task.prompt_outputs


def test_parser_handles_very_long_names_300_chars(tmp_path: Path) -> None:
    # \\w+ supports long alphanumeric/underscore names; ensure we don't crash.
    long_name = "A" * 300

    file_path = _write(
        tmp_path,
        "main.txt",
        f"""
<context:{long_name}>
value
<context:{long_name}/>

<prompt:{long_name}>
Do thing
<prompt:{long_name}/>

{{{long_name}}}
""".strip(),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    assert len(tasks) == 1
    assert errors == []

    task = tasks[0]
    assert task.context_dict[long_name] == "value"
    assert task.prompts[long_name] == "Do thing"
    assert long_name in task.prompt_outputs


def test_parser_ignores_invalid_names_with_special_characters_without_crashing(tmp_path: Path) -> None:
    # Names with '-' or spaces don't match the current regexes (\\w+ / [a-zA-Z0-9_]+).
    # The robust behavior we want: parser does not crash and simply doesn't treat them as tags.
    file_path = _write(
        tmp_path,
        "main.txt",
        """
<context:bad-name>
value
<context:bad-name/>

<prompt:bad name>
Nope
<prompt:bad name/>

{bad-name}
""".strip(),
    )

    tasks, errors = parse_tags([str(file_path)], in_comment_signs=[])

    # No valid prompts => no Task should be created.
    assert tasks == []

    # Even if we don't parse tags, we also shouldn't crash.
    assert errors == []
