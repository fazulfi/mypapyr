# E1 Research Brief: `gpt5.6-sol` Provider Documentation Contract

| Field | Value |
|---|---|
| Brief ID | E1 |
| Path | `audit-outputs/research/track-e/e1-gpt5-6-sol-contract.md` |
| Track | E (blog automation research) |
| Title | `gpt5.6-sol` provider documentation contract |
| Date | 2026-07-31 |
| Author role | Sisyphus-Junior (executor subagent) |
| Status | Complete (documentation contract produced; owner supply of private provider details still required before technical design finalization) |
| Governing decisions | DEC-051, DEC-048, DEC-054 to DEC-060, DEC-066, DEC-183, DEC-188 |
| Governing plan section | Research program plan §6.5, §7.5 (E1), §8 (template) |
| Files read | `AGENTS.md`; `audit-outputs/research-program-plan.md`; `papyr-rebuild-decisions.md` (DEC-001-188 and Open decisions, in full); `docs/superpowers/specs/2026-07-31-papyr-product-ux-design.md` (§15.6, §21.21); `docs/superpowers/specs/2026-07-31-papyr-technical-architecture.md` (§1.4, §25.3.21); `audit-outputs/spec-cross-review.md`; `audit-outputs/spec-corrections-report.md`; read-only evidence from `papyr-reference/` (grep for LLM-provider identifiers and `gpt5.6` across the clone: zero matches); public primary and secondary sources listed in Section 5 |

---

## 1. Scope

### 1.1 Feature and decision area

DEC-051 accepted the use of "the project owner's custom LLM provider and the model identifier `gpt5.6-sol`" for the automated blog workflow. DEC-051 also requires that the provider's base URL, authentication, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, and availability "must be documented before technical design is finalized." UX spec §21.21 and architecture spec §25.3.21 carry that obligation forward. E1 produces that documentation contract.

### 1.2 User problem

The automated blog workflow (DEC-048, DEC-049, DEC-052, DEC-053, DEC-121, DEC-124) generates, localizes, validates, schedules, and publishes MDX articles with blocking quality gates that fail closed. That workflow depends on a provider contract the technical design must integrate against. Without a documented contract, the provider integration cannot be isolated behind an interface (DEC-051), secrets cannot be handled safely (DEC-051), and the fail-closed gates (DEC-048) cannot be designed with known request/response and retry semantics.

### 1.3 Current approved Papyr behavior

- Blog content is stored as version-controlled MDX in the repository (DEC-049).
- Generation, localization, validation, scheduling, and publication are fully automated with blocking quality gates that fail closed (DEC-048).
- The model identifier is `gpt5.6-sol`, recorded exactly as supplied; DEC-051 states the identifier "does not imply a specific vendor, public model family, API protocol, endpoint, or capability" and that the owner "explicitly selected this existing custom provider/model rather than a standard Gemini, OpenAI, or lowest-cost routing strategy."
- Launch inventory is five topics x EN/ES/ID (DEC-052, DEC-121); post-launch cadence is at most one coordinated trilingual topic set per day (DEC-053, DEC-124).

## 2. Non-goals

