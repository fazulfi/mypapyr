#!/bin/sh
set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
GUARD="$ROOT/scripts/check-blog-content.sh"
[ -f "$GUARD" ] || { echo "test-check-blog-content: missing gate" >&2; exit 1; }
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT HUP INT TERM
mkdir -p "$TMP_DIR/frontend/content/blog/compress-pdf" "$TMP_DIR/scripts"
cp "$GUARD" "$TMP_DIR/scripts/check-blog-content.sh"
printf '# Broken\n\nNo link here at all.\n' > "$TMP_DIR/frontend/content/blog/compress-pdf/en.mdx"
if (cd "$TMP_DIR" && sh scripts/check-blog-content.sh) >/dev/null 2>&1; then
  echo "test-check-blog-content: FAIL — broken fixture passed the gate" >&2
  exit 1
fi
echo "test-check-blog-content: OK (broken fixture rejected)"
