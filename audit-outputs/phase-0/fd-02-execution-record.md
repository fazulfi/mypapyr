# FD-02 Execution Record — Backend workspace scaffold

## Skills loaded

- **ocs-delegation-gate** — applied before any non-trivial delegation. This task is single-agent (no subagent delegation); loaded skill's prompt-contract pattern is reflected in this record (skills + verification evidence explicit).
- **context-grooming** — kept the record tight: one decision log, one evidence block, no stale threads.
- **git-master** — verified legacy invariant with `git status --porcelain` and `git rev-parse HEAD` before/after.

No UI/UX work, no Cloudflare/Durable Objects work, no release work. Optional skills (impeccable-style, ocs-release-integrity, ocs-runtime-validation, ocs-openai-multi-account) deliberately not loaded — outside scope.

## Scope-discipline statement

This unit delivered only what FD-02 contract requires: a minimal FastAPI shell with `/health -> {"status":"ok"}`, pytest + ruff passing, no Dockerfile, no docker-compose, no deploy artifacts, no routers, no DB, no auth, no PDF tools, no middleware, no logging framework. All such concerns belong to later units (FD-03 deploy, SEC-04 secrets, etc.). Confirmed by `find backend -type f -not -path '*/.venv/*' -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' -not -path '*/.ruff_cache/*'` returning exactly the 7 mandated files.

## Python interpreter (used, not assumed)

- Version: `Python 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`
- Executable: `C:\Python314\python.exe` (system interpreter used to bootstrap venv)
- Venv interpreter: `<workspace-root>\backend\.venv\Scripts\python.exe` (Windows Git-Bash path: `backend/.venv/Scripts/python.exe`)
- Platform: `Windows-11-10.0.26100-SP0`, win32
- All wheel compatibility resolved natively on 3.14.3 — no fallback needed. Recorded below.

## Non-interactive environment

Every Bash call exported:

```
CI=true PIP_NO_INPUT=1 GIT_TERMINAL_PROMPT=0 GIT_PAGER=cat PAGER=cat PYTHONDONTWRITEBYTECODE=1
```

No interactive prompts encountered; pip install ran unattended.

---

## RED step — fail-first contract

### Test written first (`backend/tests/test_health.py`, 295 bytes)

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

This file was created BEFORE `app/main.py`, `app/__init__.py`, or any dependency install that pulls `fastapi`.

### Venv bootstrap commands (RED-only deps installed: pytest, httpx)

```bash
cd <workspace-root>/backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade pip     # -> pip 26.2
.venv/Scripts/python.exe -m pip install pytest httpx     # NO fastapi yet
```

Resolved at RED step (no app deps present):

- pytest 9.1.1
- httpx 0.28.1 (with h11, anyio, certifi, idna, httpcore, pluggy, pygments, iniconfig, packaging)

### RED pytest run — exact command + captured output

Command:

```
.venv/Scripts/python.exe -m pytest tests/test_health.py -v
```

Output (verbatim):

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0 -- <workspace-root>\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: <workspace-root>\backend
plugins: anyio-4.14.2
collecting ... collected 0 items / 1 error

=================================== ERRORS ====================================
____________________ ERROR collecting tests/test_health.py ____________________
ImportError while importing test module '<workspace-root>\backend\tests\test_health.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Python314\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_health.py:3: in <module>
    from fastapi.testclient import TestClient
E   ModuleNotFoundError: No module named 'fastapi'
=========================== short test summary info ============================
ERROR tests/test_health.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 0.41s ===============================
```

RED proven: collection fails before app code even has a chance to load — proving the test cannot pass without a real `app.main:app`.

---

## GREEN step — minimal scaffold

### 7 files created (with byte sizes)

| # | Path | Bytes |
|---|------|-------|
| 1 | `backend/requirements.txt` | 42 |
| 2 | `backend/requirements-dev.txt` | 60 |
| 3 | `backend/ruff.toml` | 169 |
| 4 | `backend/pytest.ini` | 54 |
| 5 | `backend/app/__init__.py` | 0 |
| 6 | `backend/app/main.py` | 206 |
| 7 | `backend/tests/test_health.py` | 295 (from RED) |

`backend/tests/__init__.py` intentionally NOT created. `pytest.ini` `pythonpath = .` already resolves the `app` package from `backend/`, and `tests/` discovery uses pytest's rootdir-based conftest-less mode. Documented choice per MUST DO B.7.

### File contents (verbatim)

#### `backend/requirements.txt`

```
fastapi==0.123.5
uvicorn[standard]==0.39.0
```

#### `backend/requirements-dev.txt`

```
-r requirements.txt
pytest==9.1.1
httpx==0.28.1
ruff==0.14.4
```

#### `backend/ruff.toml`

```toml
line-length = 100
target-version = "py314"

