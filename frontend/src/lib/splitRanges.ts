// Split PDF range grammar mirror of backend/app/services/split_service.py:parse_range_spec.
// One token is a single page ("5") or an inclusive ascending range ("1-3"); tokens are
// comma-separated and trimmed, so surrounding whitespace is canonicalized away while inner
// whitespace ("1 - 3") fails the token regex. Page bounds are unknown client-side and are
// only enforced by admission after upload, so validation here never invents page limits.

export interface ParsedRange {
  start: number;
  end: number;
}

export type RangeValidationError = "malformed" | "reversed" | "zero" | "tooManyOutputs" | "tooLong";

export type RangeSpecResult =
  | { ok: true; ranges: ParsedRange[]; canonical: string }
  | { ok: false; error: RangeValidationError };

export const MAX_RANGE_SPEC_LENGTH = 2000;
export const MAX_SPLIT_OUTPUTS = 100;

const RANGE_TOKEN_RE = /^(\d+)(?:-(\d+))?$/;

export function parseRangeSpec(raw: string): RangeSpecResult {
  const spec = raw.trim();
  if (spec === "") {
    return { ok: true, ranges: [], canonical: "" };
  }
  if (spec.length > MAX_RANGE_SPEC_LENGTH) {
    return { ok: false, error: "tooLong" };
  }
  const ranges: ParsedRange[] = [];
  for (const part of spec.split(",")) {
    const token = part.trim();
    const match = RANGE_TOKEN_RE.exec(token);
    if (match === null) return { ok: false, error: "malformed" };
    const start = Number.parseInt(match[1], 10);
    const end = Number.parseInt(match[2] ?? match[1], 10);
    // Values beyond safe-integer precision cannot be compared reliably; admission
    // rejects such page numbers via bounds checks anyway.
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end)) {
      return { ok: false, error: "malformed" };
    }
    if (start < 1) return { ok: false, error: "zero" };
    if (end < start) return { ok: false, error: "reversed" };
    ranges.push({ start, end });
  }
  if (ranges.length > MAX_SPLIT_OUTPUTS) {
    return { ok: false, error: "tooManyOutputs" };
  }
  return { ok: true, ranges, canonical: canonicalRangeSpec(ranges) };
}

export function canonicalRangeSpec(ranges: readonly ParsedRange[]): string {
  return ranges
    .map((range) => (range.start === range.end ? `${range.start}` : `${range.start}-${range.end}`))
    .join(",");
}