- No agent authentication to any provider, no provider API calls, no account creation, no access to any endpoint (prohibited by the research plan §4.1 and by this brief's method).
- No assumption that `gpt5.6-sol` maps to any specific vendor, protocol, or endpoint. Where public evidence identifies the model family, that evidence is recorded and flagged for owner confirmation; it is not treated as a resolved protocol decision.
- No implementation, no provider SDK selection, no technical design of the integration. This brief stops at the documentation contract (plan §6.5).
- No fabrication of contract fields, prices, limits, or capabilities. Every claimed public fact carries a source and an access date (DEC-056).

## 3. Research questions (plan §7.5, E1)

1. What is publicly discoverable about the exact identifier `gpt5.6-sol`, with primary sources?
2. For each DEC-051 contract field (base URL, authentication, request/response schema, structured-output support, tool use, rate limits, cost, context limits, retry behavior, data retention, availability): what is publicly documented, and what remains an owner-supplied gap?
3. Which standard documentation contract shape should the owner's private provider documentation fill, so that the integration interface can be designed?
4. What are the material owner inputs required before technical design finalization?

## 4. Method

- Read the decision log, both approved specs, both spec review/correction reports, and the research plan in full (see header).
- Performed a read-only case-insensitive search of `papyr-reference/` for LLM-provider identifiers (`gpt5.6`, `gpt5`, `gpt-5`, `openai`, `anthropic`, `gemini`, `base_url`, `api.?key`, `endpoint`). Result: zero references to any LLM provider, model identifier, or API base URL in the legacy clone. The legacy OpenClaw-era automation referenced an OpenAI-compatible chat-completions response shape (`docs/29_Papyr_OpenClaw_v1.0.md:923` `response.choices[0].message.content`), which is historical evidence only (DEC-016, DEC-026) and does not bind the rebuild.
- Verified the exact identifier against the public web with multiple independent queries on 2026-07-31.
- Verified the currency of every cited URL with read-only HTTP HEAD/GET checks on 2026-07-31 (all returned HTTP 200 unless noted).
- No prohibited action was performed (see Section 12).

## 5. Evidence

### 5.1 Exact-identifier verification (public record as of 2026-07-31)

The exact identifier `gpt5.6-sol` has substantial public documentation. Multiple independent searches on 2026-07-31 returned consistent results identifying it as the flagship variant of OpenAI's GPT-5.6 model family, released 2026-07-09.

**Primary sources:**

| # | Source (URL) | What it documents | Access date | Role |
|---|---|---|---|---|
| P1 | `https://openai.com/index/gpt-5-6` | Official general-availability announcement: GPT-5.6 family (Sol flagship, Terra, Luna); availability across ChatGPT, Codex, and the OpenAI API; per-1M-token pricing (Sol $5 input / $30 output); reasoning efforts `max` and `ultra`; Programmatic Tool Calling in the Responses API; multi-agent beta; Zero Data Retention (ZDR) compatibility; prompt-cache pricing and a July 30, 2026 price update for Terra (−20%) and Luna (−80%) | 2026-07-31 | Primary |
| P2 | `https://openai.com/index/previewing-gpt-5-6-sol` | Official limited-preview announcement for GPT-5.6 Sol: capability focus (coding, cybersecurity, knowledge work); introduces `max` reasoning effort and `ultra` mode | 2026-07-31 | Primary |
| P3 | `https://help.openai.com/en/articles/20001354-gpt-56-in-chatgpt` | OpenAI Help Center: GPT-5.6 in ChatGPT; Sol powers Medium/High/Extra High reasoning options on eligible plans; Sol Pro variant | 2026-07-31 | Primary |

**Secondary (supporting only) sources:**

| # | Source (URL) | What it documents | Access date | Role |
|---|---|---|---|---|
| S1 | `https://en.wikipedia.org/wiki/GPT-5.6` | Wikipedia article: GPT-5.6 released July 9, 2026, three variants Sol/Terra/Luna | 2026-07-31 | Secondary |
| S2 | `https://openrouter.ai/openai/gpt-5.6-sol` | OpenRouter model catalog: slug `openai/gpt-5.6-sol`; $5/$30 per 1M; 1M context; knowledge cutoff Feb 2026; served via OpenAI, Azure, Azure (EU), Amazon Bedrock (US); OpenAI-compatible, Responses-format, and Anthropic-Messages-format endpoints; `reasoning`, `response_format`, `tools`, `tool_choice` parameters | 2026-07-31 | Secondary |

**Reconciliation note (flagged for owner, not silently resolved):** DEC-051 and the research plan were written recording that the identifier "does not imply a specific vendor." The public record as of 2026-07-31 identifies `gpt5.6-sol` with OpenAI's GPT-5.6 Sol model family released 2026-07-09. The owner's DEC-051 wording ("custom LLM provider") and the public record are not contradictory: a "custom provider" can be an owner-managed access path (OpenAI platform account, an OpenAI-compatible gateway or reseller, Azure/Bedrock hosting, or a self-hosted deployment) that serves the same public model family. E1 treats the public model identity as documented fact and the owner's access path, endpoint contract, and commercial terms as owner-supplied gaps. The owner should confirm which access path their "custom provider" uses; this is recorded as a material owner input (Section 9) and a reconciliation item for X2.

### 5.2 Publicly verifiable facts relevant to each DEC-051 field

| DEC-051 field | Publicly documented (as of 2026-07-31) | Public source(s) |
|---|---|---|
| Model identity | `gpt5.6-sol` corresponds to OpenAI GPT-5.6 Sol (flagship tier of the GPT-5.6 family; Sol, Terra, Luna); OpenAI-developed; released 2026-07-09; knowledge cutoff Feb 2026 per S2; a "Sol Pro" variant is served with `reasoning.mode=pro` (S2, P3) | P1, P2, P3, S1, S2 |
| Base URL | OpenAI's platform API is documented at `https://api.openai.com/v1` (Responses and Chat Completions endpoints); OpenRouter exposes the model through OpenAI-compatible `/api/v1/chat/completions`, `/api/v1/responses`, and `/api/v1/messages` endpoints (S2). The owner's provider base URL is not publicly verifiable. | `https://platform.openai.com/docs/api-reference/responses/create` (200 on 2026-07-31); S2 |
| Authentication | OpenAI API uses `Authorization: Bearer` API keys (documented in the API reference); OpenRouter uses the same header shape (S2). The owner's provider credential model is not publicly verifiable. | platform API reference (above); S2 |
| Request/response schema | OpenAI documents the Responses API schema and the Chat Completions schema (both live at the API reference on 2026-07-31). OpenRouter documents an OpenAI-compatible chat request and a Responses-format request for this model (S2). The exact schema served by the owner's endpoint is not publicly verifiable. | `https://platform.openai.com/docs/api-reference/responses/create`; S2 |
| Structured outputs | OpenAI documents structured-output support (JSON schema via `response_format`); OpenRouter lists `response_format` for this model (S2). Whether the owner's endpoint enables this is not publicly verifiable. | `https://platform.openai.com/docs/guides/structured-outputs` (200); S2 |
| Tool use | OpenAI documents function/tool calling; OpenRouter lists `tools` and `tool_choice` for this model and rates provider tool-calling accuracy (S2). Whether the owner's endpoint enables tool calling is not publicly verifiable. | `https://platform.openai.com/docs/guides/function-calling` (200); S2 |
| Rate limits | OpenAI documents per-account-tier rate limits per model (rate-limits guide live on 2026-07-31). Exact limits depend on the account tier, which is owner-supplied. | `https://platform.openai.com/docs/guides/rate-limits` (200) |
| Cost | Public list price: Sol $5 input / $30 output per 1M tokens (P1); cache reads at 90% of input price, cache writes at 1.25x input, 30-minute minimum cache life, explicit cache breakpoints (P1); July 30, 2026 price reduction for Terra (−20%) and Luna (−80%) (P1); S2 lists the same $5/$30 with provider-level effective pricing and cache-hit rates. The owner's actual invoiced rate through their custom provider is not publicly verifiable. | P1, S2 |
| Context limits | OpenRouter lists 1M context for `openai/gpt-5.6-sol` (S2); OpenAI's models page documents context windows (live 2026-07-31). Effective context on the owner's deployment is not publicly verifiable. | S2; `https://platform.openai.com/docs/models` (200) |
| Retry behavior | OpenAI documents error semantics and retry guidance in the API reference; OpenRouter documents automatic provider retry when an endpoint errors (S2). The owner's provider retry/backoff behavior is not publicly verifiable. | platform API reference; S2 |
| Data retention | OpenAI's API data-usage policies are published (live 2026-07-31): API data is not used for training by default and a Zero Data Retention option exists; the GPT-5.6 announcement notes Programmatic Tool Calling is ZDR-compatible (P1). The owner's provider retention commitment is not publicly verifiable. | `https://openai.com/policies/api-data-usage-policies` (200); P1 |
| Availability | OpenAI publishes a public status page `https://status.openai.com` (200 on 2026-07-31). This research verified no public SLA text; any SLA or availability commitment for the owner's provider is owner-supplied. | `https://status.openai.com` (200) |

### 5.3 Standard documentation-contract reference

For building the owner's private documentation, the canonical field shape used by public LLM providers is recorded (vendor-neutral reference; this does not assert that the owner's provider is any specific vendor):

