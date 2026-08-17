// papyr — per-index password contract for the Merge PDF multipart upload (PT-04)
// ==============================================================================
// The frontend sends each encrypted file's password as a `password_<i>` multipart
// text field, where `i` is the file's position in the `files` order (0-based).
// Plain files get NO password field at all; an encrypted file with an empty
// password sends the field explicitly with an empty value so the server can
// distinguish "no password supplied" from "explicit empty password" (the latter
// is valid for documents whose user password is empty).
//
// The server contract (backend/app/routers/merge.py) mirrors this exactly:
// only `password_<i>` fields with 0 <= i < fileCount are accepted, values are
// capped at 1024 UTF-8 bytes, and every password is consumed at the sanitizer
// stage — never persisted, logged, or echoed.
//
// Values must only ever live in React state; this module is a pure function and
// never touches storage, URLs, analytics, or logs.

import { validatePassword, type PasswordValidation } from "@/lib/password";

export const PASSWORD_FIELD_PREFIX = "password_";

/** Minimal per-file metadata the password mapping keys on. */
export interface PasswordFileInfo {
  readonly name: string;
  readonly size: number;
  readonly lastModified?: number;
}

/** Stable per-file identifier (FR-MERGE-04 keeps each password independent). */
export function fileId(file: PasswordFileInfo): string {
  return file.name + ":" + String(file.size) + ":" + String(file.lastModified ?? 0);
}

/** Result of assembling the per-index password fields for a file list. */
export type MergePasswordResult =
  | { ok: true; fields: Record<string, string> }
  | { ok: false; reason: Extract<PasswordValidation, { ok: false }>["reason"]; index: number };

/**
 * Builds the `password_<i>` multipart fields for `files` from per-id values.
 *
 * A password is emitted ONLY for encrypted files (identified by `isEncrypted`
 * on the locked-file record). Plain files are omitted entirely; encrypted files
 * with an empty value still emit the field (explicit empty). Any value longer
 * than `MAX_PASSWORD_LENGTH` fails the whole submit.
 */
export function buildPasswordFields(
  files: PasswordFileInfo[],
  encryptedIds: ReadonlySet<string>,
  values: ReadonlyMap<string, string>,
): MergePasswordResult {
  const fields: Record<string, string> = {};
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (!isEncryptedFile(file, encryptedIds)) continue;
    const id = fileId(file);
    const value = values.get(id) ?? "";
    const check = validatePassword(value);
    if (!check.ok) {
      return { ok: false, reason: check.reason, index: i };
    }
    fields[PASSWORD_FIELD_PREFIX + String(i)] = value;
  }
  return { ok: true, fields };
}

function isEncryptedFile(file: PasswordFileInfo, encryptedIds: ReadonlySet<string>): boolean {
  return file.type === "application/pdf" && encryptedIds.has(fileId(file));
}

export interface PasswordFileInfo {
  readonly name: string;
  readonly size: number;
  readonly lastModified?: number;
  readonly type: string;
}

export function reconcilePasswordValues(
  files: PasswordFileInfo[],
  encryptedIds: ReadonlySet<string>,
  values: ReadonlyMap<string, string>,
): Map<string, string> {
  const next = new Map<string, string>();
  for (const file of files) {
    if (!isEncryptedFile(file, encryptedIds)) continue;
    const id = fileId(file);
    next.set(id, values.get(id) ?? "");
  }
  return next;
}
