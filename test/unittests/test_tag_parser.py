"""Unit tests for ContextLang tag parsing.

Covers:
- Parsing <context> (global context) and erroring on multiple global contexts in one file.
- Parsing named context variables: <context:NAME>...</context:NAME/> (including duplicate-name errors).
- Parsing prompts: <prompt:PromptName>...</prompt:PromptName/> (including duplicate-name errors).
- Detecting prompt outputs referenced via {PromptName} in the file (output placeholder mode).
- Detecting prompt output blocks via <PromptName>...</PromptName/> (output tag mode).
- Importing context variables from other files via:
  - <import>...</import/>
  - <import:VAR>...</import:VAR/>
  - <file:VAR>...</file:VAR/>

These tests validate that parse_tags(...) returns correct Task objects and collects errors without crashing.
"""


# TODO: Implement tests
