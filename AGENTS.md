# Repository Guidelines

## Project Overview

**Papyr** — browser-first anonymous PDF utility platform: Compress, Merge, Split, JPG-to-PDF, PDF-to-JPG. No accounts, no cloud history, trilingual (EN/ES/ID). Privacy-first and fail-closed by design: minimal metadata, never log filenames/object keys/signed URLs (DEC-174/175), opaque R2 object keys.

- Frontend: Next.js 16 / React 19 / TS 6 / Tailwind v4 (Vercel target)
- Backend: FastAPI 0.141 / Python 3.13 control plane (nginx/VPS)
- Queue: Redis Streams (`jobs` stream, `workers` group) + separate worker process
- Storage: Cloudflare R2 (temp objects, 3600 s retention + cleanup + 1-day lifecycle rule)

Reality vs spec: the five tools and the Phase 6 privacy/analytics/advertising/support baseline are implemented, tested, merged to `main` (PR #24), and deployed to production on 2026-08-15 (release 1767ca8); the Phase 6 enterprise completion (PT-04 merge-password wiring, ad-placement E2E, SEO, and documentation reconciliation) is merged via PR #46 and deployed as backend release p6-complete-1786951216 and frontend release p6-ads-all-1786954951 (2026-08-17). Phase 9 (legal revision with version footers, 15-article trilingual MDX blog, sitemap expansion to 57 URLs, content CI gates) is implemented on branch `feat/full-p9-content-legal-blog` (PR #49, head `da6e94e`) and deployed to the VPS frontend as release `p9-da6e94e` (BUILD_ID `2nIWv0nNRIdkFQbh92Ueh`) on 2026-08-21, pending merge to `main`. Frontend tool pages exist for all five tools (compress, merge, split, jpg-to-pdf, pdf-to-jpg); the backend mounts 9 versioned routers (`status`, `capabilities`, `compress`, `image_to_pdf`, `merge`, `pdf_to_jpg`, `split`, `support`, `download`) plus health routes; the worker entrypoint exists (`worker/__main__.py` + `entrypoint.py`); `frontend/src/proxy.ts` follows the Next.js 16 proxy-file convention for locale routing. Remaining gaps below — check before touching tool code.

## Architecture & Data Flow

```text
Browser → Next.js ([locale] segment, same-origin /api/v1, rewritten via next.config.ts to the backend origin)
        → FastAPI control plane (backend/app)
            1. POST /api/v1/tools/{tool}/tasks (multipart) → validate (BE-02) → sanitize (SEC-02) → R2 upload → Redis Streams enqueue → 202 TaskAdmission
            2. Worker: XREADGROUP claim → TaskStore CAS queued→processing → spawn-subprocess engine → upload outputs → RESULT_UPLOADED → XACK
            3. Client polls GET .../status → GET .../download/{output} → presigned URL (≤300 s) → R2 fetch
```

- **Control plane only admits jobs**; engines (pikepdf, Ghostscript, img2pdf/Pillow, pypdfium2) run in worker child processes. API image installs only pikepdf (sanitizer).
- **State machine** (`app/tasks/state_machine.py`, pure): `queued → processing → done|failed|cancelled`; `expired` is a TTL lifecycle outcome, not a state. Enforced by `TaskStore.transition_state` CAS (WATCH/MULTI/EXEC).
- **Queue**: custom Redis Streams — atomic Lua check-and-XADD admission (2000 cap, 900 s oldest-wait), XAUTOCLAIM stale-claim recovery, at-most-once fair-use release (4 concurrent/origin). Not Celery/RQ.
- **Errors**: envelope `{error:{code,category,message,messageKey,retryable}, request_id}`; domain errors are typed `RuntimeError` subclasses mapped to `HTTPException(detail={"messageKey": ...})` — never rendered, 500s never leak payloads.
- **DI**: no global singletons. `create_app(settings=None)` factory (single wiring seam); routers resolve `app.state` presets (`task_store`, `r2_client`, `job_queue`) lazily per-request via `_resolve_*` helpers, falling back to env. Tests inject via `app.state` + constructor `client=`/`clock=` seams.

## Key Directories

| Path | Purpose |
| --- | --- |
| `backend/app/main.py` | App factory `create_app()`; module-level `app` for uvicorn; sole router/DI owner |
| `backend/app/routers/` | Per-tool admission routers (`compress.py`, `merge.py`, `split.py`, `image_to_pdf.py`, `pdf_to_jpg.py`), `status.py`, `download.py`, `capabilities.py`, `support.py` |
| `backend/app/services/` | Engines + worker executors (`split_service`, `compress_service`, `merge_service` (engine only), `image_to_pdf_service`, `pdf_to_jpg_service`) |
| `backend/app/worker/` | `JobWorker.run_once()`, `SubprocessJobRunner` (spawn + SIGTERM/SIGKILL), protocols, `__main__.py` + `entrypoint.py` |
| `backend/app/queue/` | `TaskStore` (Redis hash, CAS), `JobQueue` (Streams), `AdmissionPolicy` contracts |
| `backend/app/tasks/` | `state_machine.py` (pure transitions), `cleanup.py` (`CleanupCoordinator`) |
| `backend/app/security/` | `validation.py` (BE-02), `sanitize.py` (SEC-02 pikepdf), `classification.py`, `fair_use.py` (BE-10), `middleware.py` (CORS+headers) |
| `backend/app/utils/` | `r2.py` (R2Client, opaque keys), `logging.py` (JSON privacy logger) |
| `backend/tests/` | 60 pytest modules + conftest; see Testing & QA |
| `frontend/src/app/[locale]/` | Routes: home, `compress-pdf`, `merge-pdf`, `split-pdf`, `jpg-to-pdf`, `pdf-to-jpg`, `[locale]/blog` listing and `[locale]/blog/[slug]` articles, 7 supporting pages, `tool-unavailable` |
| `frontend/content/blog/` | Pure-MDX blog bodies and typed manifest for 15 localized articles (5 topics × 3 locales) |
| `frontend/src/lib/` | i18n, messages, catalog, tool-ids, taskPolling, toolState, naming, blog, zip (fflate), design-tokens |
| `frontend/src/components/` | Navbar, Footer, SkipLink, LogoLockup, LanguageSwitcher, `uploader/Dropzone`, `states/*` cards, legal page/version-footer components, `supporting-page` |
| `frontend/e2e/` | Playwright specs (support-routes, not-found-contrast-favicon, locale-routing, a11y-shell, catalog-routes, rich-ui, mobile-ui, tool flows, ad-behavior, blog) |
| `deploy/` | `docker-compose.yml` (4 services), hardened nginx server block, r2-lifecycle.json, runbook-vps.md |
| `scripts/` | POSIX CI guards: `check-ci.sh` (no-CD), `verify-pins.sh`, `check-compose.sh`, `check-r2-lifecycle.sh`, `test-check-ci.sh`, `test-verify-pins.sh` |
| `docs/specifications/` | `product.md` + `architecture.md` — target-behavior authority (source+tests = current reality) |
| `qa-tools/` | markdownlint-cli2 0.23.2 pinned via committed lockfile |

## Development Commands

Backend (from `backend/`, Python 3.13+; Windows → use Git-Bash/WSL for shell scripts):

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows; POSIX: source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload                      # http://localhost:8000/health, /health/ready
pytest                                            # fast, -q (no coverage)
pytest tests/ --cov=app --cov-fail-under=80        # coverage gate (80% floor = NFR-03)
pytest tests/test_worker.py::test_name -q          # single test
REDIS_URL=redis://localhost:6379/15 pytest tests/test_integration_redis.py  # opt-in real Redis
ruff check . && ruff format --check .
python -m mypy app tests --strict --no-incremental
```

Frontend (from `frontend/`, Node 24+):

```bash
npm ci
npm run dev                                        # localhost:3000
npm test                                           # vitest run
npm run test:coverage                              # thresholds: lines 80 / funcs 80 / branches 80 / stmts 80
npm run test:e2e                                   # Playwright; builds+serves locally, start-only in CI
npm run lint && npm run format:check && npm run typecheck && npm run build
```

Repo guard (root): `bash scripts/check-ci.sh` (requires network for pin truth; CRLF rejected).

## Code Conventions & Common Patterns

### Backend

- `create_app()` factory is the only integration owner; routers never self-wire (`routers/__init__.py` intentionally empty). Add a router in `main.py`, not imports.
- Naming: `snake_case.py` modules, `PascalCase` classes, router module-level `router = APIRouter(prefix=..., tags=[...])`; private helpers `_resolve_*`/`_build_*`. `from __future__ import annotations` + `__all__` everywhere.
- Types: strict typing (mypy strict in CI); `StrEnum` for closed vocabularies; frozen dataclasses for records/Settings; pydantic v2 `extra="forbid"`; `Protocol` seams (`RedisLike`, `S3Client`, `JobExecutor`, `JobRunner`); `cast()` only at untyped redis/boto3 crossing points.
- Errors: define typed `RuntimeError` subclasses per domain with `retryable`/`failure_code` attrs; routers map them; never raise `HTTPException` with user content in `detail`.
- Settings: frozen `Settings` dataclass via `from_env()`; 5 required vars (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `ALLOWED_ORIGINS`) — missing ones fail fast. Never commit dotfiles.
- Logging: `extra={"fields": {...}}` with class names/counts only — never filenames, task ids, keys, payloads.
- Docstrings cite architecture contracts (BE-xx, DEC-xxx, TL-xx, R-xx) — preserve that style.
- Pins: exact `==` in requirements; digest-pinned base images; SHA-pinned actions with `# vX.Y.Z`; never weaken CI.

### Frontend

- App Router with dynamic `[locale]` root segment (EN default; `papyr_locale` cookie). i18n is **hand-rolled** via `src/lib/i18n.ts` + `messages.ts` (`getMessages(locale)`) — `next-intl` is installed but inert; don't add next-intl APIs.
- `'use client'` only on interactive leaves: tool pages, Navbar, Dropzone, 5 state cards, `useTaskPolling`. Everything else stays a server component (async `params: Promise<...>` + `await params` / client `use(params)`).
- Data flow: per-page `useState` (no global store) → POST FormData → `useTaskPolling` (2 s interval, sessionStorage `papyr:task:{toolId}` resume) → state card → download grant → `window.location.href`. Copy the `compress-pdf/page.tsx` pattern.
- API base is **relative** `/api/v1` — no `process.env`/`NEXT_PUBLIC_*` in src by design; `frontend/next.config.ts` has async rewrites mapping `/api/v1/:path*` to `${NEXT_PUBLIC_API_BASE_URL}/api/v1/:path*` (default `https://api.mypapyr.com`). Backend is same-origin via rewrite in production.
- Styling: Tailwind v4 tokens in `src/app/globals.css` `@theme` (navy `#1e3a5f`, accent `#2563eb`, bg, foreground) mirrored by `src/lib/design-tokens.ts` — keep in sync when editing tokens. No CSS modules, no tailwind.config.
- Naming: kebab-case lib/route files, PascalCase components, `use*` hooks; tests co-located in `__tests__/` with `// @vitest-environment jsdom` docblock; path alias `@` → `./src`.
- Fflate (`lib/zip.ts`, client-side zip) is the only PDF-ish processing in frontend; `sharp` unused. No Web Workers, no auth.

**Repo-wide**: LF line endings enforced by `.gitattributes` (blocks CRLF corruption of CI guards); markdownlint default with MD013/MD024/MD041 off; CI is deployment-free by policy (`check-ci.sh` enforces).

## Important Files

- `backend/app/main.py` — app factory (9 routers, exact mount order: status → capabilities → compress → image_to_pdf → merge → pdf_to_jpg → split → support → download; middleware order: security → request-id → error handlers)
- `backend/app/config.py` — `Settings` + required-env contract
- `backend/app/errors.py` — envelope + `spec_for_status()` table
- `backend/app/queue/store.py`, `queue/queue.py`, `tasks/state_machine.py` — job lifecycle core
- `backend/app/worker/worker.py` — claim/execute/acknowledge loop + runners
- `backend/app/security/validation.py`, `sanitize.py`, `fair_use.py` — admission gates
- `backend/app/utils/r2.py` — opaque keys `tmp/<date>/<32hex>.<ext>`, presign ≤300 s
- `frontend/src/app/[locale]/layout.tsx` (root layout), `page.tsx` (home), `compress-pdf/page.tsx` (reference tool flow), `blog/page.tsx` and `blog/[slug]/page.tsx` (listing/article routes)
- `frontend/content/blog/` + `frontend/src/lib/blog.ts` — typed pure-MDX content store and article metadata; `qa-blog-content` is the fail-closed CI content gate
- Legal pages render `LegalVersionFooter` with version 1.0 and effective date from localized `messages.legal` copy (DEC-045).
- `frontend/src/lib/taskPolling.ts` + `src/hooks/useTaskPolling.ts` — status polling contract
- `frontend/src/proxy.ts` — locale-redirect middleware logic, wired as the Next.js 16 proxy-file convention (proxy function + `config.matcher`)
- `deploy/docker-compose.yml` + `compose.override.deploy.yml`, `deploy/nginx/conf.d/production.conf` (skeleton)
- `.github/workflows/ci.yml` — 22 jobs (22 on pushes to main), including `frontend-typecheck`, `qa-seo-inventory`, and `qa-blog-content`; CI-without-CD; `scripts/check-ci.sh` guard contract

## Runtime/Tooling Preferences

- **Backend**: Python 3.13 (CI/base images; local pycache shows 3.14), **pip only** (no uv/poetry), exact `==` pins, ruff (line-length 100, target py313, select E,F,I,UP,B,SIM,PL,RUF; tests ignore PLR2004/S101), mypy **strict** via CI flags (no mypy.ini/pyproject).
- **Frontend**: Node 24+, **npm** (`package-lock.json` v3, `npm ci`; no Bun/yarn/pnpm), Next 16 App Router, ESLint flat config (next core-web-vitals + typescript-eslint, `^_` unused-ignore), Prettier (printWidth 100, double quotes, LF).
- **Shell**: scripts are POSIX `sh` (`set -eu`) — run via Git-Bash/WSL/CI on this Windows host.
- **Docker**: required for Redis integration tests (`redis:7.4.10-alpine`); Playwright needs `npx playwright install chromium`.
- No pre-commit config; no root package.json/workspaces.

## Testing & QA

- **Backend**: pytest 9.1.1 + pytest-cov (no pytest-asyncio — async exercised via `TestClient`/`run_once()`). Rootdir `conftest.py` seeds the 5 required env vars before app import; `tests/conftest.py` `client` fixture = fresh `TestClient(create_app())` per test. Fakes: `FakeClock`, fakeredis `FakeServer` (cast to `RedisLike`/`StreamsRedisLike`), moto for R2 (`MOTO_S3_CUSTOM_ENDPOINTS` before `mock_aws`, `us-east-1`). Object-seam tests (`test_*_objects_seam.py`) lock `TransitionPayload.objects` pairing on terminal transitions. Real-Redis/R2 integration is opt-in via `REDIS_URL` + module-level skipif (FLUSHDB discipline; CI uses db 15).
- **Coverage**: 80% backend floor (NFR-03) enforced only by explicit CLI/CI flag, not pytest.ini; current measured 89.38%. Vitest thresholds lines 80 / funcs 80 / branches 80 / stmts 80 (branch threshold raised to 80 from the pre-existing 74; measured 91.27 stmts / 86.15 branches / 91.71 funcs / 93.10 lines).
- **Frontend e2e**: Playwright 1.62.1, `testDir ./e2e`, baseURL `http://localhost:3000`, 2 projects (Desktop Chrome + Pixel 7), webServer builds+starts locally / start-only in CI.
- Test conventions: behavior assertions, no snapshots; parametrize boundaries; never weaken CI/coverage/Trivy/gitleaks (CONTRIBUTING.md).

- **Docs authority**: `docs/specifications/` = target behavior, `docs/roadmap.md` = implementation state; source + tests remain the authority for what actually exists (`docs/plan/index.md`).

## Known remaining gaps (check before touching tool code)

1. **Cloudflare Email Sending credentials**: not yet provisioned in production (owner out-of-band action). Contact submissions validate and are accepted; delivery failures are counted only.
2. **Deploy skeletons**: compose nginx image remains `nginx:__SET_ME__`; `Dockerfile.worker` unwired.
3. **Vercel custom domains**: `autoAssignCustomDomains: false`; budgezen.com/mypapyr.com aliases are managed manually per deployment.
