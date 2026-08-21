#!/bin/sh
set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CSS="$ROOT/frontend/src/app/globals.css"
TOKENS="$ROOT/frontend/src/lib/design-tokens.ts"

fail() {
    printf 'check-contrast: FAIL — %s\n' "$1" >&2
    exit 1
}

[ -f "$CSS" ] || fail "globals.css absent: $CSS"
[ -f "$TOKENS" ] || fail "design-tokens.ts absent: $TOKENS"
PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"

"$PYTHON" - "$CSS" "$TOKENS" <<'PY' || fail "contrast assertions failed"
import re
import sys

css_path, tokens_path = sys.argv[1:]
css = open(css_path, encoding="utf-8").read()
tokens = open(tokens_path, encoding="utf-8").read()

def reject(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)

def token(source: str, name: str, pattern: str) -> str:
    match = re.search(pattern.replace("{name}", re.escape(name)), source)
    if match is None:
        reject(f"required token missing or unparseable: {name}")
    return match.group(1).lower()

def hex_rgb(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"#[0-9a-f]{6}", value):
        reject(f"required core token is not a six-digit hex value: {value}")
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))

def luminance(value: str) -> float:
    channels = []
    for channel in hex_rgb(value):
        srgb = channel / 255
        channels.append(srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

def contrast(first: str, second: str) -> float:
    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)

values = {}
for name in ("navy", "accent", "bg", "foreground"):
    css_value = token(css, name, r"--color-{name}:\s*(#[0-9a-fA-F]{6})\s*;")
    ts_value = token(tokens, name, r"\b{name}:\s*[\"'](#[0-9a-fA-F]{6})[\"']")
    if css_value != ts_value:
        reject(f"token mismatch for {name}: globals.css={css_value}, design-tokens.ts={ts_value}")
    values[name] = css_value

white = "#ffffff"
combos = (
    ("foreground on bg", values["foreground"], values["bg"], 4.5),
    ("navy on bg", values["navy"], values["bg"], 4.5),
    ("accent on white", values["accent"], white, 4.5),
    ("accent on bg", values["accent"], values["bg"], 3.0),
    ("navy on white", values["navy"], white, 3.0),
    ("foreground on white", values["foreground"], white, 3.0),
)
for label, foreground, background, threshold in combos:
    ratio = contrast(foreground, background)
    print(f"{label}: {ratio:.2f}:1 (threshold {threshold:.1f}:1)")
    if ratio < threshold:
        reject(f"{label} is below threshold: {ratio:.2f}:1 < {threshold:.1f}:1")
PY

printf 'check-contrast: PASS\n'