[lint]
select = ["E", "F", "I", "UP", "B", "SIM", "PL", "RUF"]

[lint.per-file-ignores]
"tests/**/*.py" = ["PLR2004", "S101"]
```

Note: `target-version = "py314"` chosen because the local interpreter is 3.14.3 and all wheels (including ruff 0.14.4) install cleanly. No rule disabled without justification: `PLR2004` (magic numbers in tests) and `S101` (`assert` in tests) suppressed only inside `tests/**/*.py` because pytest patterns require them — every suppression is intentional and per-file-scoped.

#### `backend/pytest.ini`

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts = -q
```

`pythonpath = .` makes `from app.main import app` resolvable from `backend/` regardless of how pytest is invoked. `testpaths = tests` confines collection. `addopts = -q` matches contract evidence format.

#### `backend/app/__init__.py`

Empty file (0 bytes). Required for `app/` to be an importable package on Python 3.14.

#### `backend/app/main.py`

```python
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="papyr-backend", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

Fully typed (`dict[str, str]`), no DB, no routers, no middleware, no logging framework — minimal shell only, per MUST NOT DO.

#### `backend/tests/test_health.py`

(verbatim above; 295 bytes; from RED step.)

### Install full dev deps — exact command + resolved versions

Command:

```bash
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
```

Output tail:

```
Downloaded 6 packages
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 click-8.4.2 fastapi-0.123.5 httptools-0.8.0 pydantic-2.13.4 pydantic-core-2.46.4 python-dotenv-1.2.2 pyyaml-6.0.3 ruff-0.14.4 starlette-0.50.0 typing-extensions-4.16.0 typing-inspection-0.4.2 uvicorn-0.39.0 watchfiles-1.2.0 websockets-17.0.1
```

`pip freeze | grep -Ei 'fastapi|uvicorn|pytest|httpx|ruff|starlette|pydantic'` (with anyio, httptools, watchfiles, websockets, click included for completeness):

```
anyio==4.14.2
click==8.4.2
fastapi==0.123.5
httptools==0.8.0
httpx==0.28.1
pydantic==2.13.4
pydantic_core==2.46.4
pytest==9.1.1
ruff==0.14.4
starlette==0.50.0
uvicorn==0.39.0
watchfiles==1.2.0
websockets==17.0.1
```

All wheels compatible with Python 3.14.3 (no fallback used; no faked PASS).

### GREEN pytest run — exact command + captured output

Command:

```
.venv/Scripts/python.exe -m pytest tests/ -v
```

Output (verbatim):

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: <workspace-root>\backend
configfile: pytest.ini
plugins: anyio-4.14.2
collected 1 item

tests\test_health.py .                                                   [100%]

============================== 1 passed in 0.71s ===============================
```

PASS — `1 passed in 0.71s`. `configfile: pytest.ini` proves the contract is being honored.

### GREEN ruff check — exact command + captured output

Command:

```
.venv/Scripts/python.exe -m ruff check .
```

Output (verbatim):

```
All checks passed!
```

PASS — no warnings, no fixes applied. `line-length = 100`, `select = E/F/I/UP/B/SIM/PL/RUF` all clean.

### `/health` runtime proof (via TestClient)

Command:

```
.venv/Scripts/python.exe -c "
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
r = client.get('/health')
print('status:', r.status_code)
print('json:', r.json())
assert r.status_code == 200
assert r.json() == {'status': 'ok'}
print('PROOF: /health -> 200', r.json())
"
```

