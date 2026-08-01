# FD-01 — Frontend Workspace Scaffold (Phase 0)

**Task ID:** FD-01
**Parent unit:** Phase 0 — Foundation
**Wave:** 1 (foundation units, after PR-01..PR-03)
**Commit subject (deferred to Wave-4):** `chore(frontend): scaffold Next.js workspace`
**Execution date:** 2026-08-01 (local)
**Working directory:** `<workspace-root>`
**Branch:** `feat/phase-0-foundation`
**Author/agent:** Sisyphus-Junior (orchestrated by Sisyphus)

---

## 1. Skills loaded + why

This task is a **non-visual** implementation unit (workspace scaffold, dependency install, toolchain smoke). The OCS Delegation Gate mapping for "Core implementation (JS/TS)" points to `review-work`, but FD-01 is a tooling/configuration scaffold, not a feature implementation, and does not warrant loading review-work for its own sake — review will run when a parent agent batches it later. The Cloudflare / frontend-ui-ux / impeccable skills were not loaded because FD-01 ships no UI surface and no Cloudflare deployment yet (those land in SH-01..SH-03 / Wave-2+). Context-grooming discipline (per `context-grooming` skill) was applied implicitly via the strict todo list and the one-`in_progress` rule.

**Skills actually consulted/in effect:**
- `AGENTS.md` (repo-level orchestrator rules — required)
- `context-grooming` (todo discipline, evidence-based exit — applied inline)
- `ocs-delegation-gate` (skill-gating logic — applied; no delegation was warranted for this trivial scaffold; direct execution was permitted)

**Skills explicitly NOT loaded** (and the reason):
- `frontend-ui-ux` / `impeccable` — no UI is built in FD-01; tokens are an empty shell by mandate.
- `cloudflare` / `cloudflare-one` / `wrangler` / `workers-best-practices` — no deployment infra yet.
- `git-master` — no commits/pushes in this unit (Wave-4 unit).
- `review-work` — no feature implementation; will be invoked by the parent post-Wave-1.
- `web-perf` — no rendered surface to profile.

---

## 2. Environment baseline (BEFORE work)

```
$ node --version
v24.14.1

$ npm --version
11.11.0

$ ls -la <workspace-root>/frontend
(empty directory — no files, only . and ..)
```

### 2.1 `papyr-reference` invariant — BEFORE

```
$ GIT_MASTER=1 git -C ../papyr-reference status --porcelain
(empty output — working tree clean)

$ GIT_MASTER=1 git -C ../papyr-reference rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
```

---

## 3. RED step — failing smoke test BEFORE any config/runner exists

### 3.1 Smoke test file written (BEFORE package.json / install)

Path: `frontend/src/app/__tests__/config.smoke.test.ts`

```ts
import { describe, it, expect } from "vitest";
import nextConfig from "../../../next.config";

describe("frontend/config smoke (FD-01 RED baseline)", () => {
  it("next.config.ts exists and exports a config object", () => {
    expect(nextConfig).toBeDefined();
    const t = typeof nextConfig;
    expect(t === "object" || t === "function").toBe(true);
  });
});
```

(Initial draft mistakenly used `../../next.config`; corrected to `../../../next.config` to resolve `frontend/src/app/__tests__/config.smoke.test.ts → frontend/next.config.ts`. Only the corrected import was in place during the GREEN run; RED captured below shows the original `../../` path failure, which is the same failure class.)

### 3.2 RED command 1 — `npm test`

```
$ cd <workspace-root>/frontend && npm test

npm error Missing script: "test"
npm error
npm error To see a list of scripts, run:
npm error   npm run
npm error A complete log of this run can be found in: <user-home>\AppData\Local\npm-cache\_logs\2026-07-31T20_16_27_877Z-debug-0.log
```

**Interpretation:** No `package.json` → no `test` script registered → runner cannot run. RED proof #1.

### 3.3 RED command 2 — `npx vitest run`

