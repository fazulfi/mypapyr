/**
 * PT-03 Support data model and validation.
 *
 * Provides the `ContactSubmission` interface, closed-enum `ContactCategory`,
 * validation logic, and sanitizers for page/locale context.
 * No names, phone numbers, or attachment fields.
 */

/* ─── Constants ─── */

export const MAX_MESSAGE_LENGTH = 2000;
export const EMAIL_MAX_LENGTH = 254;

/** Categories that map to the approved PT-03 contact taxonomy. */
export const CONTACT_CATEGORIES = [
  "bug",
  "suggestion",
  "question",
  "privacy",
  "advertising",
  "other",
] as const;

export type ContactCategory = (typeof CONTACT_CATEGORIES)[number];

/* ─── Interfaces ─── */

export interface ContactSubmission {
  category: ContactCategory;
  message: string;
  email?: string | null;
  page?: string | null;
  locale?: string | null;
}

/* ─── Validation ─── */

/** Raw input shape expected from the form. */
export interface RawContactInput {
  category: string;
  message: string;
  email?: string | null;
  /** Honeypot — if filled, the submission is spam. */
  _hp?: string | null;
}

type ValidationOk = { ok: true; value: ContactSubmission };
type ValidationErr = { ok: false; errors: string[] };
export type ValidationResult = ValidationOk | ValidationErr;

/**
 * Strips ASCII control characters (U+0000–U+001F excluding tab/newline) from a string.
 */
function stripControlChars(value: string): string {
  return value.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, "");
}

/**
 * Validates and sanitises a raw contact form submission.
 *
 * - Trims and strips control chars from all fields.
 * - Enforces maximum lengths.
 * - Basic email format check (optional field).
 * - Honeypot detection.
 */
export function validateContactSubmission(raw: RawContactInput): ValidationResult {
  const errors: string[] = [];

  // ── Honey pot ──
  if (raw._hp && raw._hp.trim().length > 0) {
    // Silently reject — do not reveal the honeypot's presence
    return { ok: false, errors: ["Submission rejected"] };
  }

  // ── Category ──
  const categoryRaw = stripControlChars(raw.category ?? "").trim();
  if (!(CONTACT_CATEGORIES as readonly string[]).includes(categoryRaw)) {
    errors.push("Invalid category");
  }

  // ── Message ──
  const messageRaw = stripControlChars(raw.message ?? "").trim();
  if (messageRaw.length === 0) {
    errors.push("Message is required");
  } else if (messageRaw.length > MAX_MESSAGE_LENGTH) {
    errors.push(`Message must be at most ${MAX_MESSAGE_LENGTH} characters`);
  }

  // ── Email (optional) ──
  let email: string | null = null;
  if (raw.email !== undefined && raw.email !== null && raw.email.trim().length > 0) {
    email = stripControlChars(raw.email).trim();
    if (email.length > EMAIL_MAX_LENGTH) {
      errors.push(`Email must be at most ${EMAIL_MAX_LENGTH} characters`);
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.push("Invalid email format");
    }
  }

  if (errors.length > 0) {
    return { ok: false, errors };
  }

  const value: ContactSubmission = {
    category: categoryRaw as ContactCategory,
    message: messageRaw,
    email: email ?? null,
    page: null,
    locale: null,
  };

  return { ok: true, value };
}

/* ─── Context sanitizer ─── */

/**
 * Sanitizes page and locale context strings for use in contact submissions.
 *
 * - Allows alphanumeric characters, hyphens, slashes (for paths).
 * - Caps length at 120 characters each.
 * - Returns `null` for empty, whitespace-only, or excessively long strings.
 */
export function sanitizeContext(
  page?: string | null,
  locale?: string | null,
): { page: string | null; locale: string | null } {
  const sanitized: { page: string | null; locale: string | null } = {
    page: null,
    locale: null,
  };

  if (page && typeof page === "string") {
    const cleaned = page.replace(/[^a-zA-Z0-9\-\/]/g, "").trim();
    if (cleaned.length > 0 && cleaned.length <= 120) {
      sanitized.page = cleaned;
    }
  }

  if (locale && typeof locale === "string") {
    const cleaned = locale.replace(/[^a-zA-Z0-9\-\/]/g, "").trim();
    if (cleaned.length > 0 && cleaned.length <= 120) {
      sanitized.locale = cleaned;
    }
  }

  return sanitized;
}
