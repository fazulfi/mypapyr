"use client";

// papyr — memory-only password input for encrypted PDFs (PT-04)
// =============================================================
// Renders a password `<input type="password">` ONLY when a locked file is
// detected. The value lives exclusively in React state (via the `memoryUsage`
// prop) and is never written to localStorage, sessionStorage, window.location,
// FormData sent to analytics, or any tracking payload.
//
// Reviewed against DEC-036, DEC-064, DEC-074, DEC-025, DEC-042.

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import {
  type LockedFileInfo,
  type PasswordErrorKind,
  distinctError,
  isRequiredForLockedFile,
} from "@/lib/password";

export type { LockedFileInfo, PasswordErrorKind };

/**
 * Memory-only password state contract.
 *
 * The parent (e.g. a Merge tool page) holds the value in React state — never
 * in a ref, store, URL, closure captured by an analytics callback, or any
 * persisted medium.
 */
export interface MemoryUsageState {
  readonly value: string;
  onChange: (pw: string) => void;
}

interface PasswordInputProps {
  /** File metadata (must include `isEncrypted`). */
  file: LockedFileInfo;
  /** Memory-only password state holder. */
  memoryUsage: MemoryUsageState;
  /** Locale for localized labels and error text. */
  locale?: Locale;
  /** Optional error kind to display. */
  errorType?: PasswordErrorKind;
}

/** Maps an error kind to its localized message key. */
const ERROR_MESSAGE_KEY: Record<PasswordErrorKind, "wrongPassword" | "corrupt" | "unsupported"> = {
  "wrong-password": "wrongPassword",
  corrupt: "corrupt",
  unsupported: "unsupported",
};

/**
 * Resolves the display text for an error kind: localized copy when the
 * message resource is present, otherwise the stable closed key string.
 */
function errorText(
  locale: Locale,
  kind: PasswordErrorKind,
): string {
  const copy = getMessages(locale).password.errors;
  const localized = copy[ERROR_MESSAGE_KEY[kind]];
  return localized.trim() === "" ? distinctError(kind) : localized;
}

/**
 * Renders a labelled password `<input type="password">` when the file is a
 * locked PDF. Returns nothing otherwise.
 */
export default function PasswordInput({
  file,
  memoryUsage,
  locale = "en",
  errorType,
}: PasswordInputProps): React.ReactElement | null {
  const copy = getMessages(locale).password;

  if (!isRequiredForLockedFile(file, file.isEncrypted)) {
    return null;
  }

  const inputId = `password-${file.id}`;
  const errorMessage = errorType ? errorText(locale, errorType) : null;

  return (
    <div className="mb-3">
      <label htmlFor={inputId} className="mb-1 block text-sm font-medium text-gray-700">
        {copy.forFile.replace("{name}", file.name)}
      </label>
      <input
        id={inputId}
        type="password"
        className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        placeholder={copy.placeholder}
        value={memoryUsage.value}
        onChange={(e) => memoryUsage.onChange(e.target.value)}
      />
      {errorMessage && (
        <p className="mt-1 text-xs text-red-600" data-testid="password-error">
          {errorMessage}
        </p>
      )}
    </div>
  );
}