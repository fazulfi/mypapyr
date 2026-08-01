# D5 — Security, Threat, and Privacy Requirements

| Field | Value |
|---|---|
| Brief ID | PPR-RB-D5 |
| Path | `audit-outputs\research\track-d\d5-security-threat-privacy.md` |
| Track | D (monetization, legal, privacy, support, and security requirements) |
| Title | Security, threat, and privacy requirements |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete (recommendation; no approved decision) |
| Governing decisions | DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171, DEC-036, DEC-064, DEC-074, DEC-175, DEC-174, DEC-166, DEC-170, DEC-013, DEC-067, DEC-070, DEC-179, DEC-182 |
| Spec sections served | Technical Architecture spec §17, §18, §22, §23; Product/UX spec §18; Track-D plan §7.4 D5 |
| Files read (local) | `papyr-rebuild-decisions.md` (DEC-088, DEC-090, DEC-092, DEC-093, DEC-169, DEC-171, DEC-036, DEC-064, DEC-074, DEC-175, DEC-174, DEC-166, DEC-170, DEC-013, DEC-067, DEC-070, DEC-179, DEC-182, DEC-054–057, DEC-066, DEC-104); `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` §17-18, §22-23, §25.3.8; `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` §18; `papyr-reference/deploy/docker-compose.yml`; `papyr-reference/backend/Dockerfile.production`; `papyr-reference/backend/utils/pdf_validator.py`; `papyr-reference/backend/utils/config.py`; `papyr-reference/backend/utils/logging_config.py`; `papyr-reference/docs/12_Papyr_Security_Policy_v1.0.md`; `papyr-reference/docs/runbook-vps.md` (referenced); `audit-outputs/research-program-plan.md` §7.4 |

---

## 1. Scope

**Decision area.** The threat and privacy requirements that bind Papyr's server-side processing: threat classification and blocking, sanitization, malware scanning, input validation, container/process hardening, PDF password handling, the prohibited-data register, and which failure classes fail closed versus route to server fallback. This brief reconciles those requirements against the Track-D research findings (D1-D4) and primary security standards, and confirms the DEC-022 accepted-risk visibility.

**User problem.** Papyr accepts untrusted PDFs and images from anonymous users and processes them on shared infrastructure. Users must be able to trust that files are processed safely, retained only briefly, never leaked to logs/analytics, and that passwords and metadata are handled responsibly.

**Current approved behavior.** Layered defenses: edge/nginx filtering, application validation, maintained malware scanning, active-content sanitization for PDF outputs, bounded resource controls, hardened container isolation (Arch §17.1). Threat-classified files are blocked, never processed or returned (DEC-088). Passwords are requested only when encryption is detected, held in memory briefly, and never persisted (DEC-036, DEC-064). Logs are content-free and retained 30 days (DEC-175); Redis persists only minimal task metadata (DEC-174).

**What this brief produces.** The threat classification and fail-closed/fail-open matrix, sanitization and scanner requirements, the prohibited-data register as applied to findings, password-handling requirements, and the security acceptance criteria — consistent with the sanctioned research constraints (no installs, no VPS access, no scanning implementation).

## 2. Non-goals

- No malware-scanning implementation, installation, or engine testing (implementation-phase action; selection is scoped here).
- No VPS access, container builds, or security scans of running systems (DEC-063, DEC-172 consequences; execution boundaries).
- No benchmark program, comparative security-testing study, or quality-scoring of engines (DEC-066).
- No claim that any control produces malware-free or sanitization-complete outputs (DEC-090, DEC-171).
- No legal compliance assessment (D2 owns the legal-review scope).

## 3. Research questions (restated from plan §7.4, D5)

