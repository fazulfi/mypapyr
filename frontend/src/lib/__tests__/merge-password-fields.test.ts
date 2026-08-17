// @vitest-environment jsdom
// PT-04 (FR-SHARED-09 / FR-MERGE-04): per-index password fields for merge.

import { afterEach, describe, expect, it } from "vitest";

import { MAX_PASSWORD_LENGTH, neverPersist } from "@/lib/password";
import {
  PASSWORD_FIELD_PREFIX,
  buildPasswordFields,
  fileId,
  reconcilePasswordValues,
} from "@/lib/mergePasswordFields";

function makeFile(name: string, size = 1024, lastModified = 100): File {
  return new File([new Uint8Array(size)], name, { type: "application/pdf", lastModified });
}

afterEach(() => {
  localStorage.clear();
  sessionStorage.clear();
});

describe("buildPasswordFields", () => {
  it("appends a password_<i> field for each encrypted file, in files order", () => {
    const locked = makeFile("a.pdf", 10, 1);
    const plain = makeFile("b.pdf", 20, 2);
    const locked2 = makeFile("c.pdf", 30, 3);
    const ids = new Set([fileId(locked), fileId(locked2)]);
    const values = new Map([
      [fileId(locked), "s3cret-a"],
      [fileId(locked2), "s3cret-c"],
    ]);
    const result = buildPasswordFields([locked, plain, locked2], ids, values);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.fields).toEqual({
      password_0: "s3cret-a",
      password_2: "s3cret-c",
    });
  });

  it("emits no password fields at all for plain-only lists", () => {
    const files = [makeFile("a.pdf"), makeFile("b.pdf")];
    const result = buildPasswordFields(files, new Set(), new Map());
    expect(result).toEqual({ ok: true, fields: {} });
  });

  it("emits an explicit empty field for an encrypted file with no value", () => {
    const locked = makeFile("a.pdf");
    const result = buildPasswordFields([locked], new Set([fileId(locked)]), new Map());
    expect(result).toEqual({ ok: true, fields: { password_0: "" } });
  });

  it("fails the whole submit when a password exceeds MAX_PASSWORD_LENGTH", () => {
    const locked = makeFile("a.pdf");
    const tooLong = "x".repeat(MAX_PASSWORD_LENGTH + 1);
    const result = buildPasswordFields(
      [locked],
      new Set([fileId(locked)]),
      new Map([[fileId(locked), tooLong]]),
    );
    expect(result).toEqual({ ok: false, reason: "too-long", index: 0 });
  });

  it("fails with the offending index when a later file is too long", () => {
    const plain = makeFile("a.pdf");
    const locked = makeFile("b.pdf");
    const result = buildPasswordFields(
      [plain, locked],
      new Set([fileId(locked)]),
      new Map([[fileId(locked), "y".repeat(MAX_PASSWORD_LENGTH + 1)]]),
    );
    expect(result).toEqual({ ok: false, reason: "too-long", index: 1 });
  });

  it("leaves no password in localStorage or sessionStorage after building fields", () => {
    const locked = makeFile("a.pdf");
    const value = "never-persisted-123";
    buildPasswordFields([locked], new Set([fileId(locked)]), new Map([[fileId(locked), value]]));
    expect(neverPersist(value)).toBe(true);
  });
});

describe("reconcilePasswordValues", () => {
  it("drops values for removed files", () => {
    const keep = makeFile("a.pdf");
    const removed = makeFile("b.pdf");
    const values = new Map([
      [fileId(keep), "keep-pw"],
      [fileId(removed), "gone-pw"],
    ]);
    const next = reconcilePasswordValues([keep], new Set([fileId(keep), fileId(removed)]), values);
    expect(next.has(fileId(removed))).toBe(false);
    expect(next.get(fileId(keep))).toBe("keep-pw");
  });

  it("prunes entries for files that are no longer encrypted", () => {
    const file = makeFile("a.pdf");
    const next = reconcilePasswordValues([file], new Set(), new Map([[fileId(file), "pw"]]));
    expect(next.size).toBe(0);
  });

  it("seeds an empty value for newly added encrypted files", () => {
    const file = makeFile("a.pdf");
    const next = reconcilePasswordValues([file], new Set([fileId(file)]), new Map());
    expect(next.get(fileId(file))).toBe("");
  });

  it("reconciles with an empty file list (reset) to an empty map", () => {
    const next = reconcilePasswordValues([], new Set(), new Map([["x", "pw"]]));
    expect(next.size).toBe(0);
  });
});

describe("fileId", () => {
  it("is stable across calls for the same file metadata", () => {
    const a = makeFile("r.pdf", 2048, 42);
    const b = makeFile("r.pdf", 2048, 42);
    expect(fileId(a)).toBe(fileId(b));
  });

  it("distinguishes files that differ in name, size, or lastModified", () => {
    expect(fileId(makeFile("a.pdf", 1, 1))).not.toBe(fileId(makeFile("b.pdf", 1, 1)));
    expect(fileId(makeFile("a.pdf", 1, 1))).not.toBe(fileId(makeFile("a.pdf", 2, 1)));
    expect(fileId(makeFile("a.pdf", 1, 1))).not.toBe(fileId(makeFile("a.pdf", 1, 2)));
  });
});

describe("contract constants", () => {
  it("uses the password_ prefix the backend expects", () => {
    expect(PASSWORD_FIELD_PREFIX).toBe("password_");
  });
});
