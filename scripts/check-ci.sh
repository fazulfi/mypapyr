#!/bin/sh
#
# check-ci.sh — deterministic CI-without-CD and workflow-integrity guard.
# Exits non-zero on the first failure.
#   a  workflow file exists                 (b/h)  no CD keywords after comment strip
#   c  no pull_request_target               j      no workflow_run
#   d  no secrets mapping/interpolation     e      EVERY uses: is a full-SHA pin
#   f  only ci.yml under .github/workflows  g      dependabot.yml present + valid
#   i  no write scope anywhere              k      every checkout credential-free
#   l  workflow YAML parses (pyyaml)        m      every SHA pin carries `# vX.Y.Z`
#   n  pin truth (scripts/verify-pins.sh)   —      (needs network to api.github.com)
#   o  production API image verification    —      (build + non-root health smoke
#                                                  + Compose render with fixtures)
#
# Check (e) enumerates every `uses:` occurrence in every workflow YAML file
# under .github/workflows/ — not just lines that already look pinned — so an
# unpinned or floating reference (e.g. `uses: actions/foo@v1`) fails the gate
# instead of being silently skipped by the collection regex.

set -eu

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
WF_DIR="$ROOT/.github/workflows"
DEPENDABOT="$ROOT/.github/dependabot.yml"

fail() {
    printf 'check-ci: FAIL — %s\n' "$1" >&2
    exit 1
}

WORKFLOW_FILES=$(find "$WF_DIR" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort || true)
[ -n "$WORKFLOW_FILES" ] || fail "no workflow files under $WF_DIR"

for WF in $WORKFLOW_FILES; do
    # (a) workflow file exists
    [ -f "$WF" ] || fail "workflow absent: $WF"

    if grep -q "$(printf '\r')" "$WF"; then
        fail "workflow contains CRLF line endings: $WF"
    fi

    STRIPPED=$(sed -e 's/[[:space:]]*#.*$//' "$WF")

    # (b)+(h) no-CD guard. Deployment intent is matched SEMANTICALLY, not by
    # substring: structural CD markers are forbidden anywhere in the file,
    # while deployment COMMANDS are forbidden inside `run:` step bodies (the
    # only place they can execute) by the Python check below. A legitimate
    # workspace path such as `${{ github.workspace }}/deploy` in a job `env:`
    # must therefore be expressible literally — `deploy` is not scanned as a
    # bare substring here, so no shell obfuscation is ever needed.
    STRUCTURAL_KEYWORDS='workflow_dispatch|environments:|id-token:|registry-push|registry|publish|docker[[:space:]]+login|docker[[:space:]]+push|docker[[:space:]]+buildx'
    MATCH=$(printf '%s\n' "$STRIPPED" | grep -nE -i "($STRUCTURAL_KEYWORDS)" || true)
    [ -z "$MATCH" ] || fail "forbidden deployment/structural keyword detected in $WF"

    # (c)+(j) privileged triggers
    if grep -qE '^[[:space:]]*pull_request_target[[:space:]]*:' "$WF"; then
        fail "pull_request_target trigger present in $WF"
    fi
    if grep -qE '^[[:space:]]*workflow_run[[:space:]]*:' "$WF"; then
        fail "workflow_run trigger present in $WF"
    fi

    # (d) secrets
    if grep -qE '^[[:space:]]*secrets[[:space:]]*:' "$WF"; then
        fail "secrets mapping present in $WF"
    fi
    if grep -qE '\$\{\{[[:space:]]*secrets\.' "$WF"; then
        fail "secrets interpolation present in $WF"
    fi

    # (i) no write scope (no `key: write` / `permissions: write-all`)
    WRITE_SCOPE=$(grep -nE '^[[:space:]]*[a-zA-Z_-]+:[[:space:]]*(write|write-all)([[:space:]]|$)' "$WF" || true)
    [ -z "$WRITE_SCOPE" ] || fail "write scope present in $WF: $WRITE_SCOPE"

    # (e) every uses: occurrence must be a full 40-hex SHA pin. Collect ALL
    # uses: lines (any reference), then reject any that is not SHA-pinned.
    FILE_USES=$(grep -nE '^[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^[:space:]]+' "$WF" || true)
    [ -n "$FILE_USES" ] || fail "no actions found in $WF"

    BAD_USES=$(printf '%s\n' "$FILE_USES" \
        | grep -vE '^[[:digit:]]+:[[:space:]]*-?[[:space:]]*uses:[[:space:]]*[^@[:space:]]+@[0-9a-f]{40}([[:space:]]|$)' \
        || true)
    [ -z "$BAD_USES" ] || fail "an action is not pinned to a full commit SHA in $WF: $BAD_USES"

    # (m) every SHA pin carries a `# vX.Y.Z` comment (Dependabot requirement)
    BAD_COMMENT=$(printf '%s\n' "$FILE_USES" | grep -vE '@[0-9a-f]{40}[[:space:]]+#[[:space:]]*v[0-9]' || true)
    [ -z "$BAD_COMMENT" ] || fail "a SHA pin lacks its '# vX.Y.Z' comment in $WF: $BAD_COMMENT"

    # (k) every checkout is credential-free
    CHECKOUT_VIOLATION=$(awk '
      /- *uses: *actions\/checkout/ { pending=1; found=0; next }
      pending {
        if ($0 ~ /persist-credentials: *false/) found=1
        if ($0 ~ /^[[:space:]]*-[[:space:]]*uses:/) {
          if (!found) print "line " NR
          pending=0
        }
      }
      END { if (pending && !found) print "end of file" }
    ' "$WF")
    [ -z "$CHECKOUT_VIOLATION" ] || fail "checkout without persist-credentials: false in $WF ($CHECKOUT_VIOLATION)"

    PYTHON=python3
    command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
    command -v "$PYTHON" >/dev/null 2>&1 || fail "python3/python required"
    "$PYTHON" -c 'import yaml' >/dev/null 2>&1 || fail "pyyaml required (python3 -m pip install pyyaml)"

    # (l) workflow YAML parses
    "$PYTHON" -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1], encoding="utf-8"))' "$WF" \
        || fail "workflow YAML does not parse: $WF"

    # (b)+(h) semantic no-CD scan + job-env guard. Deployment COMMANDS are
    # rejected inside `run:` step bodies (the only place they can execute); a
    # legitimate workspace path such as `${{ github.workspace }}/deploy` in an
    # `env:` value is allowed and must not be hidden behind shell obfuscation.
    "$PYTHON" - "$WF" <<'PY' || fail "no-CD semantic guard rejected $WF"