1. How are files classified as threats, and which failure classes fail closed versus route to server fallback (DEC-088, DEC-065)?
2. What must sanitization and malware scanning cover, and what are their honest limits (DEC-090, DEC-171)?
3. What input validation and isolation requirements apply to PDF and image paths (DEC-169, DEC-092, DEC-093)?
4. What password-handling requirements apply across the applicable tools (DEC-036, DEC-064, DEC-074)?
5. What does the prohibited-data register require across logs, analytics, Redis, backups, alerts, and support flows as applied to Track-D findings (Arch §23.2)?
6. Which infrastructure threats fail closed (DEC-088) and what monitoring protects the controls (DEC-182, DEC-175)?

## 4. Evidence

### 4.1 Local authoritative requirements

| Source | Location | Requirement |
|---|---|---|
| DEC-088 | `papyr-rebuild-decisions.md:1072-1082` | Threat-classified files are blocked; never processed for fidelity, sanitized, or returned; file does not reach document engines beyond minimum safely isolated inspection; cleanup within the absolute retention ceiling; safe localized rejection without exploit details; logs/security telemetry keep only minimal non-content indicators; false-positive handling never routes the rejected document through contact form |
| DEC-090 | `papyr-rebuild-decisions.md:1096-1107` | Merge/Split/Compress sanitize JavaScript, launch actions, embedded attachments, other active features from outputs; attachments removed and not offered separately; inputs always untrusted; no execution of embedded actions; no perfect-sanitization claim; threat-classified files blocked, not sanitized |
| DEC-092 | `papyr-rebuild-decisions.md:1121-1131` | PDF-to-JPG treats inputs as untrusted; rasterization excludes active content but parser/resource attacks remain; rendering isolated, least-privilege, bounded, patched; no execution of actions/attachments/external references; successful rasterization is not a malware-free claim |
| DEC-093 | `papyr-rebuild-decisions.md:1133-1143` | JPG-to-PDF: verify type from bytes, reject unsupported/malformed, enforce encoded/decoded resource limits, decode in isolation; extension/MIME untrusted; EXIF preservation never authorizes executing/logging/trusting metadata; browser and server paths need equivalent safety outcomes |
| DEC-169 | `papyr-rebuild-decisions.md:1985-1995` | Focused validation that blocks unsupported files and credible security/resource-exhaustion threats without rejecting ordinary valid documents; Docker one layer not the sole boundary; non-root, least privilege, bounded CPU/memory/time/disk, restricted network, hardened filesystem/capabilities, maintained engines; rejections expose only safe general categories; tuned by functional/security testing and production observations, not benchmarks |
| DEC-171 | `papyr-rebuild-decisions.md:2008-2017` | Maintained general malware scanner alongside other layers; scanner result is one signal, never a malware-free claim; scanner failure/update health/resource consumption/safe rejection monitored; user-facing rejection only safe categories |
| DEC-036 | `papyr-rebuild-decisions.md:452-462` | Passwords only when encryption detected; memory-only shortest practical lifetime; never in logs, analytics, URLs, queue dashboards, persistent task records, storage metadata, backups; secret-safe transport; wrong-password vs corrupt/unsupported errors distinct; cleared after success/failure/cancellation/timeout |
| DEC-064 | `papyr-rebuild-decisions.md:787-797` | Encrypted input support on Compress/Merge/Split/PDF-to-JPG; per-file password for Merge; credentials and permissions respected; clear localized errors; password handling governed by DEC-036 |
| DEC-074 | `papyr-rebuild-decisions.md:909-920` | Separate password per locked Merge input (read: `papyr-rebuild-decisions.md:909-920`) |
| DEC-175 | `papyr-rebuild-decisions.md:2054-2063` | 30-day sanitized operational logs; content-excluded |
| DEC-174 | `papyr-rebuild-decisions.md:2043-2052` | Redis persists minimal task metadata only; no contents/passwords/signed URLs/filenames/previews/extracted content |
| DEC-166 | `papyr-rebuild-decisions.md:1951-1960` | Active deletion by absolute deadline with lifecycle safety net; cleanup idempotent and observable without logging content/sensitive identifiers |
| DEC-170 | `papyr-rebuild-decisions.md:1997-2006` | Short-lived signed URLs; expiry never exceeds artifact expiry; URLs never in analytics/logs/browser persistence/support reports/status data |
| DEC-013/DEC-067/DEC-070 | `papyr-rebuild-decisions.md:158-170, 825-836, 861-872` | One-hour absolute retention from upload receipt; expiry enforced even while tab open; retention clock starts at upload receipt |
| DEC-179 | `papyr-rebuild-decisions.md:2108-2119` | Monthly dependency review; critical security fixes promptly; native processors, base images, packages, Actions, malware signatures in scope |
| DEC-182 | `papyr-rebuild-decisions.md:2131-2140` | Netdata + external uptime; coverage without collecting document contents; noise-resistant status |
| Arch §17-18, §23 | `2026-07-31-papyr-technical-architecture.md:744-853, 968-1006` | Defense layers; validation specifics; threat blocking; scanner; hardening; secrets; logging; backups; data classes; prohibited-data register; retention summary |
| UX §18 | `2026-07-31-papyr-product-ux-design.md:598-610` | Error/recovery behavior incl. fail-closed routing transparency (DEC-065) |