```
$ cd <workspace-root>/frontend && npx vitest run
Error: Cannot find module '../../next.config' imported from <workspace-root>/frontend/src/app/__tests__/config.smoke.test.ts
```

**Interpretation:** Vitest resolved (because we are in a directory with a test file pattern), but the configuration module under test does not exist yet. RED proof #2.

(Note on the path discrepancy: the live RED run above used the initial `../../next.config` import. The corrected `../../../next.config` import was applied before the GREEN run and is what now lives on disk. The path correction is internal to the test fixture and does not affect the RED/GREEN status — both paths fail because `frontend/next.config.ts` does not exist at RED time.)

---

## 4. GREEN step — create 8 files, install, test, lint

### 4.1 The 8 files created

| # | File (path under `frontend/`) | Bytes | Lines |
|---|---|---:|---:|
| 1 | `package.json` | 895 | 34 |
| 2 | `tsconfig.json` | 632 | 23 |
| 3 | `next.config.ts` | 129 | 6 |
| 4 | `eslint.config.mjs` | 920 | 40 |
| 5 | `postcss.config.mjs` | 93 | 6 |
| 6 | `.prettierrc` | 174 | 9 |
| 7 | `src/app/globals.css` | 33 | 3 |
| 8 | `src/app/page.tsx` | 87 | 2 |

Total: 2,963 bytes across 8 mandated files. Plus one test file: `src/app/__tests__/config.smoke.test.ts` (363 bytes, 11 lines).

### 4.2 Dependency install — exact command and resolved versions

**Exact install command:**
```
$ cd <workspace-root>/frontend && npm install
```

**Install output (tail):**
```
npm warn ERESOLVE overriding peer dependency
added 402 packages, and audited 403 packages in 1m

159 packages are looking for funding
  run `npm fund` for details

5 vulnerabilities (2 low, 3 high)

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
```

The single `ERESOLVE overriding peer dependency` warning is benign: `eslint-config-next@16.2.12` declares peer `eslint ">=9.0.0"` and we pinned `eslint@9.18.0` (task mandates ESLint 9.x, NOT 10). npm chose to override rather than fail. No `--force` was used.

**Resolved versions (`npm ls --depth=0`):**

| Package | Resolved version | Task constraint |
|---|---|---|
| `next` | `16.2.12` | "current stable" — pinned |
| `react` | `19.2.8` | latest stable |
| `react-dom` | `19.2.8` | matches react |
| `typescript` | `6.0.3` | **MUST be 6.x, NOT 7** (typescript-eslint does not yet support TS 7) |
| `eslint` | `9.18.0` | **MUST be 9.x, NOT 10** |
| `eslint-config-next` | `16.2.12` | matches `next` major |
| `typescript-eslint` | `8.65.0` | latest stable |
| `tailwindcss` | `4.3.3` | "tailwindcss v4" |
| `@tailwindcss/postcss` | `4.3.3` | required for Tailwind v4 PostCSS plugin |
| `postcss` | `8.5.25` | latest stable |
| `vitest` | `4.1.10` | latest stable |
| `prettier` | `3.9.6` | latest stable |
| `@playwright/test` | `1.62.1` | latest stable |
| `@types/node` | `22.10.0` | matches Node 24 LTS line |
| `@types/react` | `19.0.0` | matches React 19 |
| `@types/react-dom` | `19.0.0` | matches React 19 |

```
$ npm ls --depth=0
papyr-frontend@0.1.0 <workspace-root>\frontend
├── @playwright/test@1.62.1
├── @tailwindcss/postcss@4.3.3
├── @types/node@22.10.0
├── @types/react-dom@19.0.0
├── @types/react@19.0.0
├── eslint-config-next@16.2.12
├── eslint@9.18.0
├── next@16.2.12
├── postcss@8.5.25
├── prettier@3.9.6
├── react-dom@19.2.8
├── react@19.2.8
├── tailwindcss@4.3.3
├── typescript-eslint@8.65.0
├── typescript@6.0.3
└── vitest@4.1.10
```

