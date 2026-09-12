#!/bin/bash
# Compatibility entry point; build_tikz.py verifies source and SVG hashes.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/build_tikz.py" "$@"
