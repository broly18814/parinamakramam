# SPDX-License-Identifier: Apache-2.0
"""Parinama Verify (pkv): an independent checker for code changes.

Parts so far:
- gitdiff:  what changed, and the code's fingerprint (tree hash)
- imports:  the map of which Python files use which (import graph)
- affected: which tests a change could break, with reasons
- cli:      the `pkv` command
"""

__version__ = "0.1.2"
