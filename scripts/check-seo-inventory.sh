#!/bin/sh
#
# check-seo-inventory.sh — SEO-01 governance guard (SH-04, R-15, R-16, R-25,
# DEC-127, DEC-194, DEC-114).
#
# Verifies the single authoritative SEO inventories stay in sync with the
# running application, fail-closed:
#   * docs/seo/legacy-url-inventory.md — every legacy locale-less path has
#     exactly one disposition (301/410/307) whose mechanism is defined.
#   * docs/seo/slug-table.md — the 5 canonical tool slugs and their localized
#     hrefs are present (301 targets are real, indexable slugs).
#   * frontend/src/lib/i18n.ts LEGACY_ROUTING_PATHS — the 15-path inventory
#     exactly equals the app's reserved legacy set (no drift, no duplicates,
#     no conflicting slug tables).
#
# Exit codes:
#   0 = inventories consistent with code (PASS)
#   1 = drift / missing disposition / unmapped mechanism / duplicate (FAIL)
#   2 = an artifact is absent or unreadable
#
# Testability: pass an explicit repo root as $1 (defaults to git rev-parse) so
# the self-test (scripts/test-check-seo-inventory.sh) can run the guard against
# a mutated fixture and prove it fails closed.

set -eu

fail() {
    printf 'check-seo-inventory: FAIL — %s\n' "$1" >&2
    exit 1
}

