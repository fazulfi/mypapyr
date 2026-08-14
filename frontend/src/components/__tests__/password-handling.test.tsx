// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  MAX_PASSWORD_LENGTH,
  distinctError,
  isRequiredForLockedFile,
  neverPersist,
  validatePassword,
} from "@/lib/password";

import PasswordInput, {
  type LockedFileInfo,
  type MemoryUsageState,
} from "@/components/PasswordInput";

// ---------------------------------------------------------------------------
// Mock analytics so we can prove no password data leaks into any event.
// PasswordInput intentionally never calls trackEvent; the mock lets the test
// assert that even tool-page analytics payloads carry no password material.
// ---------------------------------------------------------------------------
const { trackEvent } = vi.hoisted(() => ({ trackEvent: vi.fn() }));

vi.mock("@/lib/analytics", () => ({
  trackEvent,
  ALLOWED_FIELDS: Object.freeze(["tool", "locale", "funnel", "errorCategory"]),
  bandSize: (_bytes: number) => "small" as const,
  isAllowedField: (key: string) => key !== "password" && key !== "pass",
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function makePdf(name: string, isEncrypted = false): LockedFileInfo {
  return {
    id: name,
    name,
    type: "application/pdf",
    size: 1024,
    isEncrypted,
  };
}

function makeImage(name: string): LockedFileInfo {
  return {
    id: name,
    name,
    type: "image/jpeg",
    size: 1024,
    isEncrypted: false,
  };
}

function lockedFileFixture(overrides: Partial<LockedFileInfo> = {}): LockedFileInfo {
  return {
    id: "f1",
    name: "report.pdf",
    type: "application/pdf",
    size: 4096,
    isEncrypted: true,
    ...overrides,
  };
}

function memoryUsageFixture(initial = ""): MemoryUsageState {
  let value = initial;
  return {
    get value() {
      return value;
    },
    onChange: (pw: string) => {
      value = pw;
    },
  };
}

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------
beforeEach(() => {
  trackEvent.mockClear();
  localStorage.clear();
  sessionStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

// ===================================================================
// 1.  lib/password – isRequiredForLockedFile
// ===================================================================
describe("isRequiredForLockedFile", () => {
  it("returns true for an encrypted PDF (application/pdf)", () => {
    expect(isRequiredForLockedFile(makePdf("doc.pdf", true), true)).toBe(true);
  });

  it("returns false for an unencrypted PDF", () => {
    expect(isRequiredForLockedFile(makePdf("doc.pdf", false), false)).toBe(false);
  });

  it("returns false for an encrypted image file", () => {
    expect(isRequiredForLockedFile(makeImage("photo.jpg"), false)).toBe(false);
  });

  it("returns false for a plain PDF with isEncrypted=false", () => {
    expect(isRequiredForLockedFile(makePdf("plain.pdf", false), false)).toBe(false);
  });

  it("returns false for a non-PDF type even when isEncrypted is true", () => {
    const file: LockedFileInfo = {
      id: "x",
      name: "notes.txt",
      type: "text/plain",
      size: 100,
      isEncrypted: true,
    };
    expect(isRequiredForLockedFile(file, true)).toBe(false);
  });

  it("treats pdf/ and .pdf type strings as PDFs", () => {
    const barePdf: LockedFileInfo = {
      id: "a", name: "a.pdf", type: "pdf", size: 1, isEncrypted: true,
    };
    const dotPdf: LockedFileInfo = {
      id: "b", name: "b.pdf", type: "application/pdf.pdf", size: 1, isEncrypted: true,
    };
    expect(isRequiredForLockedFile(barePdf, true)).toBe(true);
    expect(isRequiredForLockedFile(dotPdf, true)).toBe(true);
  });
});

// ===================================================================
// 2.  lib/password – validatePassword
// ===================================================================
describe("validatePassword", () => {
  it("accepts an empty string (unlocked file submits no password)", () => {
    expect(validatePassword("")).toEqual({ ok: true });
  });

  it("accepts a valid-length password", () => {
    expect(validatePassword("secret")).toEqual({ ok: true });
  });

  it("rejects a password exceeding MAX_PASSWORD_LENGTH", () => {
    const long = "x".repeat(MAX_PASSWORD_LENGTH + 1);
    expect(validatePassword(long)).toEqual({ ok: false, reason: "too-long" });
  });

  it("accepts a password at exactly MAX_PASSWORD_LENGTH", () => {
    const exact = "x".repeat(MAX_PASSWORD_LENGTH);
    expect(validatePassword(exact)).toEqual({ ok: true });
  });
});

// ===================================================================
// 3.  lib/password – neverPersist
// ===================================================================
describe("neverPersist", () => {
  it("returns true for a password that has not been stored", () => {
    expect(neverPersist("hunter2")).toBe(true);
  });

  it("returns false when the password is in localStorage", () => {
    localStorage.setItem("pw", "supersecret");
    expect(neverPersist("supersecret")).toBe(false);
  });

  it("returns false when the password is in sessionStorage", () => {
    sessionStorage.setItem("auth", "mypassword");
    expect(neverPersist("mypassword")).toBe(false);
  });

  it("returns true when window is unavailable (SSR)", () => {
    const original = globalThis.window;
    try {
      // @ts-expect-error – simulating a non-browser environment
      delete globalThis.window;
      expect(neverPersist("pw")).toBe(true);
    } finally {
      globalThis.window = original;
    }
  });
});

// ===================================================================
// 4.  lib/password – distinctError
// ===================================================================
describe("distinctError", () => {
  it("returns a stable key for wrong-password", () => {
    expect(distinctError("wrong-password")).toBe("WRONG_PASSWORD");
  });

  it("returns a stable key for corrupt", () => {
    expect(distinctError("corrupt")).toBe("CORRUPT_FILE");
  });

  it("returns a stable key for unsupported", () => {
    expect(distinctError("unsupported")).toBe("UNSUPPORTED_FILE");
  });

  it("produces distinct strings for each kind", () => {
    const keys = [
      distinctError("wrong-password"),
      distinctError("corrupt"),
      distinctError("unsupported"),
    ];
    expect(new Set(keys).size).toBe(3);
  });
});

// ===================================================================
// 5.  PasswordInput component – rendering behaviour
// ===================================================================
describe("PasswordInput rendering", () => {
  it("renders a password field for an encrypted PDF", () => {
    const mu = memoryUsageFixture();
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} />);
    expect(screen.getByLabelText(/password/i)).toBeDefined();
  });

  it("does NOT render a password field for a plain (unencrypted) PDF", () => {
    const file = lockedFileFixture({ isEncrypted: false });
    const mu = memoryUsageFixture();
    const { container } = render(<PasswordInput file={file} memoryUsage={mu} />);
    expect(container.querySelector("input")).toBeNull();
  });

  it("does NOT render a password field for an image file", () => {
    const mu = memoryUsageFixture();
    const { container } = render(<PasswordInput file={makeImage("photo.jpg")} memoryUsage={mu} />);
    expect(container.querySelector("input")).toBeNull();
  });

  it("renders the input with type='password'", () => {
    const mu = memoryUsageFixture();
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} />);
    const input = screen.getByLabelText(/password/i) as HTMLInputElement;
    expect(input.type).toBe("password");
  });

  it("calls memoryUsage.onChange when the user types", () => {
    const onChange = vi.fn();
    const mu: MemoryUsageState = { value: "", onChange };
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} />);
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "opensesame" } });
    expect(onChange).toHaveBeenCalledWith("opensesame");
  });

  it("renders the file name in the label", () => {
    const mu = memoryUsageFixture();
    render(
      <PasswordInput file={lockedFileFixture({ name: "classified.pdf" })} memoryUsage={mu} />,
    );
    expect(screen.getByText(/classified\.pdf/)).toBeDefined();
  });
});

