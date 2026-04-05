"""Allow running the evaluator as ``python -m roboharness.evaluate``."""

from __future__ import annotations

import sys

from roboharness.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["evaluate", *sys.argv[1:]]))
