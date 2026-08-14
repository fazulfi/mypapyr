#!/bin/sh
#
# check-r2-lifecycle.sh — deterministic lifecycle gate (U-R2; ARC-06, PE-03).
#
# Self-contained validation of deploy/r2-lifecycle.json against the approved
# R2 lifecycle contract. Uses only system python3 + json module (stdlib).
# No network access; no secrets.
#
# Exit codes: 0 = exact match, 1 = drift or secret-like material,
#             2 = artifact absent, malformed JSON, or invalid schema.
#
# For deploy-time application (out-of-band, manual operator action):
#   wrangler r2 bucket lifecycle set <BUCKET_NAME> --file deploy/r2-lifecycle.json

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
PATH_LIFECYCLE="$ROOT/deploy/r2-lifecycle.json"
PYTHON=python

command -v "$PYTHON" >/dev/null 2>&1 || { printf 'check-r2-lifecycle: FAIL — python required\n'; exit 2; }
"$PYTHON" -c 'import json' >/dev/null 2>&1 || { printf 'check-r2-lifecycle: FAIL — json module unavailable\n'; exit 2; }

exec "$PYTHON" -c "
import json, sys, os

_EXPECTED_TMP_RULE_ID = 'papyr-tmp-objects-expire-r2-minimum-1-day-safety-net'
_EXPECTED_MULTIPART_RULE_ID = 'papyr-abort-incomplete-multipart-r2-minimum-1-day'

EXPECTED = {
    'RetentionContract': {
        'HardMaximumSeconds': 3600,
        'Enforcement': 'application-cleanup',
        'LifecycleSafetyNet': 'r2-minimum-one-day-expiration',
    },
    'Rules': [
        {
            'ID': _EXPECTED_TMP_RULE_ID,
            'Status': 'Enabled',
            'Filter': {'Prefix': 'tmp/'},
            'Expiration': {'Days': 1},
        },
        {
            'ID': _EXPECTED_MULTIPART_RULE_ID,
            'Status': 'Enabled',
            'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 1},
        },
    ],
}

_SECRET_MARKERS = ('secret', 'token', 'password', 'passwd', 'accesskey', 'account', 'akia', 'privatekey', 'credential')

path = sys.argv[1]
try:
    with open(path, encoding='utf-8') as f:
        raw = f.read()
except OSError:
    print(json.dumps({'status': 'absent', 'error': 'lifecycle artifact absent or unreadable'}))
    sys.exit(2)

try:
    doc = json.loads(raw)
except ValueError:
    print(json.dumps({'status': 'malformed', 'error': 'lifecycle artifact is not valid JSON'}))
    sys.exit(2)

if not isinstance(doc, dict):
    print(json.dumps({'status': 'malformed', 'error': 'lifecycle artifact must be a JSON object'}))
    sys.exit(2)

# Scan for secret-like keys
def _normalize(name):
    lowered = name.lower()
    for sep in ('_', '-', ' ', '.'):
        lowered = lowered.replace(sep, '')
    return lowered

findings = []
def scan(value, prefix=''):
    if isinstance(value, dict):
        for k, v in value.items():
            child = f'{prefix}.{k}' if prefix else str(k)
            if isinstance(k, str) and any(m in _normalize(k) for m in _SECRET_MARKERS):
                findings.append(child)
            scan(v, child)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            scan(v, f'{prefix}[{i}]')

scan(doc)
if findings:
    print(json.dumps({'status': 'secret_material', 'error': f'lifecycle artifact carries secret/identity material at {len(findings)} path(s)'}))
    sys.exit(1)

# Compare top-level fields
drift = []
for key in EXPECTED:
    if key == 'Rules':
        continue
    if key not in doc:
        drift.append({'kind': 'missing_field', 'path': key, 'expected': EXPECTED[key], 'actual': None})
    elif EXPECTED[key] != doc[key]:
        drift.append({'kind': 'value_mismatch', 'path': key, 'expected': EXPECTED[key], 'actual': doc[key]})

for key in doc:
    if key not in EXPECTED:
        drift.append({'kind': 'unexpected_field', 'path': key, 'expected': None, 'actual': doc[key]})

# Compare rules
actual_rules = doc.get('Rules')
if actual_rules is None:
    drift.append({'kind': 'missing_field', 'path': 'Rules', 'expected': EXPECTED['Rules'], 'actual': None})
elif not isinstance(actual_rules, list):
    drift.append({'kind': 'value_mismatch', 'path': 'Rules', 'expected': 'a list of rules', 'actual': type(actual_rules).__name__})
else:
    expected_by_id = {r['ID']: r for r in EXPECTED['Rules']}
    actual_by_id = {}
    for idx, rule in enumerate(actual_rules):
        if not isinstance(rule, dict):
            drift.append({'kind': 'value_mismatch', 'path': f'Rules[{idx}]', 'expected': 'an object', 'actual': type(rule).__name__})
            continue
        rid = rule.get('ID')
        if rid in actual_by_id:
            drift.append({'kind': 'unexpected_rule', 'path': f'Rules[{idx}]', 'expected': None, 'actual': f'duplicate ID {rid!r}'})
            continue
        actual_by_id[rid] = rule

    for rid, exp in expected_by_id.items():
        if rid not in actual_by_id:
            drift.append({'kind': 'missing_rule', 'path': f'Rules[ID={rid!r}]', 'expected': exp, 'actual': None})
            continue
        def compare_val(e, a, p):
            res = []
            if isinstance(e, dict) and isinstance(a, dict):
                for ek in e:
                    cp = f'{p}.{ek}' if p else ek
                    if ek not in a:
                        res.append({'kind': 'missing_field', 'path': cp, 'expected': e[ek], 'actual': None})
                    else:
                        res.extend(compare_val(e[ek], a[ek], cp))
                for ak in a:
                    if ak not in e:
                        res.append({'kind': 'unexpected_field', 'path': f'{p}.{ak}' if p else ak, 'expected': None, 'actual': a[ak]})
            elif e != a:
                res.append({'kind': 'value_mismatch', 'path': p, 'expected': e, 'actual': a})
            return res
        drift.extend(compare_val(exp, actual_by_id[rid], f'Rules[ID={rid!r}]'))

    for rid in actual_by_id:
        if rid not in expected_by_id:
            drift.append({'kind': 'unexpected_rule', 'path': f'Rules[ID={rid!r}]', 'expected': None, 'actual': actual_by_id[rid]})

if drift:
    print(json.dumps({'status': 'drift', 'findings': drift}, default=str))
    sys.exit(1)

print(json.dumps({'status': 'match'}))
sys.exit(0)
" "$PATH_LIFECYCLE"