import re
import sys
import yaml

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
workflow = yaml.safe_load(text)

# Structural CD markers may never appear anywhere in the file.
STRUCTURAL = re.compile(
    r"workflow_dispatch|environments:|id-token:|registry|publish|"
    r"docker[ \t]+login|docker[ \t]+push|docker[ \t]+buildx",
    re.IGNORECASE,
)
stripped = re.sub(r"(?m)^[ \t]*#.*$", "", text)
sm = STRUCTURAL.search(stripped)
if sm:
    raise SystemExit("forbidden deployment/structural keyword: " + sm.group(0))

# Deployment commands are forbidden inside run-step bodies only.
RUN_CMD = re.compile(
    r"\b(?:deploy|scp|ssh|rsync|kubectl|helm|aws|gcloud|azure|doctl|"
    r"vercel|netlify|heroku|firebase|fly|render|wrangler|cloudflared|ftp|ghcr)\b",
    re.IGNORECASE,
)
# GitHub Actions expressions use ${{ }}; a literal $( or backtick in an env
# value is shell syntax that the runner sets verbatim and never evaluates.
SHELL_FRAG = re.compile(r"\$\(|`")

for job_name, job in (workflow.get("jobs") or {}).items():
    if not isinstance(job, dict):
        continue
    for key, value in (job.get("env") or {}).items():
        if isinstance(value, str) and SHELL_FRAG.search(value):
            raise SystemExit(
                "%s job env %s holds a shell fragment (%s) — env values are "
                "templated by GitHub Actions, never shell-evaluated"
                % (job_name, key, value)
            )
        if job_name == "qa-production-api" and key == "PAPYR_COMPOSE_DIR":
            if value != "${{ github.workspace }}/deploy":
                raise SystemExit(
                    "qa-production-api PAPYR_COMPOSE_DIR must be the "
                    "GitHub-evaluated '${{ github.workspace }}/deploy' path, got: %s"
                    % value
                )
    for step in job.get("steps") or []:
        if not isinstance(step, dict):
            continue
        body = re.sub(r"(?m)^[ \t]*#.*$", "", str(step.get("run", "")))
        cm = RUN_CMD.search(body)
        if cm:
            raise SystemExit(
                "deployment command %r in run step %r — the no-CD guard is "
                "scoped to commands/run-step semantics"
                % (cm.group(0), step.get("name", ""))
            )
PY
done

# (f) only ci.yml may exist under .github/workflows
EXTRA_WF=$(printf '%s\n' "$WORKFLOW_FILES" | grep -v '/ci\.yml$' || true)
[ -z "$EXTRA_WF" ] || fail "unexpected workflow file(s): $EXTRA_WF"

# (o) Production-image verification must be an ordinary read-only CI job: it
# builds the production Dockerfile, runs it as the image's non-root user with
# a hard capability/rootfs dropout, exercises /health, then renders Compose with
# non-secret fixtures and a digest-form PAPYR_API_IMAGE value. This validates
# deploy wiring without starting deferred services or performing CD work.
"$PYTHON" - "$WF_DIR/ci.yml" <<'PY' || fail "production API image verification contract invalid"
import sys
import yaml

with open(sys.argv[1], encoding="utf-8") as fh:
    workflow = yaml.safe_load(fh)

job = workflow.get("jobs", {}).get("qa-production-api")
if not isinstance(job, dict):
    raise SystemExit("qa-production-api job missing")
if job.get("permissions") != {"contents": "read"}:
    raise SystemExit("qa-production-api must use permissions: contents: read")
