// @vitest-environment jsdom
// PT-01: Leakage guards for the analytics pipeline.
// Asserts that prohibited fields never escape the redaction layer and that the
// schema module itself carries no prohibited key in its exported shapes.

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ALLOWED_FIELDS,
  bandSize,
  isAllowedField,
  isOptedOut,
  redactPayload,
  trackEvent,
} from "../lib/analytics";
import { PROHIBITED_FIELD_NAMES, isProhibitedFieldName } from "../lib/analytics-schema";
import * as schema from "../lib/analytics-schema";

type VaSink = ReturnType<typeof vi.fn>;

function mockVa(): VaSink {
  return (window as Window & { va?: VaSink }).va as VaSink;
}

// ---------------------------------------------------------------------------
// 1. redactPayload strips every prohibited key
// ---------------------------------------------------------------------------

describe("redactPayload strips prohibited keys", () => {
  it("drops a payload containing a mock filename", () => {
    const payload = { page: "/compress", filename: "tax-return.pdf" };
    const result = redactPayload(payload);
    expect(result).toEqual({ page: "/compress" });
    expect(result).not.toHaveProperty("filename");
  });

  it("drops an objectKey field", () => {
    const payload = { locale: "en", objectKey: "tmp/2026/a1b2c3.pdf" };
    const result = redactPayload(payload);
    expect(result).toEqual({ locale: "en" });
    expect(result).not.toHaveProperty("objectKey");
  });

  it("drops a signedUrl field", () => {
    const payload = { page: "/download", signedUrl: "https://r2.example.com/sign?token=abc" };
    const result = redactPayload(payload);
    expect(result).toEqual({ page: "/download" });
    expect(result).not.toHaveProperty("signedUrl");
  });

  it("drops a password field", () => {
    const payload = { page: "/merge", password: "hunter2" };
    const result = redactPayload(payload);
    expect(result).toEqual({ page: "/merge" });
    expect(result).not.toHaveProperty("password");
  });

  it("drops multiple prohibited keys in one pass", () => {
    const payload = {
      page: "/compress",
      locale: "en",
      filename: "doc.pdf",
      objectKey: "tmp/xxx",
      signedUrl: "https://r2.example.com/s?t=abc",
      password: "secret",
      pass: "secret2",
      tool: "compress-pdf",
    };
    const result = redactPayload(payload);
    expect(Object.keys(result).sort()).toEqual(["locale", "page", "tool"]);
  });

  it("coerces a prohibited-string value in an allowed field to a stub", () => {
    const payload = { referrer: "my-document.pdf", page: "/compress" };
    const result = redactPayload(payload);
    expect(result).toEqual({ referrer: "[redacted]", page: "/compress" });
  });
});

// ---------------------------------------------------------------------------
// 2. Raw error string is NOT sent — only errorCategory
// ---------------------------------------------------------------------------

describe("raw error → errorCategory mapping", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { va: vi.fn() });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("maps a string error to errorCategory without sending the raw string", () => {
    trackEvent("task_failed", { page: "/compress", error: "invalid file" });
    const va = mockVa();
    expect(va).toHaveBeenCalledTimes(1);
    const call = va.mock.calls[0] as [string, Record<string, unknown>];
    expect(call[0]).toBe("event");
    expect(call[1]).toHaveProperty("errorCategory", "invalid-file");
    expect(call[1]).not.toHaveProperty("error");
  });

  it("maps an Error object to errorCategory", () => {
    trackEvent("task_failed", { page: "/compress", error: new Error("limit exceeded") });
    const va = mockVa();
    expect(va).toHaveBeenCalledTimes(1);
    const call = va.mock.calls[0] as [string, Record<string, unknown>];
    expect(call[1]).toHaveProperty("errorCategory", "limit-exceeded");
    expect(call[1]).not.toHaveProperty("error");
  });

  it("maps a message string to errorCategory", () => {
    trackEvent("task_failed", { page: "/merge", message: "server unavailable" });
    const va = mockVa();
    expect(va).toHaveBeenCalledTimes(1);
    const call = va.mock.calls[0] as [string, Record<string, unknown>];
    expect(call[1]).toHaveProperty("errorCategory", "server-unavailable");
    expect(call[1]).not.toHaveProperty("message");
  });

  it("maps an unknown error string to internal", () => {
    trackEvent("task_failed", { error: "something went wrong" });
    const va = mockVa();
    expect(va).toHaveBeenCalledTimes(1);
    const call = va.mock.calls[0] as [string, Record<string, unknown>];
    expect(call[1]).toHaveProperty("errorCategory", "internal");
  });
});

// ---------------------------------------------------------------------------
// 3. bandSize boundaries
// ---------------------------------------------------------------------------