### 4.2 Legacy hardening baseline (evidence, not requirement)

- `papyr-reference/deploy/docker-compose.yml` — read-only root fs, dropped capabilities, `no-new-privileges`, CPU/memory limits, ephemeral tmpfs, internal ports only, healthchecks, log rotation (baseline cited by Arch §7.1).
- `papyr-reference/backend/Dockerfile.production` — multi-stage build, non-root user, tini, healthcheck, four uvicorn workers.
- `papyr-reference/backend/utils/pdf_validator.py` — legacy validation order: empty, MIME, extension, magic bytes, size, page count, encrypted (cited by Arch §17.2; the rebuild adds structure/decode-risk checks per DEC-169/DEC-093).
- `papyr-reference/backend/utils/config.py` — `MAX_UPLOAD_SIZE_MB` (20), `FILE_RETENTION_MINUTES` (60), `RATE_LIMIT_PER_MINUTE` (10).
- `papyr-reference/backend/utils/logging_config.py` — JSON structured logging with explicit no-content prohibitions ("TIDAK BOLEH log: file names, file contents, user IPs", lines 4-6).
- `papyr-reference/docs/12_Papyr_Security_Policy_v1.0.md` — historical security policy (zero-account/zero-tracking posture superseded by the accepted analytics/advertising model; validation and hardening patterns remain useful baseline).

### 4.3 Primary security standards and tool evidence (accessed 2026-07-31)

| Source | URL | Evidence |
|---|---|---|
| OWASP File Upload Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html | Extension allowlists, Content-Type untrusted, magic-byte validation, generated filenames, size limits, storage outside webroot, antivirus/CDR, library currency, CSRF protection |
| OWASP Unrestricted File Upload | https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload | Threat classes: web shells, parser exploits, decompression bombs, storage DoS, client-side active content, metadata disclosure |
| OWASP ASVS | https://owasp.org/www-project-application-security-verification-standard/ | Application-security verification levels usable as the security-testing baseline for the CI core gate |
| ClamAV Documentation | https://docs.clamav.net/ | GPLv2 open-source scanner; PDF scanning; archive scanning and archive-bomb protection; signed signature databases; ~3-4 GiB RAM recommendation for standard databases; LTS branch 1.4; security patches 1.5.3/1.4.5 (July 2026, blog.clamav.net) |
| Docker security documentation | https://docs.docker.com/engine/security/ | Container isolation as defense-in-depth; kernel namespaces/cgroups; the legacy compose baseline aligns |