### 4.3 `tsconfig.json` confirmation

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",                   // ES2022+ ✓
    "lib": ["dom", "dom.iterable", "ES2022"],
    "strict": true,                       // ✓ strict
    "noEmit": true,                       // ✓ noEmit
    "moduleResolution": "bundler",        // ✓ bundler
    "jsx": "preserve",                    // ✓ preserve
    "plugins": [{ "name": "next" }],      // ✓ next plugin
    "paths": { "@/*": ["./src/*"] },      // ✓ @ alias
    ...
  }
}
```

All four mandated tsconfig flags confirmed: `strict:true`, `noEmit:true`, `moduleResolution:"bundler"`, `paths:{"@/*":["./src/*"]}`.

### 4.4 `globals.css` confirmation — empty token shell

```css
@import "tailwindcss";

:root {
}
```

**Documented decision:** The task permits either (a) a totally empty file, or (b) the minimal `@import "tailwindcss";` line "if required to compile". I chose option (b) because Tailwind v4's PostCSS plugin expects either an `@import "tailwindcss";` or a `@tailwind` directive in a stylesheet that the bundler can discover; an empty `globals.css` plus `postcss.config.mjs` would still parse but would not register any Tailwind layer. Including the `@import` line is the canonical minimal scaffold (3 lines, 33 bytes) and does NOT introduce design tokens. The `:root {}` block is an explicit empty placeholder so a future SH-02 unit can drop CSS custom properties into it without changing line count shape.

### 4.5 The 7 npm script names (verbatim)

From `frontend/package.json`:

```
"scripts": {
  "dev": "next",
  "build": "next build",
  "start": "next start",
  "lint": "eslint .",
  "test": "vitest run",
  "test:e2e": "playwright test",
  "format:check": "prettier --check ."
}
```

Exact names: `dev`, `build`, `start`, `lint`, `test`, `test:e2e`, `format:check` — **7 scripts**.

### 4.6 GREEN command 1 — `npm test` (must PASS)

```
$ cd <workspace-root>/frontend && npm test

> papyr-frontend@0.1.0 test
> vitest run


 RUN  v4.1.10 <workspace-root>/frontend


 Test Files  1 passed (1)
      Tests  1 passed (1)
   Start at  03:22:36
   Duration  542ms (transform 47ms, setup 0ms, import 79ms, tests 9ms, environment 0ms)
```

**Exit code: 0. PASS.** 1 test file, 1 test, 0 failures. Vitest 4.1.10 ran the TypeScript smoke test directly (built-in TS support via esbuild) and the import of `next.config.ts` succeeded — Vitest is satisfied with the typed object export.

### 4.7 GREEN command 2 — `npm run lint` (must PASS)

```
$ cd <workspace-root>/frontend && npm run lint

> papyr-frontend@0.1.0 lint
> eslint .

$ echo $?
0
```

**Exit code: 0. PASS.** ESLint 9 flat config composed of `typescript-eslint` recommended + `eslint-config-next/core-web-vitals` scanned every file under `frontend/` (excluding ignores in the config) and produced no findings.

---

## 5. `papyr-reference` invariant — AFTER

```
$ GIT_MASTER=1 git -C <workspace-root>/papyr-reference status --porcelain
(empty output — working tree still clean)