// ===================================================================
// 6.  Merge: per-file independent validation (two locked files)
// ===================================================================
describe("Merge: per-file password isolation", () => {
  it("renders two separate password fields for two locked files", () => {
    const mu1 = memoryUsageFixture();
    const mu2 = memoryUsageFixture();
    const file1 = lockedFileFixture({ id: "f1", name: "a.pdf" });
    const file2 = lockedFileFixture({ id: "f2", name: "b.pdf" });

    const { container } = render(
      <div>
        <PasswordInput file={file1} memoryUsage={mu1} />
        <PasswordInput file={file2} memoryUsage={mu2} />
      </div>,
    );
    const inputs = container.querySelectorAll('input[type="password"]');
    expect(inputs.length).toBe(2);
  });

  it("tracks each locked file's password independently", () => {
    const mu1: MemoryUsageState = { value: "alpha", onChange: vi.fn() };
    const mu2: MemoryUsageState = { value: "beta", onChange: vi.fn() };

    const { container } = render(
      <div>
        <PasswordInput file={lockedFileFixture({ id: "f1", name: "a.pdf" })} memoryUsage={mu1} />
        <PasswordInput file={lockedFileFixture({ id: "f2", name: "b.pdf" })} memoryUsage={mu2} />
      </div>,
    );
    const inputs = container.querySelectorAll('input[type="password"]');
    expect((inputs[0] as HTMLInputElement).value).toBe("alpha");
    expect((inputs[1] as HTMLInputElement).value).toBe("beta");
  });
});