ClamAV notes relevant to selection: it scans PDFs, handles archives and archive bombs, and requires several GiB RAM per its documented recommendation; scanner resource bounds must be incorporated into worker limits (interface to C2). The 1.4 LTS branch and the July 2026 patch releases evidence the "maintained" requirement (DEC-171); the monthly signature/dependency cadence in DEC-179 covers it.

## 5. Alternatives

### Alternative A — Maintained general scanner (ClamAV class) plus format validation, sanitization, resource bounds, and hardened containers (approved architecture as-is)

- **Description.** Keep DEC-169/DEC-171's layered model: edge/Nginx filtering; application validation (structure + decoded-resource risk); a maintained scanner; active-content sanitization for PDF outputs; bounded resources; hardened isolation.
- **Trade-offs.** Best defense-in-depth posture; operational cost of scanner maintenance (signatures, RAM, update health); sanitization may reduce fidelity (disclosed honestly per DEC-090); scanner is one signal, not a guarantee.
- **Cost/operational impact.** Scanner RAM/CPU bounds inside worker limits; monthly signature updates; monitoring of update health.
- **Privacy/security implications.** Scanner sees file bytes in isolation; no content retained (DEC-175); scanner logs minimal non-content indicators.
- **Risk.** Residual: novel/undetected malware, sanitizer coverage gaps, parser CVEs; mitigated by patching cadence (DEC-179) and honest limits (DEC-090, DEC-171).

### Alternative B — Validation and isolation only, without a maintained malware scanner

- **Description.** Drop the scanner layer; rely on format validation, sanitization, resource controls, and container isolation.
- **Trade-offs.** Cheaper and simpler; contradicts DEC-171 (accepted decision) and weakens the defense-in-depth rationale; any single-parser or sanitizer gap becomes a single point of failure.
- **Cost/operational impact.** Lower.
- **Privacy/security implications.** Higher residual risk of malicious payloads reaching engines.
- **Risk.** Conflicts with the approved decision baseline; not viable without a superseding decision.

### Alternative C — Add a second independent scanner or CDR (Content Disarm and Reconstruction) layer

- **Description.** Add a second scanner engine or CDR for PDFs in addition to the primary scanner.
- **Trade-offs.** Marginal detection improvement; doubles resource consumption and signature/maintenance load; CDR changes PDF structure and interacts poorly with the metadata-preservation decision (DEC-084) for JPG-to-PDF.
- **Cost/operational impact.** Higher RAM/CPU and licensing considerations (CDR products are typically commercial).
- **Privacy/security implications.** More tooling = more attack surface and more false-positive risk on ordinary valid documents, conflicting with DEC-169's "focused validation" principle.
- **Risk.** Over-engineering for the MVP; revisit only if production data shows a material gap (DEC-066-adjusted, from observations).

**Comparison summary:** A implements the accepted decisions with the strongest defensible posture and honest limits. B conflicts with DEC-171. C is premature for MVP and risks violating DEC-169's focused-validation principle. Recommendation: A.

## 6. Recommendation (recommendation only, not an accepted decision)

1. **Adopt Alternative A**, specifying ClamAV as the maintained general scanner candidate (GPLv2, PDF/archive scanning, documented RAM profile) with a selection checklist that re-verifies current version, LTS branch, signature-update channel, and safe-failure behavior at implementation time (DEC-056, DEC-171).
2. **Adopt the threat-classification and fail-closed/fail-open matrix** in Section 6.1 and apply it in the routing logic (DEC-088, DEC-065).
3. **Adopt the sanitization, validation, and isolation requirements** in Sections 6.2-6.4, including the honest-limits statements.
4. **Adopt the password-handling requirements** in Section 6.5.
5. **Enforce the prohibited-data register across all surfaces** as applied in Section 6.6, and make the D3 leakage-test suite the executable guard for it (Arch §22.3).
6. **Require security-testing acceptance** (Section 7) tied to the CI core gate (DEC-177), using OWASP ASVS-aligned checks and functional security tests — not a benchmark program.