Output (verbatim):

```
status: 200
json: {'status': 'ok'}
PROOF: /health -> 200 {'status': 'ok'}
```

Status 200, body `{"status":"ok"}` — exact contract match.

---

## Legacy invariant — papyr-reference untouched (proof)

### BEFORE

```
$ git -C ../papyr-reference status --porcelain
(empty)
$ git -C ../papyr-reference rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
```

### AFTER

```
$ git -C ../papyr-reference status --porcelain
(empty)
$ git -C ../papyr-reference rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
```

`papyr-reference/` working tree clean and HEAD pinned to the expected SHA before, during, and after this unit. No files added, modified, formatted, or installed inside it.

---

## MUST NOT DO compliance check

| Prohibition | Status |
|---|---|
| No Dockerfile / Dockerfile.production / docker-compose / deploy artifacts | PASS — none created; only the 7 mandated files exist on disk |
| No legacy backend modules / business logic | PASS — `app/main.py` is a 5-line minimal shell |
| No routers, DB models, Alembic, auth, PDF tools | PASS — none present |
| No modification/format/install into `papyr-reference/` | PASS — porcelain empty, HEAD unchanged (above) |
| No read/print/reference of `<workspace-root>\.env.papyr` | PASS — file never opened; no secret values in this record |
| No git add/commit/push/init | PASS — files left untracked; root `.gitignore` already excludes `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/` |
| No `# type: ignore`, bare `except:`, or empty except blocks | PASS — none used; `main.py` has full `dict[str, str]` annotation |
| No chat-only completion claim | PASS — this file is the deliverable |

---

## Uncertainties / open items

- `pydantic-core 2.46.4` and `pydantic 2.13.4` are pulled transitively by `fastapi 0.123.5`. Versions locked by FastAPI's pin and verified compatible with Python 3.14 wheels. No manual override needed.
- `uvicorn[standard]` extra pulled `httptools 0.8.0`, `watchfiles 1.2.0`, `websockets 17.0.1`, `click 8.4.2`, `python-dotenv 1.2.2`, `pyyaml 6.0.3` — all expected from the standard extras group.
- `backend/tests/__init__.py` was deliberately not created per MUST DO B.7 ("OR rely on pytest.ini pythonpath; document choice"). This choice is recorded above. If a later unit prefers package-mode tests, adding an empty `tests/__init__.py` is a one-line change.
- Ruff `target-version = "py314"` is supported by ruff 0.14.4; if a future ruff release drops py314 support, the pin needs to track.
- No benchmark, no test coverage tool, no CI config were added — out of scope for FD-02.

---

## Reproducibility block (for parent re-verification)

```bash
# Python (system)
python --version                                 # Python 3.14.3

# Navigate
cd <workspace-root>/backend

# (Venv already exists from this run; rebuild from scratch if needed)
# python -m venv .venv
# .venv/Scripts/python.exe -m pip install --upgrade pip
# .venv/Scripts/python.exe -m pip install -r requirements-dev.txt

# Re-run contract evidence
.venv/Scripts/python.exe -m pytest tests/ -v
.venv/Scripts/python.exe -m ruff check .

# Re-verify /health via TestClient
.venv/Scripts/python.exe -c "
from fastapi.testclient import TestClient
from app.main import app
r = TestClient(app).get('/health')
assert r.status_code == 200 and r.json() == {'status': 'ok'}
print(r.status_code, r.json())
"

# Re-verify legacy invariant (must remain clean + HEAD unchanged)
cd ../papyr-reference && git status --porcelain && git rev-parse HEAD
# expected: empty porcelain + 981c59a171f4b83c9e2afcecc6e934bee14a3a5e
```

Venv activation path for Windows Git-Bash: `backend/.venv/Scripts/python.exe` (already shown above).

---

## Deliverable file metadata

- Path: `<workspace-root>\audit-outputs\phase-0\fd-02-execution-record.md`
- Self-verified via `filesystem_get_file_info` (line count and byte size reported in chat reply).