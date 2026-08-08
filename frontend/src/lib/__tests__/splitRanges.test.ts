import { describe, expect, it } from "vitest";

import {
  MAX_RANGE_SPEC_LENGTH,
  MAX_SPLIT_OUTPUTS,
  canonicalRangeSpec,
  parseRangeSpec,
} from "../splitRanges";

describe("splitRanges/parseRangeSpec default mode", () => {
  it("treats an empty spec as the default one-output-per-page mode", () => {
    expect(parseRangeSpec("")).toEqual({ ok: true, ranges: [], canonical: "" });
  });

  it("treats a whitespace-only spec as the default mode", () => {
    expect(parseRangeSpec("   ")).toEqual({ ok: true, ranges: [], canonical: "" });
  });
});

describe("splitRanges/parseRangeSpec grammar parity with admission", () => {
  it("parses single pages and ascending ranges preserving order", () => {
    const result = parseRangeSpec("1-3,5,7-9");
    expect(result).toEqual({
      ok: true,
      ranges: [
        { start: 1, end: 3 },
        { start: 5, end: 5 },
        { start: 7, end: 9 },
      ],
      canonical: "1-3,5,7-9",
    });
  });

  it("canonicalizes surrounding token whitespace away", () => {
    const result = parseRangeSpec("  1-3 ,  5  ");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.canonical).toBe("1-3,5");
    }
  });

  it("preserves duplicates and overlapping ranges as independent ordered outputs", () => {
    const result = parseRangeSpec("2-4,1,2-4");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.ranges).toEqual([
        { start: 2, end: 4 },
        { start: 1, end: 1 },
        { start: 2, end: 4 },
      ]);
      expect(result.canonical).toBe("2-4,1,2-4");
    }
  });

  it("rejects inner whitespace inside a range token", () => {
    expect(parseRangeSpec("1 - 3")).toEqual({ ok: false, error: "malformed" });
  });

  it("rejects malformed tokens", () => {
    for (const spec of ["abc", "1-", "-3", "1-2-3", "1,,2", "1,2,", ",", "1;2"]) {
      expect(parseRangeSpec(spec), `spec ${JSON.stringify(spec)}`).toEqual({
        ok: false,
        error: "malformed",
      });
    }
  });

  it("rejects zero page numbers", () => {
    expect(parseRangeSpec("0")).toEqual({ ok: false, error: "zero" });
    expect(parseRangeSpec("0-5")).toEqual({ ok: false, error: "zero" });
  });

  it("rejects reversed ranges", () => {
    expect(parseRangeSpec("5-2")).toEqual({ ok: false, error: "reversed" });
    expect(parseRangeSpec("1,9-4")).toEqual({ ok: false, error: "reversed" });
  });

  it("accepts an equal-start-end range as a single page", () => {
    const result = parseRangeSpec("4-4");
    expect(result).toEqual({ ok: true, ranges: [{ start: 4, end: 4 }], canonical: "4" });
  });

  it("rejects page numbers beyond safe-integer precision", () => {
    expect(parseRangeSpec("99999999999999999999")).toEqual({ ok: false, error: "malformed" });
  });
});

describe("splitRanges/parseRangeSpec limits", () => {
  const LONG_RANGE = "123456789012345-123456789012345";

  it(`rejects specs longer than ${MAX_RANGE_SPEC_LENGTH} characters`, () => {
    const spec = Array(65).fill(LONG_RANGE).join(",");
    expect(spec.length).toBeGreaterThan(MAX_RANGE_SPEC_LENGTH);
    expect(parseRangeSpec(spec)).toEqual({ ok: false, error: "tooLong" });
  });

  it(`accepts a spec of exactly ${MAX_RANGE_SPEC_LENGTH} characters`, () => {
    const spec = Array(62).fill(LONG_RANGE).join(",") + ",1234567890123456";
    expect(spec.length).toBe(MAX_RANGE_SPEC_LENGTH);
    const result = parseRangeSpec(spec);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.ranges).toHaveLength(63);
    }
  });

  it(`rejects more than ${MAX_SPLIT_OUTPUTS} outputs`, () => {
    const spec = Array.from({ length: MAX_SPLIT_OUTPUTS + 1 }, (_, index) => `${index + 1}`).join(
      ",",
    );
    expect(parseRangeSpec(spec)).toEqual({ ok: false, error: "tooManyOutputs" });
  });

  it(`accepts exactly ${MAX_SPLIT_OUTPUTS} outputs`, () => {
    const spec = Array.from({ length: MAX_SPLIT_OUTPUTS }, (_, index) => `${index + 1}`).join(",");
    const result = parseRangeSpec(spec);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.ranges).toHaveLength(MAX_SPLIT_OUTPUTS);
    }
  });
});

describe("splitRanges/canonicalRangeSpec", () => {
  it("serializes single pages without a hyphen and ranges with one", () => {
    expect(
      canonicalRangeSpec([
        { start: 1, end: 3 },
        { start: 5, end: 5 },
      ]),
    ).toBe("1-3,5");
  });

  it("serializes an empty range list to an empty string", () => {
    expect(canonicalRangeSpec([])).toBe("");
  });
});
