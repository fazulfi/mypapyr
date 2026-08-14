// papyr — memory-only password handling (PT-04)
// =============================================
// Passwords for encrypted PDFs are held only in React state and are never
// written to URLs, localStorage, sessionStorage, analytics, or logs.
// Reviewed against DEC-036, DEC-064, DEC-074, DEC-025, DEC-042.

/** Maximum accepted password length (bytes/UTF-16 code units). */
export const MAX_PASSWORD_LENGTH = 1024;

/** Minimal file metadata needed to decide whether a password is required. */
export interface LockedFileInfo {
  readonly id: string;
  readonly name: string;
  readonly type: string;
  readonly size: number;
  readonly isEncrypted: boolean;
}

const PDF_MIME = "application/pdf";

/** True when the file's MIME type identifies a PDF. */
function isPdfType(type: string): boolean {
  const t = type.trim().toLowerCase();
  if (t === PDF_MIME) return true;
  if (t === "pdf") return true;
  if (t.endsWith(".pdf")) return true;
  return false;
}

/**
 * Decides whether the password field is required for a given file.
 *
 * The field appears ONLY when the file is both a PDF and flagged encrypted —
 * never for plain PDFs, and never for image or other file types.
 */
export function isRequiredForLockedFile(
  file: { type: string; size: number },
  isEncrypted: boolean,
): boolean {
  return isEncrypted && isPdfType(file.type);
}

/** Result of validating a password candidate. */
export type PasswordValidation =
  | { ok: true }
  | { ok: false; reason: "too-long" | "empty" };

/**
 * Validate a password candidate.
 *
 * An empty string is OK because unlocked files submit no password. A value
 * longer than `MAX_PASSWORD_LENGTH` is rejected defensively; every other
 * non-empty value is accepted (actual correctness is decided by the server).
 */
export function validatePassword(pw: string): PasswordValidation {
  if (pw.length === 0) return { ok: true };
  if (pw.length > MAX_PASSWORD_LENGTH) return { ok: false, reason: "too-long" };
  return { ok: true };
}

/**
 * Pure check that a password value has NOT been written to any persistent
 * browser store (localStorage or sessionStorage). Used by tests to prove the
 * memory-only guarantee; the component itself never calls the storage APIs.
 */
export function neverPersist(pw: string): boolean {
  if (typeof window === "undefined") return true;
  const stores: Storage[] = [window.localStorage, window.sessionStorage];
  for (const store of stores) {
    try {
      for (let i = 0; i < store.length; i++) {
        const key = store.key(i);
        if (key !== null && store.getItem(key) === pw) return false;
      }
    } catch {
      // Storage access can throw in privacy-restricted contexts; treat as no match.
    }
  }
  return true;
}

/** Closed set of password-related error kinds. */
export type PasswordErrorKind = "wrong-password" | "corrupt" | "unsupported";

const ERROR_KEYS: Record<PasswordErrorKind, string> = {
  "wrong-password": "WRONG_PASSWORD",
  corrupt: "CORRUPT_FILE",
  unsupported: "UNSUPPORTED_FILE",
};

/**
 * Maps a closed error kind to its stable, machine-readable key string.
 *
 * The keys are distinct so a wrong password can never be confused with a
 * corrupt or unsupported file. Components may map these keys to localized
 * copy when available; the key string is the stable fallback.
 */
export function distinctError(kind: PasswordErrorKind): string {
  return ERROR_KEYS[kind];
}
