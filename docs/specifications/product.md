# Product specification

## Product promise

Papyr is planned as a fast, simple, anonymous PDF utility platform. A user should be able to arrive, select a focused tool, provide files, understand where processing occurs, receive an honest result, and leave without creating an account.

The launch catalogue contains exactly five tools:

1. Compress PDF.
2. Merge PDF.
3. Split PDF.
4. JPG to PDF.
5. PDF to JPG.

These workflows are target requirements; they are not implemented in the current foundation code.

## Audience and experience principles

Papyr serves people who need a common document task completed quickly without navigating a general-purpose editor. The interface prioritizes:

- One clear primary action per page.
- Minimal configuration and predictable defaults.
- Honest progress, processing-location, and result reporting.
- Keyboard access, visible focus, readable contrast, and semantic status updates.
- Responsive use on mobile and desktop.
- English, Spanish, and Indonesian across every essential launch surface.
- Product completion ahead of advertising or promotional content.

## Shared workflow

Every launch tool follows a consistent state model:

1. **Ready** — explain accepted inputs, limits, privacy, and processing behaviour.
2. **Selected** — validate file type, size, count, encryption, and structural constraints.
3. **Processing** — disclose browser or server execution and show truthful progress.
4. **Completed** — summarize outputs and expose direct download actions.
5. **Failed** — provide a stable, actionable category without exposing engine internals.
6. **Cancelled or expired** — stop work, invalidate capabilities, and remove temporary data.

A server fallback must never be hidden. If a browser path cannot complete reliably, the user is told before server upload begins.

## Launch tools

### Compress PDF

- One automatic compression profile optimized for strong visual quality and useful size reduction.
- Report original size, result size, and actual percentage saved.
- Never report fabricated savings and never substitute the original while claiming compression.
- The planned native server path invokes the official, unmodified Ghostscript distribution as a separate hardened subprocess.

### Merge PDF

- Accept multiple PDFs, preserve explicit user ordering, and produce one result.
- Allow file-level reorder and removal before processing.
- Reject unsupported encryption and invalid structures with clear categories.
- Define metadata, bookmark, form, and active-content handling consistently between browser and server paths.

### Split PDF

- Support custom ranges and one-file-per-page output.
- Validate overlap, ordering, duplicates, and out-of-range pages deterministically.
- Preserve requested result ordering and provide a predictable archive when multiple outputs are produced.

### JPG to PDF

- Accept JPG and JPEG at minimum; PNG and WebP are launch candidates when implemented and tested.
- Respect image orientation.
- Fit images predictably to standard pages without unexpected cropping.
- Keep output ordering aligned with the user's file ordering.

### PDF to JPG

- Render every requested page at one documented quality profile.
- Composite transparency predictably.
- Preserve page ordering and package multi-page results consistently.

## Localization

English, Spanish, and Indonesian are launch requirements. Locale choice must be persistent and manually overridable. URLs, metadata, canonical links, hreflang, errors, consent text, limits, and essential support content must remain aligned across locales.

## Accessibility

The target is WCAG 2.2 AA for launch surfaces. Required behaviours include:

- Full keyboard operation.
- Visible focus indication.
- Semantic labels, headings, errors, and status regions.
- No colour-only meaning.
- Respect for reduced motion.
- Touch targets and responsive layouts suitable for mobile use.
- Screen-reader announcements for validation, progress, completion, and failure.

## Privacy and retention

- No account is required for the launch catalogue.
- Browser-processed documents remain local.
- Server upload is disclosed before transfer.
- Server-side objects use opaque keys and have a target maximum retention of one hour from upload receipt.
- Passwords, filenames, document contents, extracted text, signed URLs, and object keys are excluded from analytics and logs.
- Advertising must not obstruct upload, processing, consent, error, or download controls.

## Limits and errors

Limits must be documented per tool and enforced before expensive work begins. Errors use stable categories such as invalid input, unsupported encryption, limit exceeded, unavailable server processing, expired result, cancelled operation, or internal processing failure. User-facing responses do not reveal command lines, scanner signatures, stack traces, filesystem paths, or provider credentials.

## Product success criteria

A launch workflow is complete only when it has:

- End-to-end browser and/or server behaviour as specified.
- Automated tests for success, limits, cancellation, errors, and cleanup.
- Accessible interaction states.
- Trilingual essential copy.
- Truthful result reporting.
- Security and retention controls verified by tests and operational evidence.

## Non-goals for the launch catalogue

Accounts, billing, team workspaces, cloud history, a public business API, paid priority, OCR, signing, watermarking, and office-format conversion are not part of the five-tool launch catalogue.