| Contract field | Canonical public reference (URL, verified 200 on 2026-07-31) |
|---|---|
| Endpoint and request/response schema | `https://platform.openai.com/docs/api-reference/responses/create`; `https://openrouter.ai/openai/gpt-5.6-sol` (OpenAI-compatible and Responses-format requests) |
| Structured outputs | `https://platform.openai.com/docs/guides/structured-outputs` |
| Tool use | `https://platform.openai.com/docs/guides/function-calling` |
| Rate limits | `https://platform.openai.com/docs/guides/rate-limits` |
| Pricing | `https://openai.com/api/pricing` (200); P1 |
| Context windows and models | `https://platform.openai.com/docs/models` |
| Data usage/retention | `https://openai.com/policies/api-data-usage-policies` |
| Availability | `https://status.openai.com` |
| Reasoning parameters (relevant to this model family) | `https://developers.openai.com/api/docs/guides/reasoning` (200; cited by S2 for `reasoning.mode=pro`) |

## 6. Alternatives (DEC-055)

| # | Approach | Trade-offs, risks, cost/operational impact, privacy/security | Assessment |
|---|---|---|---|
| A1 | **Contract pending owner private docs, with a per-field known/unknown matrix.** E1 documents all publicly verifiable facts and lists every DEC-051 field as owner-supplied where the owner's endpoint, terms, or access path is not publicly verifiable. Technical design waits for the owner's fill-in. | Correct per DEC-051 ("must be documented before technical design is finalized"); no invented facts; the integration interface can be designed against a stable field list. Cost: one owner round-trip before design finalization. Privacy/security: secrets handled per DEC-176; no provider access during research. | Recommended (Section 7). |
| A2 | **Adopt the public OpenAI API contract as the assumed contract for the owner's provider.** | Faster start, but directly contradicts DEC-051's "does not imply a specific vendor/endpoint" and risks designing against the wrong base URL, auth, rate limits, retention, and cost. Fabrication risk under DEC-056. | Rejected for design purposes; public facts are recorded in Section 5.2 as evidence only. |
| A3 | **Produce only a generic vendor-neutral contract template with no public evidence.** | Avoids any vendor identification, but discards verifiable public evidence (Section 5.1) that materially reduces the owner's fill-in burden and contradicts DEC-056's primary-source priority. | Rejected. |

