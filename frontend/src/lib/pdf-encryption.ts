/**
 * Client-side encrypted-PDF detection (PT-04 / FR-SHARED-09).
 *
 * Reads the first `SCAN_BYTES` of a PDF File and searches for the `/Encrypt`
 * cross-reference or object marker. This is a heuristic: encrypted PDFs must
 * advertise an `/Encrypt` entry in the trailer or a root-object dictionary.
 * False negatives are possible (e.g. a fragmented /Encrypt beyond the scan
 * window), but extremely rare for well-formed PDFs. This module never reads
 * the full file into memory.
 *
 * Designed to run from a client component's effect or before-submit check;
 * the result feeds the `isEncrypted` field of `LockedFileInfo`.
 */

/** Number of bytes scanned from the start of the PDF file for encryption markers. */
export const SCAN_BYTES = 4096;

/**
 * Returns `true` when the file's first `SCAN_BYTES` contain the `/Encrypt`
 * marker that indicates a password-protected PDF.
 *
 * On read errors, returns `false` (fail-safe: the absent detection is no
 * worse than the current behaviour, and the server-side sanitizer will
 * refuse the file if a password is actually needed).
 */
export async function isEncryptedPdf(file: File): Promise<boolean> {
  // Only attempt detection for PDF files.
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    return false;
  }

  try {
    const slice = file.slice(0, Math.min(file.size, SCAN_BYTES));
    const bytes = await readAsText(slice);
    return /\/Encrypt\b/.test(bytes);
  } catch {
    return false;
  }
}

async function readAsText(blob: Blob): Promise<string> {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result as string) ?? "");
    reader.onerror = () => reject(reader.error ?? new Error("FileReader error"));
    reader.readAsText(blob);
  });
}
