"""Unit tests for prompt dependency ordering.

Covers:
- Building a prompt execution order when prompts reference other prompts via {OtherPromptName} placeholders.
- Ensuring dependency chains are ordered correctly (A before B if B depends on A).
- Ensuring fan-in dependencies are respected (C after A and B if C references both).
- Handling dependency cycles gracefully (cycle detection fallback should not crash and should still produce an order).

These tests validate build_prompt_order(...) populates task.prompt_order and task.prompt_layers consistently.
"""


# TODO: Implement tests