## 7. Recommendation

**Recommendation (not an accepted decision; DEC-054, DEC-057):** Adopt A1. The documentation contract in Section 8 is the canonical fill-in form the owner completes from their private `gpt5.6-sol` provider documentation. Publicly verifiable facts (Section 5.2) are separated from owner-supplied gaps (Section 8). The owner should also confirm the reconciliation item in Section 5.1 (which access path their "custom provider" uses). Technical design of the provider integration must not finalize until the owner supplies the private documentation (DEC-051, UX §21.21, arch §25.3.21).

## 8. The DEC-051 documentation contract (known/unknown matrix)

For each field: **Publicly verifiable** (Yes/Partial/No + source) vs **Owner-supplied value** (the gap). "Owner-supplied" means only the owner can provide it from their private provider documentation, account, or contract. The workflow's quality gates in DEC-048 remain provider-independent; this contract documents only the provider integration.

| # | DEC-051 field | Publicly verifiable (as of 2026-07-31) | Public source(s) | Owner-supplied value (the gap) |
|---|---|---|---|---|
| 1 | Model identifier and identity | Yes: identifier matches OpenAI GPT-5.6 Sol (flagship tier), released 2026-07-09, knowledge cutoff Feb 2026 | P1, P2, P3, S1, S2 | Confirm the identifier the owner's provider expects exactly (e.g., `gpt-5.6-sol` vs `gpt5.6-sol` vs `openai/gpt-5.6-sol`) |
| 2 | Base URL | Partial: OpenAI platform base URL and OpenRouter base URLs are public; the owner's provider base URL is not | API reference (5.2); S2 | The provider's exact base URL(s), API version path, and whether it mirrors a public protocol |
| 3 | Authentication | Partial: Bearer-key pattern is the public standard; the owner's credential model is not | API reference; S2 | Auth scheme (Bearer API key, OAuth, header name), key rotation procedure, which environment holds it (DEC-176) |
| 4 | Request schema | Partial: Responses/Chat Completions schemas are public; the owner's endpoint schema is not | API reference; S2 | Endpoint paths, required/optional fields, message/role model, streaming support, parameters (reasoning effort, temperature, max output tokens), maximum request size |
| 5 | Response schema | Partial: public schemas documented; owner's endpoint response shape not | API reference; S2 | Response structure, error envelope, usage/token fields, reasoning-token fields, chunk format if streaming |
| 6 | Structured-output support | Partial: OpenAI documents structured outputs; the owner's endpoint support is not | `platform.openai.com/docs/guides/structured-outputs`; S2 | Whether `response_format`/JSON-schema output is enabled, supported schema features, failure behavior when schema is violated |
| 7 | Tool use | Partial: function calling documented; the owner's endpoint support is not | `platform.openai.com/docs/guides/function-calling`; S2 | Whether tool/function calling is enabled, tool schema limits, tool-call retry semantics, parallel tool calls |
| 8 | Rate limits | Partial: OpenAI documents per-tier limits; the owner's account tier and limits are not | `platform.openai.com/docs/guides/rate-limits` | The owner's plan/tier, requests-per-minute and tokens-per-minute limits, burst vs sustained limits, limit headers returned |
| 9 | Cost | Partial: public list price $5/$30 per 1M for Sol, cache pricing (reads 90%, writes 1.25x, 30-min minimum cache life), 2026-07-30 price update for Terra/Luna | P1; S2 | The owner's actual billed rate, billing unit, invoicing cadence, any reseller markup, monthly cost ceiling for the blog workflow, and how budget overruns pause the pipeline |
| 10 | Context limits | Partial: 1M context listed publicly; effective limit on the owner's deployment not | S2; `platform.openai.com/docs/models` | Maximum input context and maximum output tokens actually enforced, and whether the blog prompts fit with headroom |
| 11 | Retry behavior | Partial: OpenAI documents error semantics/retry guidance; the owner's endpoint behavior not | API reference; S2 | Retryable vs fatal error classes, suggested backoff, timeout recommendations, idempotency support, max-request-duration |
| 12 | Data retention | Partial: OpenAI API policies (no default training use; ZDR option) are public; the owner's provider commitment not | `openai.com/policies/api-data-usage-policies`; P1 | Whether the owner's provider commits to no training on prompts/outputs, retention window for logs, ZDR availability, and how that aligns with DEC-025 boundaries |
| 13 | Availability | Partial: public status page exists; no public SLA verified; the owner's provider terms not | `status.openai.com` | Expected availability, any SLA, incident communication channel, and how availability failures trigger the kill switch (DEC-048, DEC-053) |
| 14 | Compliance and safety policy (context for gate design) | Partial: OpenAI usage policies are public; the owner's provider terms not | `openai.com/policies/usage-policies` (200); `openai.com/policies/` (200) | Provider terms that could restrict generated content or automated publishing, and any content-moderation requirements the pipeline must satisfy |