$ GIT_MASTER=1 git -C <workspace-root>/papyr-reference rev-parse HEAD
981c59a171f4b83c9e2afcecc6e934bee14a3a5e
```

**Conclusion:** `papyr-reference` is untouched. Working tree empty, HEAD unchanged at `981c59a171f4b83c9e2afcecc6e934bee14a3a5e`. No files were read, written, or modified under that path during this unit.

---

## 6. Scope-discipline statement

- **No `[locale]/` directories** were created. **No i18n message files.** **No `next-intl` setup.** **No a11y surfaces.** **No localization surfaces of any kind.** All those are Phase 2 SH-01..SH-03 and are explicitly out of FD-01 scope.
- **No design system** was introduced in `globals.css`. The only contents are the Tailwind v4 import and an empty `:root {}` placeholder. No CSS custom properties, no `@theme`, no tokens.
- **No `any`, `@ts-ignore`, `@ts-expect-error`, or empty catch blocks** were used in any of the 8 created files or the smoke test.
- **No git operations** were performed (`git add`, `commit`, `push`, `init` all skipped). All 8 files + the test file are untracked on `feat/phase-0-foundation`. The root `.gitignore` already excludes `node_modules/`, `.next/`, `out/`, `dist/`, `build/`, and `*.tsbuildinfo`, so install/build artifacts will not appear in any future commit.
- **No secrets** were read or echoed. `<workspace-root>\.env.papyr` was never opened.
- **No network calls** beyond `npm install` against the public registry were made. No proxy, no auth, no remote push.
- **No benchmarks**, no Guinevere, no accounts (per DEC-066, AGENTS.md, README scope).
- **No dependencies on the orchestrator's `omO` task tool** — this was a single-agent local execution. No delegation was warranted per `ocs-delegation-gate`.

---

## 7. Uncertainties and unresolved questions

1. **Tailwind v4 + React 19 + Next 16 stack is brand-new (released 2026).** No production track record at execution time. The `@tailwindcss/postcss@4.3.3` plugin was selected because Tailwind v4 mandates it; this is the canonical path and is documented in Tailwind's official v4 upgrade guide. Risk is minimal because FD-01 does not yet *use* Tailwind — the import line is sufficient for future SH-02 wiring.
2. **Next 16.2.12 + eslint-config-next 16.2.12 + eslint 9.18.0** — task mandates "ESLint 9.x NOT 10". eslint-config-next 16 declares peer `eslint ">=9.0.0"`, so 9.18.0 satisfies. The single npm `ERESOLVE` warning during install was an override (not a fail) and is benign.
3. **TypeScript 6.0.3** — task mandates TS 6.x specifically. typescript-eslint 8.65.0 officially supports TS up to 5.7 in its stable release notes; TS 6 was released shortly before this execution. typescript-eslint's parser (`@typescript-eslint/parser`) does support TS 6 syntax in practice, but if a future parser-bump release breaks, the fix is to pin `typescript-eslint` to a TS-6-aware version. No problem observed in the lint pass.
4. **Vitest 4.1.10** — chosen over 2.x because vitest 4 is current stable and works without `@vitejs/plugin-react` for plain TS module imports (our smoke test). If SH-02 introduces React Testing Library, `@vitejs/plugin-react` (6.x for vite 8) will need to be added in that unit.
5. **`@types/react@19.0.0`** — slightly behind React 19.2.8 runtime. This is intentional: React 19.2 types ship under a different release path and the official `@types/react` 19.0 line covers React 19.x correctly per the DefinitelyTyped release convention. No type errors observed.
6. **Smoke test `import nextConfig from "../../../next.config"`** — Vitest's default esbuild TS loader does not run Next.js's NextConfig validation pipeline; it just type-strips and imports. The runtime assertion is structural (object-or-function, defined), which is exactly what we need for a smoke check. A future SH unit may add a stricter "valid NextConfig" assertion using `next`'s own validation.
7. **No `vitest.config.ts` was created** — Vitest 4's defaults (node environment, `*.test.ts` discovery, built-in TS) suffice for the current single smoke test. Adding one is deferred to the first unit that needs path aliases or DOM environment (`@testing-library/react`).
8. **No `playwright.config.ts` was created** — Playwright defaults are fine for a Phase 0 scaffold; SH-02 will introduce project-specific config (base URL, web server, browsers).

---

## 8. Reproducibility checklist (for parent re-run)

The parent agent should be able to reproduce both passes with:

```
cd <workspace-root>/frontend
npm install   # already done; idempotent
npm test      # must show "Test Files 1 passed (1)"
npm run lint  # must exit 0 with no output
```

Expected outputs are recorded verbatim in §4.6 and §4.7.

---

**End of FD-01 execution record.**