# Product roadmap

This roadmap distinguishes code available in the repository from intended product capability. It is directional, not a release commitment.

## Available foundation

- Minimal Next.js application and strict TypeScript configuration.
- Minimal FastAPI application with a tested health endpoint.
- Public-safe Compose, Nginx, and environment templates.
- CI with format, lint, unit-test, coverage, build, Trivy, and gitleaks gates.
- Public product, architecture, security, integration, and contribution documentation.

## Next: shared product shell

- English, Spanish, and Indonesian locale routing.
- Accessible navigation, upload, progress, failure, and download patterns.
- Shared file validation and processing-location disclosure.
- Stable analytics and error contracts that exclude document-derived data.

## Planned launch catalogue

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