## 9. Assumptions, uncertainties, and unresolved questions

1. **Material owner input (blocking for design finalization):** the private `gpt5.6-sol` provider documentation (all fields marked "owner-supplied" in Section 8). DEC-051, UX §21.21, and arch §25.3.21 all gate technical design on it.
2. **Reconciliation for the owner:** DEC-051/plan text said the identifier implies no vendor; the public record now identifies the model family as OpenAI GPT-5.6 Sol. The owner must confirm whether their "custom provider" is an OpenAI platform account, an OpenAI-compatible gateway/reseller, Azure/Bedrock hosting, or another path. This is recorded for X2 and the owner review (DEC-183; no silent resolution).
3. **Version drift:** public model families change (knowledge cutoff Feb 2026; price updates on 2026-07-30). The contract must record the provider documentation version and re-verify when provider terms or model versions materially change (DEC-056).
4. **SLA uncertainty:** this research verified a public status page but no public SLA text; any SLA is a matter of the owner's provider terms.
5. **Legacy automation history:** the removed OpenClaw-era stack used an OpenAI-compatible chat-completions response shape (`papyr-reference/docs/29_Papyr_OpenClaw_v1.0.md:923`). This is historical evidence only and does not imply the owner's current provider uses that protocol.

## 10. Dependencies and cross-track interfaces

- **E2** consumes the finalized contract to design the pipeline's provider interface, fail-closed gates, retry policy, and secret handling.
- **E3** is independent of the provider contract except for cadence and gate behavior at runtime.
- **X1/X2** record this brief's mapping (governing decisions DEC-051/048/052/053/121/124; spec sections UX §21.21, arch §25.3.21) and surface the reconciliation item in Section 9.2 to the owner.
- **Technical design** (blocked until owner supply): provider adapter isolation behind an interface (DEC-051), secrets per DEC-176, cost and rate-limit ceilings that feed the pause/kill-switch design (DEC-048, DEC-053, DEC-097).

## 11. Source-date log and evidence-completeness notes

- All sources accessed 2026-07-31. URL currency verified with read-only HTTP checks (HTTP 200) on 2026-07-31 unless noted.
- Legacy evidence: case-insensitive grep of `papyr-reference/` for `gpt5.6`, `gpt5`, `gpt-5`, `openai`, `anthropic`, `gemini`, `base_url`, `api.?key`, `endpoint` found zero LLM-provider references (only REST "endpoint" mentions in backend code and step prompts, unrelated to LLM providers).
- Evidence-completeness caveat: the OpenAI API reference pages were verified live and their canonical content is summarized from the official announcement and catalog pages fetched in full; the API reference pages themselves were not fully re-fetched beyond the HTTP currency check. Public prices/limits are recorded as of 2026-07-31 and are subject to change.

## 12. Prohibitions-compliance statement

- No provider authentication, provider API call, account creation, or access to any provider endpoint was performed.
- No installs, builds, servers, VPS access, deployment, or git writes were performed.
- `papyr-reference/` was only read; read-only `git -C papyr-reference status --porcelain` returned empty output with exit 0 before and after this brief.
- No source, spec, or decision file was modified. The only files created by this brief are this deliverable.
- No model fact was fabricated: every claimed public fact carries a source URL and access date; all remaining contract fields are explicitly marked owner-supplied gaps.
- A chat-only summary is insufficient; this file is the primary deliverable.