### 6.1 Threat classification and fail-closed/fail-open matrix

**Classification signals (defense-in-depth, no single source decisive):** file signature/type mismatch, structural parse failure, decoded-resource risk (pixel count, frame count, decompression ratios, page counts), malware-scanner verdict, active-content profile exceeding sanitizable scope, and resource exhaustion (size, complexity, depth) per per-tool limits (C2).

| Failure class | Disposition |
|---|---|
| File classified as an infrastructure threat (DEC-088) | **Fail closed**: block; no processing, no sanitize-and-return, no output; safe localized rejection; prompt cleanup within the retention ceiling; user never asked to email/upload the file |
| Unsupported or malformed input (ordinary invalid file) | Safe localized validation error; no server fallback (DEC-065); no exploit details |
| Password wrong/missing/unsupported/permission-restricted (DEC-036, DEC-064) | Distinct localized error per file; no server fallback that would force an upload of the same file; no sensitive details |
| Security-policy failure (scanner failure, sanitization refusal, validation indeterminate) | **Fail closed**: treat as blocked or reject-safe per the classified outcome; scanner failure itself is monitored and must not silently accept files (DEC-171) |
| User cancellation, retention violation, unsafe condition | Fail closed; never force a server upload (DEC-065) |
| Safe recoverable browser failure (engine memory/dimension limits) | Route to server fallback only for classified recoverable failures (DEC-065), subject to server validation/sanitization all over again |
| Backend outage | Tool pages remain; server-dependent processing communicates temporary unavailability; no unsafe fallback (DEC-163) |

Rule: anything the system cannot classify as safe fails closed (block or safe rejection), never "process anyway". Sanitization never downgrades a blocked file into an output (DEC-088 vs DEC-090 boundary).

### 6.2 Sanitization requirements (Merge, Split, Compress outputs)

1. Remove or neutralize detected JavaScript, launch actions, embedded attachments, and other active PDF features (DEC-090); attachments are removed and not offered separately.
2. Inputs are always treated as untrusted; embedded actions/attachments are never executed (DEC-090, DEC-092).
3. Sanitization reports general categories removed (JavaScript, embedded attachments, launch actions, external actions) without payloads or exploit details (DEC-091); sanitization is distinguished from malware detection.
4. Sanitization coverage limitations are documented and verified by normal functional/security tests; Papyr claims no universal sanitization (DEC-090).
5. PDF-to-JPG rasterization inherently excludes active content but the input still passes untrusted-input inspection and threat blocking (DEC-092).

### 6.3 Input validation and isolation requirements

1. Validation inspects actual file structure and decoded-resource risk, not extension/MIME alone (DEC-169, DEC-093; OWASP File Upload Cheat Sheet: validate type by content, generated filenames, size limits, storage controls).
2. PDF validation covers empty files, MIME, extension, magic bytes, size, page count, encryption status, structure, and resource risk (Arch §17.2, extending the legacy `pdf_validator.py` order).
3. Image validation covers signatures, dimensions, pixel count, frame count, orientation data, decode expansion, and resource limits per format (DEC-093); accepted formats JPG/JPEG, PNG, WebP (DEC-187).
4. Processing services run non-root, least privilege, bounded CPU/memory/time/disk, restricted network, hardened filesystem/capabilities, maintained engines (DEC-169); legacy compose/Dockerfile provide the baseline.
5. Browser and server paths produce equivalent safety outcomes even with different decoders (DEC-093).

### 6.4 Malware-scanning requirements

1. Scanner runs as one layer among several; results never support a malware-free claim (DEC-171).
2. Scanner failure, update health, resource consumption, and safe rejection are monitored (DEC-171, DEC-182); a stale or failed scanner must fail closed rather than silently pass files.
3. Rejection messages expose only safe general categories (DEC-171).
4. Scanner resource profile (ClamAV documents ~3-4 GiB RAM for standard databases) is incorporated into worker/container bounds (interface to C2), with the documented raising procedure.
5. Signature updates follow DEC-179's monthly review and prompt critical-fix cadence.

