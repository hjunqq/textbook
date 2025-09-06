#!/usr/bin/env python3
"""
Thin CLI wrapper for the improved MD→LaTeX converter.

Usage examples:
  python tools/md2latex.py --project-root . --clean
  python tools/md2latex.py --convert-only
  python tools/md2latex.py --chapters 1,2
"""

import sys
from pathlib import Path

# Allow running from repo root or tools directory
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import improved_main_converter as conv  # type: ignore


def main(argv: list[str]) -> int:
    return conv.main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

