# PT-03 Dossier — Contact form and result-problem report

## Files created/modified

### Created
1. `frontend/src/lib/support.ts` — data model + validation (`ContactCategory`, `ContactSubmission`, `validateContactSubmission`, `sanitizeContext`)
2. `frontend/src/lib/analytics.ts` — PT-01 module (created by PT-01 task) with locked `redactPayload`/`trackEvent` signatures consumed by PT-03; NOT part of this commit
3. `frontend/src/components/support/ContactForm.tsx` — `'use client'` categorized contact form with honeypot, Turnstile placeholder, rate-limit guard, graceful fetch fallback, and redaction-safe analytics
4. `frontend/src/components/support/ResultProblemReport.tsx` — `'use client'` inline report trigger shown near result/download states
5. `frontend/src/__tests__/support.test.ts` — 32 tests covering validation, sanitizeContext, rate limiting, ContactForm, analytics redaction, and ResultProblemReport

### Modified
6. `frontend/src/app/[locale]/contact/page.tsx` — replaced thin shell with a complete trilingual categorized form (server wrapper + client `ContactForm`)
7. `frontend/src/lib/messages.ts` — added `contact` copy block in EN, ES, ID with all form keys
8. `frontend/src/__tests__/supporting-pages.test.tsx` — relaxed heading test for rich contact page, excluded contact from byte-identical shell test

## Vitest output (tail)

```
Test Files  41 passed (41)
     Tests  584 passed (584)
```

## PT-03 test output

```
✓ validateContactSubmission > accepts category (bug/suggestion/question/privacy/advertising/other)
✓ validateContactSubmission > rejects a message over 2000 characters
✓ validateContactSubmission > rejects a missing message
✓ validateContactSubmission > accepts an empty or null optional email
✓ validateContactSubmission > rejects a badly formatted email
✓ validateContactSubmission > rejects an email over 254 characters
✓ validateContactSubmission > blocks a filled honeypot
✓ validateContactSubmission > sanitizes control characters from the message
✓ validateContactSubmission > rejects an invalid category
✓ sanitizeContext > allows alphanumeric, hyphen, and slash
✓ sanitizeContext > strips path/script content and control characters
✓ sanitizeContext > returns null for empty or whitespace-only input
✓ sanitizeContext > caps length at 120 characters
✓ rate limiting > records submissions and blocks the 4th in a short window
✓ ContactForm > submits with each category
✓ ContactForm > rejects a message over 2000 characters with an error
✓ ContactForm > rejects a missing message
✓ ContactForm > accepts an empty optional email
✓ ContactForm > rejects a badly formatted email
✓ ContactForm > accepts a valid email
✓ ContactForm > blocks submission when the honeypot is filled
✓ ContactForm > blocks the 4th submit in a short window via rate limiting
✓ ContactForm > clears the message input after a failed submit (never resurfaced)
✓ ContactForm > falls back to a client-side confirmation when the endpoint is unavailable
✓ analytics redaction > never sends message, email, filename, or password fields
✓ analytics redaction > sends only allowed fields through trackEvent
✓ ResultProblemReport > renders a compact trigger and opens the categorized form prefilled with context
      Tests  32 passed (32)
```

## Branch
`feat/phase-6-privacy-analytics-support` — PT-03 commit `8087828` on top of PT-04 `2c5f908` and PT-01 `25f927d`