### 6.5 Password-handling requirements

1. Passwords requested only when encryption is detected and only when required for the operation (DEC-036, DEC-064).
2. Passwords held in process memory for the shortest practical time; cleared after success, failure, cancellation, or timeout to the extent supported by the runtime (DEC-036).
3. Never written to logs, analytics, URLs, queue dashboards, persistent task records, storage metadata, backups, or error payloads (DEC-036, DEC-174, DEC-175).
4. Secret-safe transport across API/worker boundaries with redaction behavior (DEC-036); worker payloads carry no passwords.
5. Distinct wrong-password errors vs corrupt/unsupported errors without revealing sensitive engine details (DEC-036, DEC-064).
6. Merge collects a separate password per locked input and never confuses credentials between files (DEC-074, DEC-064).
7. JPG-to-PDF unaffected (image inputs); all four PDF tools in scope (DEC-064).

### 6.6 Prohibited-data register as applied to Track-D findings

The register in Arch §23.2 is reaffirmed and applied to the D-track surfaces:

- **Analytics (D3):** file contents, previews, rendered text, filenames, object keys, signed URLs, passwords, full error payloads, stable fingerprints prohibited; coarse bands only (DEC-025).
- **Logs:** content-free, 30-day retention, access-controlled (DEC-175); legacy `logging_config.py` prohibition pattern retained.
- **Redis:** minimal task metadata only; expires with task lifecycle (DEC-174).
- **Backups:** no user files, passwords, signed URLs, or temporary queue payloads (DEC-173).
- **Telegram alerts:** no user files, filenames, passwords, signed URLs, object keys, or sensitive payloads (DEC-180); no sensitive telemetry by design.
- **Support/contact (D4):** no document contents, filenames, passwords, signed URLs, or object keys in submissions or errors (DEC-046, DEC-117, DEC-120).
- **Advertising (D1):** ad identifiers are third-party telemetry on the page; they never combine with document-sensitive fields (D3 boundary) and never touch the processing pipeline.
- **Signed URLs:** never in analytics, logs, browser persistence, support reports, or status data (DEC-170); expiry never exceeds artifact expiry.
- **Ephemeral passwords (D5 above):** full exclusion from all persistent surfaces.

### 6.7 DEC-022 accepted-risk visibility

- DEC-022 remains an accepted risk, not a compliance finding (per the task instruction, surface it clearly; if evidence materially conflicts, escalate rather than rewrite). No evidence in this track changes its status: D1 found that the provider's public documents do not evidence a consent-free lawful basis for advertising identifiers in EEA/UK/CH, which *reinforces* (does not contradict) the risk record. This is recorded as a supporting finding and a reconciliation input (X2), not a decision rewrite.
- The security controls in this brief do not reduce or increase the DEC-022 risk; advertising consent is orthogonal to file-processing security. Both remain owner decisions (DEC-057).

## 7. Measurable acceptance criteria (no benchmark wording)