[ $# -gt 1 ] && fail "unexpected arguments (expected at most one repo root)"

if [ $# -eq 1 ]; then
    ROOT=$1
else
    ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi

LEGACY_DOC="$ROOT/docs/seo/legacy-url-inventory.md"
SLUG_DOC="$ROOT/docs/seo/slug-table.md"
I18N_SRC="$ROOT/frontend/src/lib/i18n.ts"
TOOL_IDS_SRC="$ROOT/frontend/src/lib/tool-ids.ts"

[ -f "$LEGACY_DOC" ] || { printf 'check-seo-inventory: FAIL — inventory absent: %s\n' "$LEGACY_DOC"; exit 2; }
[ -f "$SLUG_DOC" ] || { printf 'check-seo-inventory: FAIL — slug table absent: %s\n' "$SLUG_DOC"; exit 2; }
[ -f "$I18N_SRC" ] || { printf 'check-seo-inventory: FAIL — i18n source absent: %s\n' "$I18N_SRC"; exit 2; }
[ -f "$TOOL_IDS_SRC" ] || { printf 'check-seo-inventory: FAIL — tool-ids source absent: %s\n' "$TOOL_IDS_SRC"; exit 2; }

# Normalize each disposition row to "<path>|<disposition>" (no spaces) for
# unambiguous field extraction.
INV_PATH_DISP=$(
    grep -E '^\| /[^|]+\|' "$LEGACY_DOC" \
        | sed -E 's/^\| *([^ |]+) *\| *([0-9]{3}) *\|.*/\1|\2/'
)
[ -n "$INV_PATH_DISP" ] || fail "no legacy disposition rows found in $LEGACY_DOC"

PATH_LIST=$(printf '%s\n' "$INV_PATH_DISP" | cut -d'|' -f1 | sort)
DISP_LIST=$(printf '%s\n' "$INV_PATH_DISP" | cut -d'|' -f2)

ROW_COUNT=$(printf '%s\n' "$PATH_LIST" | wc -l | tr -d ' ')
[ "$ROW_COUNT" -eq 15 ] || fail "expected exactly 15 legacy paths, found $ROW_COUNT"
UNIQ_COUNT=$(printf '%s\n' "$PATH_LIST" | sort -u | wc -l | tr -d ' ')
[ "$UNIQ_COUNT" -eq 15 ] || fail "duplicate legacy path in inventory (15 rows, $UNIQ_COUNT unique)"

COUNT_301=$(printf '%s\n' "$DISP_LIST" | grep -x '301' | wc -l | tr -d ' ')
COUNT_410=$(printf '%s\n' "$DISP_LIST" | grep -x '410' | wc -l | tr -d ' ')
COUNT_307=$(printf '%s\n' "$DISP_LIST" | grep -x '307' | wc -l | tr -d ' ')
[ "$COUNT_301" -eq 5 ] || fail "expected 5 × 301, found $COUNT_301"
[ "$COUNT_410" -eq 8 ] || fail "expected 8 × 410, found $COUNT_410"
[ "$COUNT_307" -eq 2 ] || fail "expected 2 × 307, found $COUNT_307"

printf '%s\n' "$DISP_LIST" | grep -v '^301$\|^410$\|^307$' | grep -q . \
    && fail "inventory contains an undefined disposition"
true

SRC_PATHS=$(
    sed -n '/export const LEGACY_ROUTING_PATHS/,/]);/p' "$I18N_SRC" \
        | grep -oE '"/[^"]+"' | tr -d '"' | sort
)
[ -n "$SRC_PATHS" ] || fail "unable to parse LEGACY_ROUTING_PATHS from $I18N_SRC"
SRC_COUNT=$(printf '%s\n' "$SRC_PATHS" | wc -l | tr -d ' ')
[ "$SRC_COUNT" -eq 15 ] || fail "app LEGACY_ROUTING_PATHS has $SRC_COUNT paths, expected 15"

INV_PATHS=$(printf '%s\n' "$INV_PATH_DISP" | cut -d'|' -f1 | sort)
if [ "$INV_PATHS" != "$SRC_PATHS" ]; then
    fail "inventory paths diverge from app LEGACY_ROUTING_PATHS"
fi

SLUG_TOOL_KEYS=$(
    sed -n '/## 3\. Tool slugs/,/## 4\./p' "$SLUG_DOC" \
        | grep -E '^\| tool \|' | sed -E 's/^\| tool \| ([^ ]+) .*/\1/' | sort
)
[ -n "$SLUG_TOOL_KEYS" ] || fail "no tool slugs found in $SLUG_DOC"

for row in $INV_PATH_DISP; do
    disp=$(printf '%s\n' "$row" | cut -d'|' -f2)
    path=$(printf '%s\n' "$row" | cut -d'|' -f1)
    if [ "$disp" = "301" ]; then
        target=$(grep -E "^\| $path \|" "$LEGACY_DOC" | head -n1 \
            | sed -E 's/^\| \/[^|]+ \| 301 \| \/\{locale\}\/([^ |]+) .*/\1/')
        [ -n "$target" ] || fail "301 path $path has no locale-prefixed canonical target"
        match=$(printf '%s\n' "$SLUG_TOOL_KEYS" | grep -x "$target" || true)
        [ -n "$match" ] || fail "301 target '$target' (from $path) is not a canonical tool slug"
    fi
done

DEFERRED=$(
    sed -n '/export const LEGACY_TOOL_IDS = Object.freeze(\[/,/] as const);/p' "$TOOL_IDS_SRC" \
        | grep -oE '"[a-z0-9-]+"' | tr -d '"' | sort
)
DEFERRED_COUNT=$(printf '%s\n' "$DEFERRED" | wc -l | tr -d ' ')
[ "$DEFERRED_COUNT" -eq 8 ] || fail "app LEGACY_TOOL_IDS has $DEFERRED_COUNT ids, expected 8"

INV_410=$(printf '%s\n' "$INV_PATH_DISP" | grep '|410$' | cut -d'|' -f1 \
    | sed 's#^/##' | sort)
if [ "$INV_410" != "$DEFERRED" ]; then
    fail "410 paths do not match catalog LEGACY_TOOL_IDS"
fi

INV_307=$(printf '%s\n' "$INV_PATH_DISP" | grep '|307$' | cut -d'|' -f1 | sort | tr '\n' ' ')
INV_307=${INV_307% }
EXPECT_307="/faq /privacy"
if [ "$INV_307" != "$EXPECT_307" ]; then
    fail "307 paths are '$INV_307', expected '$EXPECT_307'"
fi

SLUG_COUNT=$(printf '%s\n' "$SLUG_TOOL_KEYS" | wc -l | tr -d ' ')
[ "$SLUG_COUNT" -eq 5 ] || fail "slug table lists $SLUG_COUNT tool slugs, expected 5"

CANONICAL_IDS=$(
    sed -n '/export const TOOL_IDS = Object.freeze(\[/,/] as const);/p' "$TOOL_IDS_SRC" \
        | grep -oE '"[a-z0-9-]+"' | tr -d '"' | sort
)
CANONICAL_COUNT=$(printf '%s\n' "$CANONICAL_IDS" | wc -l | tr -d ' ')
[ "$CANONICAL_COUNT" -eq 5 ] || fail "app TOOL_IDS has $CANONICAL_COUNT ids, expected 5"
if [ "$SLUG_TOOL_KEYS" != "$CANONICAL_IDS" ]; then
    fail "slug table tool slugs diverge from app TOOL_IDS"
fi

printf 'check-seo-inventory: PASS — 15 legacy paths, all dispositions mapped, slug table consistent\n'