steps = job.get("steps", [])
run_text = "\n".join(str(step.get("run", "")) for step in steps if isinstance(step, dict))
required = (
    "docker build",
    "backend/Dockerfile.production",
    "docker run",
    "--cap-drop",
    "--read-only",
    "/health",
    "docker compose",
    "config --quiet",
    "PAPYR_API_IMAGE=",
    "@sha256:",
)
missing = [item for item in required if item not in run_text]
if missing:
    raise SystemExit("qa-production-api missing required markers: " + ", ".join(missing))
# The smoke must run the image in the background with its INHERITED CMD, probe
# /health, and always clean up. A `sh -c` trailing the image replaces CMD
# (uvicorn), so the API never starts; a detached start without a probe or
# cleanup leaves a dead container. Require -d/--detach, an in-container or
# published-port probe, and trap/docker rm -f cleanup.
smoke_step = ""
compose_step = ""
for step in steps:
    if not isinstance(step, dict):
        continue
    r = str(step.get("run", ""))
    if "docker run" in r and "/health" in r:
        smoke_step = r
    if "config --quiet" in r:
        compose_step = r
if not smoke_step:
    raise SystemExit("qa-production-api must run the image and probe /health")
if not compose_step:
    raise SystemExit("qa-production-api missing docker compose config gate")
if "-d" not in smoke_step and "--detach" not in smoke_step:
    raise SystemExit("qa-production-api smoke must start the container in the background (-d/--detach) so the inherited CMD stays the entrypoint")
if "sh -c" in smoke_step:
    raise SystemExit("qa-production-api smoke must NOT override the image CMD with 'sh -c' (the API would never start)")
if "docker exec" not in smoke_step and "--publish" not in smoke_step and " -p " not in smoke_step:
    raise SystemExit("qa-production-api smoke must probe /health inside the running container (docker exec) or via a published port")
if "trap" not in smoke_step and "docker rm -f" not in smoke_step:
    raise SystemExit("qa-production-api smoke must always clean up the container (trap or docker rm -f)")
if "/health" not in smoke_step:
    raise SystemExit("qa-production-api smoke must probe /health")
# PAPYR_API_IMAGE / PAPYR_WORKERS_IMAGE / PAPYR_CLAMD_IMAGE / PAPYR_ENV_FILE
# must ALL be exported as environment variables BEFORE `docker compose ...
# config --quiet`. The compose file gates every image on `${PAPYR_*_IMAGE:?...}`
# (fail-closed), so rendering the model without any one of them aborts.
# Assignments trailing the subcommand are positional arguments that never
# reach Compose. Every image fixture must be digest-form (`@sha256:<64 hex>`).
import re as _re

_compose_lines = compose_step.splitlines()
_cfg = next((i for i, ln in enumerate(_compose_lines) if "config --quiet" in ln), -1)
if _cfg < 0:
    raise SystemExit("qa-production-api docker compose gate missing config --quiet")
_before = "\n".join(_compose_lines[:_cfg])
_after = "\n".join(_compose_lines[_cfg + 1 :])
_required_env = ("PAPYR_API_IMAGE=", "PAPYR_WORKERS_IMAGE=", "PAPYR_CLAMD_IMAGE=", "PAPYR_ENV_FILE=")
_missing_env = [name for name in _required_env if name not in _before]
if _missing_env:
    raise SystemExit(
        "qa-production-api must export %s BEFORE docker compose config --quiet"
        % ", ".join(_required_env)
    )
for name in ("PAPYR_API_IMAGE=", "PAPYR_WORKERS_IMAGE=", "PAPYR_CLAMD_IMAGE="):
    if not _re.search(name + r"\S*@sha256:[0-9a-f]{64}", _before):
        raise SystemExit(
            "qa-production-api %s must be a non-secret digest-form fixture (@sha256:<64 hex>)"
            % name.rstrip("=")
        )
if "PAPYR_" in _compose_lines[_cfg] or "PAPYR_" in _after:
    raise SystemExit("qa-production-api compose env assignments must not trail the config --quiet subcommand")
if "secrets" in run_text.lower() or "docker push" in run_text.lower():
    raise SystemExit("qa-production-api must not use secrets or push images")
PY

# (g) dependabot config present, parses, and covers the repo ecosystems
[ -f "$DEPENDABOT" ] || fail "dependabot config absent: $DEPENDABOT"
"$PYTHON" -c '
import sys, yaml
with open(sys.argv[1], encoding="utf-8") as fh:
    cfg = yaml.safe_load(fh)
pairs = [(u.get("package-ecosystem"), u.get("directory")) for u in cfg.get("updates", [])]
required = [("github-actions", "/"), ("npm", "/frontend"), ("npm", "/qa-tools"), ("pip", "/backend")]
missing = ["%s@%s" % (e, d) for e, d in required if (e, d) not in pairs]
if missing:
    print("missing dependabot entries: " + ", ".join(missing), file=sys.stderr)
    sys.exit(1)
' "$DEPENDABOT" || fail "dependabot config invalid"

# (n) pin truth (network to api.github.com required)
"$ROOT/scripts/verify-pins.sh" || fail "pin truth verification failed"

printf 'check-ci: PASS\n'
