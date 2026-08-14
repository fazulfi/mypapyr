# PT-04: Password handling surface verification

## Summary

Created the memory-only password handling surface for encrypted PDF inputs.
The password field appears ONLY when a locked/encrypted PDF is detected, values
live exclusively in React state, and automated guards prove no password data
reaches analytics, localStorage, sessionStorage, or URL parameters.

## Files created

| File | Purpose |
|---|---|
| `frontend/src/lib/password.ts` | Memory-only password helper + validators |
| `frontend/src/components/PasswordInput.tsx` | `"use client"` password input component |
| `frontend/src/components/__tests__/password-handling.test.tsx` | TDD test suite (37 cases) |

## Files modified

| File | Change |
|---|---|
| `frontend/src/lib/messages.ts` | Added `password` message group (label, placeholder, forFile, errors) to EN/ES/ID |

## Key design decisions

- `isRequiredForLockedFile` checks both `isEncrypted` boolean AND PDF MIME type
  (`application/pdf`, `pdf`, `.pdf`) — never shows field for images or plain PDFs.
- `validatePassword("")` returns `{ ok: true }` so unlocked files submit cleanly.
- `neverPersist` scans both `localStorage` and `sessionStorage` at test time
  to prove memory-only compliance (component itself never calls storage APIs).
- `distinctError` returns closed stable keys (`WRONG_PASSWORD`, `CORRUPT_FILE`,
  `UNSUPPORTED_FILE`) that are guaranteed distinct — no risk of category confusion.
- `trackEvent` is never called by PasswordInput, but the test asserts that even
  tool-page analytics payloads carry no `password`/`pass` keys or values.

## Test results

```
$ npx vitest run src/components/__tests__/password-handling.test.tsx

 RUN  v4.1.10 C:/Users/faizz/mypapyr/frontend


 Test Files  1 passed (1)
      Tests  37 passed (37)
   Start at  06:37:45
   Duration  2.76s (transform 190ms, setup 0ms, import 537ms, tests 180ms, environment 1.69s)
```

## Test coverage

1. **isRequiredForLockedFile** (6 tests): encrypted PDF → true; unencrypted PDF → false;
   encrypted image → false; non-PDF encrypted → false; pdf/ and .pdf type strings → true.
2. **validatePassword** (4 tests): empty OK; valid accepted; too-long rejected; MAX boundary.
3. **neverPersist** (4 tests): fresh pw → true; in localStorage → false; in sessionStorage → false; SSR → true.
4. **distinctError** (4 tests): each error kind stable key; all three keys distinct.
5. **PasswordInput rendering** (6 tests): field for encrypted PDF; hidden for plain/image; type=password;
   onChange fires; file name in label.
6. **Merge per-file isolation** (2 tests): two locked files → two input fields; independent state values.
7. **Distinct errors** (5 tests): localized wrong-password/corrupt/unsupported; distinct texts;
   stable key fallback.
8. **Analytics leakage** (3 tests): PasswordInput never fires analytics; no password/pass key in any
   trackEvent payload; no password-shaped values.
9. **Persistence guards** (3 tests): neverPersist true for fresh; no localStorage/sessionStorage growth;
   no URL leakage.