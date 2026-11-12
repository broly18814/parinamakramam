# SPDX-License-Identifier: Apache-2.0
"""Lets `python -m pkv ...` run the pkv command.

The guard below means importing this file does nothing by itself, so a
self-check can import it safely; only `python -m pkv` runs the command.
"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
