import { describe, expect, it } from "vitest";

import { disambiguateName, safeFileName } from "../naming";

const MAX_NAME_LENGTH = 120;

describe("lib/naming safeFileName", () => {
  it("strips control characters and filesystem-illegal characters", () => {
    expect(safeFileName('a<b>c"d:e|f?g*.pdf', "source")).toBe("abcdefg.pdf");
    expect(safeFileName("report\u0000\u001f.pdf", "source")).toBe("report.pdf");
  });

  it("trims trailing dots and spaces", () => {
    expect(safeFileName("report. ", "source")).toBe("report");
    expect(safeFileName("report...", "source")).toBe("report");
  });

  it("behaves identically across all three scopes", () => {
    const input = 'a<b>c"d:e|f?g*.pdf';
    const source = safeFileName(input, "source");
    expect(safeFileName(input, "zip")).toBe(source);
    expect(safeFileName(input, "one-per-page")).toBe(source);
  });

  it("enforces the 120-char total bound while preserving the extension", () => {
    const long = `${"x".repeat(300)}.pdf`;
    const result = safeFileName(long, "zip");
    expect(result.length).toBe(MAX_NAME_LENGTH);
    expect(result.endsWith(".pdf")).toBe(true);
    expect(result.startsWith("x".repeat(MAX_NAME_LENGTH - 4))).toBe(true);
  });

  it("falls back to document when the sanitized result is empty", () => {
    expect(safeFileName("///", "source")).toBe("document");
    expect(safeFileName("\u0000\u0001", "source")).toBe("document");
  });

  it("falls back to a document name prefix when the extension alone exceeds the bound", () => {
    const result = safeFileName(`x.${"y".repeat(200)}`, "zip");
    expect(result.length).toBe(MAX_NAME_LENGTH);
    expect(result.startsWith("document.")).toBe(true);
  });
});

describe("lib/naming disambiguateName", () => {
  it("returns the name unchanged when it is not already used", () => {
    expect(disambiguateName("report.pdf", new Set(["other.pdf"]))).toBe("report.pdf");
  });

  it("inserts a numeric suffix before the extension on collision", () => {
    expect(disambiguateName("report.pdf", new Set(["report.pdf"]))).toBe("report 2.pdf");
  });

  it("keeps incrementing until a free name is found", () => {
    const used = new Set(["report.pdf", "report 2.pdf"]);
    expect(disambiguateName("report.pdf", used)).toBe("report 3.pdf");
  });

  it("appends the numeric suffix when there is no extension", () => {
    expect(disambiguateName("report", new Set(["report"]))).toBe("report 2");
  });
});
