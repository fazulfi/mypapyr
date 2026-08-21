#!/bin/sh
set -eu

fail() {
    printf 'test-check-contrast: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
GUARD="$ROOT/scripts/check-contrast.sh"
[ -f "$GUARD" ] || fail "check-contrast.sh absent: $GUARD"
PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"

FIXTURE=$(mktemp -d) || fail "cannot create temporary fixture"
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM
mkdir -p "$FIXTURE/frontend/src/app" "$FIXTURE/frontend/src/lib"
cp "$ROOT/frontend/src/app/globals.css" "$FIXTURE/frontend/src/app/globals.css"
cp "$ROOT/frontend/src/lib/design-tokens.ts" "$FIXTURE/frontend/src/lib/design-tokens.ts"

printf '=== 1. green: current tokens PASS ===\n'
if ! (cd "$ROOT" && sh "$GUARD") >/dev/null; then
    fail "guard rejected current tokens"
fi
printf 'PASS — current tokens accepted\n'

printf '=== 2. mutation: weak foreground/background FAIL ===\n'
"$PYTHON" - "$FIXTURE/frontend/src/app/globals.css" "$FIXTURE/frontend/src/lib/design-tokens.ts" <<'PY'
from pathlib import Path
import sys

css_path, tokens_path = map(Path, sys.argv[1:])
css_path.write_text(css_path.read_text(encoding="utf-8").replace("--color-foreground: #171717;", "--color-foreground: #ffffff;"), encoding="utf-8")
tokens_path.write_text(tokens_path.read_text(encoding="utf-8").replace('foreground: "#171717"', 'foreground: "#ffffff"'), encoding="utf-8")
PY

if (cd "$FIXTURE" && sh "$GUARD") >/dev/null 2>&1; then
    fail "guard accepted a mutated failing contrast combo"
fi
printf 'PASS — mutated failing combo rejected\n'
printf 'test-check-contrast: PASS\n'