1. Threat-classified files are blocked end-to-end: integration tests upload representative threat samples and assert no output, no engine processing beyond isolated inspection, prompt cleanup, and a safe localized rejection (DEC-088).
2. Sanitization behavior is verified with fixtures containing each active-content category; outputs contain no executable JavaScript, launch actions, or attachments, and the UI shows general categories removed (DEC-090, DEC-091).
3. Malware scanner is present, maintained (signature updates current), and its failure state is fail-closed and monitored (DEC-171, DEC-182); a simulated scanner failure rejects rather than accepts files.
4. Validation rejects unsupported/malformed inputs and resource-exhaustion profiles with safe localized errors and never routes them to server fallback (DEC-093, DEC-065).
5. Password tests assert: passwords never appear in logs, analytics, task records, backups, error payloads, or Redis (Arch §22.3 leakage tests); wrong-password and corrupt-file errors are distinct; per-file Merge passwords are not cross-applied (DEC-036, DEC-064, DEC-074).
6. Hardening checks verify non-root execution, dropped capabilities, `no-new-privileges`, read-only root, bounded CPU/memory/time/disk, restricted network, and internal ports only (DEC-169; legacy compose baseline).
7. The prohibited-data register is enforced by the D3 leakage-test suite across analytics, logs, Redis, backups, alerts, and support flows (Arch §22.3).
8. Dependency review and critical-patch cadence are operational (DEC-179), evidenced by a documented monthly review and prompt-fix procedure.
9. Cleanup runs within the absolute retention ceiling with observable counts only (DEC-166); signed-URL expiry never exceeds artifact expiry (DEC-170).
10. No security acceptance criterion references a benchmark program, corpus, or comparative quality score (DEC-066).

## 8. Assumptions, uncertainties, and unresolved questions

- **Assumption:** ClamAV (or an equally maintained scanner) is deployed at implementation time after current-version verification; scanner selection is not finalized by this brief (Arch §25.3.8).
- **Uncertainty:** Exact resource bounds (scanner RAM, worker limits, rate-limit values) are implementation-level values tuned from production observations, not set here (DEC-066, C2/C4).
- **Uncertainty:** Sanitization coverage depends on the selected engine (Track A evidence); coverage limitations are documented at implementation with functional verification.
- **Unresolved (owner):** Scanner choice confirmation; acceptance of the fail-closed posture's false-positive rate (balanced per DEC-169); whether security reports receive a dedicated address (D4).
- **Unresolved (legal review, D2):** Whether any control changes GDPR/ePrivacy posture; it does not affect the DEC-022 advertising risk.

## 9. Dependencies and cross-track interfaces

- **A2-A6 (tool briefs):** Per-tool validation/sanitization/render requirements feed C2 limits and this brief's per-tool acceptance tests.
- **C2 (server limits):** Resource bounds consumed by the scanner and engines.
- **C4 (hardening):** Nginx rate limits, container hardening, fair-use thresholds; scanner placement in the VPS stack.
- **C5 (observability):** Scanner health, cleanup health, fail-closed monitoring; Telegram alerts content-free (DEC-180).
- **D1/D2/D3/D4:** Advertising telemetry boundary, copy truthfulness about controls (no malware-free claims), analytics leakage tests, support-flow content prohibitions.
- **X2 (reconciliation):** Escalation record that D1 evidence reinforces DEC-022's risk; scanner and fail-closed owner prompts.

## 10. Source-date log and evidence-completeness notes

| Source | Accessed | Notes |
|---|---|---|
| OWASP File Upload Cheat Sheet | 2026-07-31 | Current community-maintained standard |
| OWASP Unrestricted File Upload | 2026-07-31 | Threat taxonomy |
| OWASP ASVS | 2026-07-31 | Verification-level baseline for security testing |
| ClamAV docs + blog | 2026-07-31 | GPLv2, PDF/archive scanning, RAM profile, 1.4 LTS, 1.5.3/1.4.5 patches (July 2026) |
| Docker security docs | 2026-07-31 | Container-isolation context |
| Legacy security artifacts | 2026-07-31 | Baseline only |

Evidence-completeness: standards and tool evidence cover the accepted decision layers; exact numeric bounds remain implementation-time values per DEC-066, recorded as open rather than hidden.

## 11. Prohibitions-compliance statement

- No installs, builds, container operations, server starts, VPS access, or account creation were performed; no scanning engine was run.
- No source, specification, decision-log, or existing `audit-outputs/` file was modified. The only file created is this brief.
- `papyr-reference/` was only read and remains unchanged.
- No benchmark program, corpus, or comparative security study was created (DEC-066).
- Findings are recommendations requiring owner approval (DEC-054, DEC-057).