describe("bandSize boundaries", () => {
  it("maps 0 to small", () => expect(bandSize(0)).toBe("small"));
  it("maps 1048576 (1 MiB) to small", () => expect(bandSize(1048576)).toBe("small"));
  it("maps 1048577 (>1 MiB) to medium", () => expect(bandSize(1048577)).toBe("medium"));
  it("maps 10485760 (10 MiB) to medium", () => expect(bandSize(10485760)).toBe("medium"));
  it("maps 10485761 (>10 MiB) to large", () => expect(bandSize(10485761)).toBe("large"));
  it("maps -1 to small (negative sentinel)", () => expect(bandSize(-1)).toBe("small"));
});

// ---------------------------------------------------------------------------
// 4. Opted-out client does NOT call window.va
// ---------------------------------------------------------------------------

describe("opt-out prevents window.va calls", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { va: vi.fn() });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("does not call va when doNotTrack is 1", () => {
    vi.stubGlobal("navigator", { doNotTrack: "1" });
    trackEvent("test");
    expect(mockVa()).not.toHaveBeenCalled();
  });

  it("does not call va when _papyrAnalyticsOptOut is true", () => {
    vi.stubGlobal("navigator", {});
    (window as unknown as Record<string, unknown>)._papyrAnalyticsOptOut = true;
    trackEvent("test");
    expect(mockVa()).not.toHaveBeenCalled();
  });

  it("does not call va when globalPrivacyControl is true", () => {
    vi.stubGlobal("navigator", { globalPrivacyControl: true });
    trackEvent("test");
    expect(mockVa()).not.toHaveBeenCalled();
  });

  it("calls va when none of the opt-out signals are set", () => {
    vi.stubGlobal("navigator", {});
    trackEvent("test", { page: "/compress" });
    expect(mockVa()).toHaveBeenCalledTimes(1);
  });
});

// ---------------------------------------------------------------------------
// 5. Only allowed keys pass through (schema validation gate)
// ---------------------------------------------------------------------------

describe("schema validation gate — only allowed keys survive", () => {
  it("redactPayload keeps only allowed keys by default", () => {
    const payload = {
      page: "/compress",
      locale: "en",
      tool: "compress-pdf",
      mode: "server",
      filename: "tax.pdf",
      objectKey: "tmp/xxx",
      error: "some error",
    };
    const result = redactPayload(payload);
    const keys = Object.keys(result).sort();
    expect(keys).toEqual(["locale", "mode", "page", "tool"]);
  });

  it("isAllowedField validates correctly", () => {
    expect(isAllowedField("page")).toBe(true);
    expect(isAllowedField("locale")).toBe(true);
    expect(isAllowedField("errorCategory")).toBe(true);
    expect(isAllowedField("filename")).toBe(false);
    expect(isAllowedField("password")).toBe(false);
    expect(isAllowedField("unknown_field")).toBe(false);
  });

  it("respects a custom allowedKeys set", () => {
    const payload = { page: "/compress", locale: "en", tool: "compress-pdf" };
    const result = redactPayload(payload, ["page"]);
    expect(Object.keys(result).sort()).toEqual(["page"]);
  });
});

// ---------------------------------------------------------------------------
// 6. No prohibited key name appears in analytics-schema.ts exported shapes
// ---------------------------------------------------------------------------

describe("schema module has no prohibited key in exported shapes", () => {
  /**
   * Walk an exported value and fail if any object key it exposes is a
   * prohibited field name. Arrays and Sets expose numeric/indices — not keys —
   * so neither counts as a field name exposure.
   */
  function assertNoProhibitedKeys(value: unknown, path: string): void {
    if (value === null || typeof value !== "object") return;
    if (Array.isArray(value)) {
      value.forEach((item, index) => assertNoProhibitedKeys(item, `${path}[${index}]`));
      return;
    }
    for (const [key, nested] of Object.entries(value)) {
      expect(
        isProhibitedFieldName(key),
        `prohibited key "${key}" found in exported shape ${path}`,
      ).toBe(false);
      assertNoProhibitedKeys(nested, `${path}.${key}`);
    }
  }

  it("no exported shape from analytics-schema exposes a prohibited key", () => {
    for (const [name, value] of Object.entries(schema)) {
      if (typeof value === "object" && value !== null) {
        assertNoProhibitedKeys(value, `analytics-schema.${name}`);
      }
    }
  });

  it("ALLOWED_FIELDS does not contain any prohibited name", () => {
    for (const field of ALLOWED_FIELDS) {
      expect(isProhibitedFieldName(field)).toBe(false);
    }
  });

  it("every prohibited name is listed in PROHIBITED_FIELD_NAMES", () => {
    const prohibitedArray: readonly string[] = PROHIBITED_FIELD_NAMES;
    const check = (name: string) => expect(prohibitedArray.includes(name)).toBe(true);
    check("filename");
    check("objectKey");
    check("signedUrl");
    check("password");
  });
});