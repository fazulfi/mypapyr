# Product roadmap

This roadmap distinguishes code available in the repository from intended product capability. It is directional, not a release commitment.

## Available foundation

- Minimal Next.js application and strict TypeScript configuration.
- FastAPI service foundation: app factory, strict environment configuration, health and readiness endpoints, request correlation, a stable error envelope, file and job validation schemas, and the pure server task state machine, with full unit coverage.
- Public-safe Compose, Nginx, and environment templates.
- CI with format, lint, unit-test, coverage, build, Playwright E2E, Trivy, gitleaks, dependency and package audit, and repository QA gates.
- Public product, architecture, security, integration, and contribution documentation.

## Now available: shared trilingual shell

The shared trilingual shell that lands the locale routing, accessibility navigation, and supporting pages is implemented and tested. The remaining work below is what comes next.

- English, Spanish, and Indonesian locale routing with persistent preference via cookie and Accept-Language fallback; non-supported two-letter prefixes are stripped so requests resolve under EN without redirect loops.
- Accessible navigation across all three locales: SkipLink as the first focusable element, sticky Navbar with categorized tool menus, Footer with tools and support columns, LanguageSwitcher with equivalent-path resolution, and a single `main` landmark per locale.
- Localized homepage, localized 404 with `lang` and locale-resolved copy, and localized supporting route shells for privacy, terms, cookies and advertising, contact, status, roadmap, and blog.
- Unit and Playwright E2E gates cover locale routing, cookie preference, the SkipLink and focus target, contrast on the focused SkipLink, the localized 404, and the supporting route headings across all three locales.

## Next: tool pages and shared experience

- Localization across the five tool pages (English, Spanish, Indonesian) and the localized upload, progress, failure, and download patterns.
- Shared file validation and processing-location disclosure.
- Stable analytics and error contracts that exclude document-derived data.

## Specified launch catalogue

The five-tool catalogue below is fully specified in the product specification. The tools are not implemented yet; this section describes target behaviour and the planned implementation approach.

1. **Compress PDF** — one automatic quality profile. The server path uses the official, unmodified Ghostscript distribution through a hardened subprocess boundary.
2. **Merge PDF** — ordered multi-file merging with preservation rules defined by the product specification.
3. **Split PDF** — range and per-page output with deterministic ordering.
4. **JPG to PDF** — image normalization, orientation handling, and predictable page fitting.
5. **PDF to JPG** — high-quality page rendering with transparent compositing.

Each tool is planned with browser-first capability detection, a transparent server fallback where needed, explicit limits, accessible states, and consistent retention rules.

## Planned platform services

- Versioned API contracts and validation.
- Redis-backed durable queue with bounded fair scheduling.
- Isolated workers and native engine wrappers.
- Cloudflare R2 temporary-object lifecycle.
- Abuse controls, monitoring, incident alerts, and recovery procedures.
- Separately authorized production release and deployment automation.

## Later opportunities

Additional PDF tools, organizational features, billing, public APIs, and advanced workflows are outside the launch catalogue and require separate product decisions.
