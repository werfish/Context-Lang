"""Unit tests for file discovery and ignore behavior.

Covers:
- Recursively collecting file paths under a directory.
- Respecting .gitignore rules (ignored files/dirs should not appear in get_file_paths output).
- Respecting the built-in ignore_list (e.g., Context_Logs directory).

These tests validate get_file_paths(...) returns the expected set of files for a synthetic directory tree.
"""


# TODO: Implement tests