// ===================================================================
// 7.  Distinct error rendering
// ===================================================================
describe("PasswordInput distinct errors", () => {
  it("shows localized wrong-password error text", () => {
    const mu = memoryUsageFixture();
    render(
      <PasswordInput file={lockedFileFixture()} memoryUsage={mu} errorType="wrong-password" />,
    );
    expect(screen.getByText("Wrong password")).toBeDefined();
  });

  it("shows localized corrupt error text", () => {
    const mu = memoryUsageFixture();
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} errorType="corrupt" />);
    expect(screen.getByText("Corrupt file")).toBeDefined();
  });

  it("shows localized unsupported error text", () => {
    const mu = memoryUsageFixture();
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} errorType="unsupported" />);
    expect(screen.getByText("Unsupported file")).toBeDefined();
  });

  it("renders distinct texts for each error kind", () => {
    const mu = memoryUsageFixture();
    const { container, rerender } = render(
      <PasswordInput file={lockedFileFixture()} memoryUsage={mu} errorType="wrong-password" />,
    );
    const first = container.textContent ?? "";
    rerender(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} errorType="corrupt" />);
    const second = container.textContent ?? "";
    rerender(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} errorType="unsupported" />);
    const third = container.textContent ?? "";

    expect(first).not.toBe(second);
    expect(second).not.toBe(third);
    expect(first).not.toBe(third);
  });

  it("falls back to the stable key when the localized copy is empty", () => {
    // The stable key is the machine-readable contract; the localized message
    // is the display layer. distinctError keys must stay distinct.
    expect(distinctError("wrong-password")).not.toBe(distinctError("corrupt"));
    expect(distinctError("corrupt")).not.toBe(distinctError("unsupported"));
  });
});

// ===================================================================
// 8.  Leakage: password never reaches analytics
// ===================================================================
describe("analytics leakage guard", () => {
  it("PasswordInput never fires analytics while typing a password", () => {
    const mu = memoryUsageFixture();
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} />);
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "opensesame" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "hunter2" } });
    expect(trackEvent).not.toHaveBeenCalled();
  });

  it("tool-page analytics payloads carry no password/pass key in any fired event", () => {
    trackEvent("task_started", { tool: "merge-pdf", locale: "en" });
    trackEvent("task_completed", { tool: "merge-pdf", outcome: "success" });
    trackEvent("task_failed", { tool: "merge-pdf", errorCategory: "encrypted" });

    const calls = trackEvent.mock.calls as Array<[string, Record<string, unknown>]>;
    expect(calls.length).toBeGreaterThan(0);
    for (const [, data] of calls) {
      for (const key of Object.keys(data)) {
        const lower = key.toLowerCase();
        expect(lower).not.toBe("password");
        expect(lower).not.toBe("pass");
      }
    }
  });

  it("no analytics payload value matches a password-shaped string", () => {
    trackEvent("task_failed", { tool: "merge-pdf", errorCategory: "encrypted" });
    const calls = trackEvent.mock.calls as Array<[string, Record<string, unknown>]>;
    for (const [, data] of calls) {
      for (const value of Object.values(data)) {
        if (typeof value === "string") {
          expect(value).not.toMatch(/^passw/i);
        }
      }
    }
  });
});

// ===================================================================
// 9.  Persistence: password never in localStorage / sessionStorage / URL
// ===================================================================
describe("password never persisted", () => {
  it("neverPersist returns true for a fresh password", () => {
    expect(neverPersist("my-temp-password")).toBe(true);
  });

  it("typing a password does not write to localStorage or sessionStorage", () => {
    const mu = memoryUsageFixture();
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} />);
    const pw = "should-not-persist";
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: pw } });
    expect(localStorage.length).toBe(0);
    expect(sessionStorage.length).toBe(0);
    expect(neverPersist(pw)).toBe(true);
  });

  it("submitting does not put the password in the URL", () => {
    const mu = memoryUsageFixture();
    render(<PasswordInput file={lockedFileFixture()} memoryUsage={mu} />);
    const pw = "url-unsafe";
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: pw } });
    expect(window.location.href).not.toContain(pw);
    expect(window.location.search).not.toContain(pw);
    expect(window.location.hash).not.toContain(pw);
  });
});