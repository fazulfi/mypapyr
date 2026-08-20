#!/bin/sh
#
# test-check-seo-inventory.sh — focused offline regression for
# scripts/check-seo-inventory.sh (TDD red/green proof).
#
# Proves the SEO-01 guard fails closed on each injected defect and passes on a
# correct inventory, using a temporary fixture (no network, no mutation of the
# real tree):
#   1. Consistency:  the guard PASS-es on the real repository inventory.
#   2. Missing disposition:  a removed legacy row ==> fail.
#   3. Undefined disposition:  a bogus status code ==> fail.
#   4. Code drift:  an extra path in i18n LEGACY_ROUTING_PATHS ==> fail.
#   5. Unmapped mechanism:  a 301 target absent from the slug table ==> fail.

set -eu

fail() {
    printf 'test-check-seo-inventory: FAIL — %s\n' "$1" >&2
    exit 1
}

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
GUARD="$ROOT/scripts/check-seo-inventory.sh"
[ -f "$GUARD" ] || fail "check-seo-inventory.sh absent: $GUARD"

FIXTURE=$(mktemp -d) || fail "cannot create temp fixture"
trap 'rm -rf "$FIXTURE"' EXIT HUP INT TERM

# Seed the fixture with the real artifacts so mutations are minimal diffs.
mkdir -p "$FIXTURE/docs/seo" "$FIXTURE/frontend/src/lib"
cp "$ROOT/docs/seo/legacy-url-inventory.md" "$FIXTURE/docs/seo/"
cp "$ROOT/docs/seo/slug-table.md" "$FIXTURE/docs/seo/"
cp "$ROOT/frontend/src/lib/i18n.ts" "$FIXTURE/frontend/src/lib/"
cp "$ROOT/frontend/src/lib/tool-ids.ts" "$FIXTURE/frontend/src/lib/"

run_guard() {
    sh "$GUARD" "$FIXTURE"
}

printf '=== 1. consistency: real inventory passes ===\n'
run_guard >/dev/null 2>&1 || fail "guard rejected a consistent inventory"
printf 'PASS — consistent inventory accepted\n'

printf '=== 2. missing disposition (row removed) fails closed ===\n'
# Remove the /watermark row entirely -> 14 rows, guard must reject.
grep -v '^| /watermark | ' "$FIXTURE/docs/seo/legacy-url-inventory.md" \
    > "$FIXTURE/docs/seo/legacy-url-inventory.md.new"
mv "$FIXTURE/docs/seo/legacy-url-inventory.md.new" "$FIXTURE/docs/seo/legacy-url-inventory.md"
if run_guard >/dev/null 2>&1; then
    fail "missing disposition was NOT rejected (guard exited 0)"
fi
printf 'PASS — missing disposition rejected\n'

printf '=== 3. undefined disposition (bogus status) fails closed ===\n'
cat > "$FIXTURE/docs/seo/legacy-url-inventory.md" <<'DOC'
# SEO — Legacy URL Inventory & Disposition

| Legacy path | Disposition | Target / mechanism | Notes |
| --- | --- | --- | --- |
| /compress | 301 | /{locale}/compress-pdf | single-hop to localized canonical |
| /merge | 301 | /{locale}/merge-pdf | single-hop to localized canonical |
| /split | 301 | /{locale}/split-pdf | single-hop to localized canonical |
| /image-to-pdf | 301 | /{locale}/jpg-to-pdf | single-hop to localized canonical |
| /pdf-to-image | 301 | /{locale}/pdf-to-jpg | single-hop to localized canonical |
| /rotate | 410 | MECH_410 | retired tool; localized 410 Gone |
| /protect | 410 | MECH_410 | retired tool; localized 410 Gone |
| /unlock | 410 | MECH_410 | retired tool; localized 410 Gone |
| /watermark | 999 | MECH_410 | bogus disposition |
| /sign | 410 | MECH_410 | retired tool; localized 410 Gone |
| /pdf-to-word | 410 | MECH_410 | retired tool; localized 410 Gone |
| /ocr | 410 | MECH_410 | retired tool; localized 410 Gone |
| /pdf-to-excel | 410 | MECH_410 | retired tool; localized 410 Gone |
| /faq | 307 | /{locale}/faq | locale-less supporting (DEC-047) |
| /privacy | 307 | /{locale}/privacy | locale-less supporting (DEC-047) |
DOC
if run_guard >/dev/null 2>&1; then
    fail "undefined disposition was NOT rejected (guard exited 0)"
fi
printf 'PASS — undefined disposition rejected\n'

printf '=== 4. code drift (extra legacy path) fails closed ===\n'
# Restore the canonical inventory, then add an extra path to i18n SRC -> 16.
cp "$ROOT/docs/seo/legacy-url-inventory.md" "$FIXTURE/docs/seo/"
sed 's#"/compress",#"/compress",#; /"\/compress",/a\  "/compress-pdf",' \
    "$ROOT/frontend/src/lib/i18n.ts" > "$FIXTURE/frontend/src/lib/i18n.ts"
if [ "$(grep -c '^  "/' "$FIXTURE/frontend/src/lib/i18n.ts")" -ne 16 ]; then
    fail "fixture i18n mutation did not add a 16th legacy path"
fi
if run_guard >/dev/null 2>&1; then
    fail "code drift (extra legacy path) was NOT rejected"
fi
printf 'PASS — code drift rejected\n'

printf '=== 5. unmapped mechanism (301 target absent from slug table) fails closed ===\n'
cp "$ROOT/docs/seo/legacy-url-inventory.md" "$FIXTURE/docs/seo/"
cp "$ROOT/frontend/src/lib/i18n.ts" "$FIXTURE/frontend/src/lib/"
# Point /compress at a non-canonical slug; guard must fail the slug-table check.
sed 's#| /compress | 301 | /{locale}/compress-pdf |#| /compress | 301 | /{locale}/compress-pdff |#' \
    "$FIXTURE/docs/seo/legacy-url-inventory.md" > "$FIXTURE/docs/seo/legacy-url-inventory.md.new"
mv "$FIXTURE/docs/seo/legacy-url-inventory.md.new" "$FIXTURE/docs/seo/legacy-url-inventory.md"
if run_guard >/dev/null 2>&1; then
    fail "unmapped 301 mechanism was NOT rejected (guard exited 0)"
fi
printf 'PASS — unmapped 301 mechanism rejected\n'

printf 'test-check-seo-inventory: PASS — consistency, missing/undefined disposition, drift, and unmapped-mechanism contracts hold\n'
