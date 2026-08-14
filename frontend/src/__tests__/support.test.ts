// @vitest-environment jsdom
// PT-03: Contact form + result-problem report tests.
//
// Covers: category submits/validation, message length limits, optional email,
// honeypot blocking, client-side rate limiting, error-state content privacy
// (submitted content never resurfaced), sanitizeContext, and analytics
// redaction (events never contain message/email/filename/password).
//
// NOTE: named `.ts` (per the PT-03 task) so component renders use
// `createElement` instead of JSX.

import { createElement } from "react";
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { redactPayload, trackEvent } from "../lib/analytics";
import { getMessages } from "../lib/messages";
import {
  CONTACT_CATEGORIES,
  MAX_MESSAGE_LENGTH,
  sanitizeContext,
  validateContactSubmission,
} from "../lib/support";

import { ContactForm, isRateLimited, recordSubmission } from "../components/support/ContactForm";
import { ResultProblemReport } from "../components/support/ResultProblemReport";

/* ─── Helpers ─── */

const EN = getMessages("en");

/** Shape of the Vercel Analytics event sink exposed on `window.va`. */
type VaSink = (type: string, payload?: Record<string, unknown>) => void;

function getVaSink(): VaSink | undefined {
  return (window as Window & { va?: VaSink }).va;
}

function selectCategory(value: string): void {
  fireEvent.change(screen.getByLabelText(EN.contact.categoryLabel), {
    target: { value },
  });
}

function typeMessage(value: string): void {
  fireEvent.change(screen.getByLabelText(EN.contact.messageLabel), {
    target: { value },
  });
}

function typeEmail(value: string): void {
  fireEvent.change(screen.getByLabelText(/Email/), { target: { value } });
}

async function submitForm(): Promise<void> {
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: EN.contact.submit }));
  });
}

const memoryStore = new Map<string, string>();

beforeEach(() => {
  memoryStore.clear();
  vi.stubGlobal("window", {
    va: vi.fn(),
    localStorage: {
      getItem: (key: string) => memoryStore.get(key) ?? null,
      setItem: (key: string, value: string) => {
        memoryStore.set(key, value);
      },
      removeItem: (key: string) => {
        memoryStore.delete(key);
      },
    },
  });
  vi.stubGlobal("navigator", {});
  vi.stubGlobal("fetch", vi.fn());
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-08-15T00:00:00Z"));
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});


/* ─── Validation (support.ts) ─── */

describe("validateContactSubmission", () => {
  it.each(CONTACT_CATEGORIES)("accepts category %s", (category) => {
    const result = validateContactSubmission({ category, message: "Hello" });
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.category).toBe(category);
      expect(result.value.message).toBe("Hello");
    }
  });

  it("rejects a message over 2000 characters", () => {
    const result = validateContactSubmission({
      category: "bug",
      message: "x".repeat(MAX_MESSAGE_LENGTH + 1),
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors.join(" ")).toContain("2000");
    }
  });

  it("rejects a missing message", () => {
    const result = validateContactSubmission({ category: "bug", message: "" });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors.join(" ")).toContain("Message is required");
    }
  });

  it("accepts an empty or null optional email", () => {
    expect(validateContactSubmission({ category: "bug", message: "Hi", email: "" }).ok).toBe(
      true,
    );
    expect(
      validateContactSubmission({ category: "bug", message: "Hi", email: null }).ok,
    ).toBe(true);
  });

  it("rejects a badly formatted email", () => {
    const result = validateContactSubmission({
      category: "bug",
      message: "Hi",
      email: "not-an-email",
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors.join(" ")).toContain("email");
    }
  });

  it("rejects an email over 254 characters", () => {
    const result = validateContactSubmission({
      category: "bug",
      message: "Hi",
      email: `a@${"b".repeat(254)}.com`,
    });
    expect(result.ok).toBe(false);
  });

  it("blocks a filled honeypot", () => {
    const result = validateContactSubmission({
      category: "bug",
      message: "Hello",
      _hp: "spam",
    });
    expect(result.ok).toBe(false);
  });

  it("sanitizes control characters from the message", () => {
    const result = validateContactSubmission({
      category: "bug",
      message: "line1\u0000line2",
    });
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.message).toBe("line1line2");
    }
  });

  it("rejects an invalid category", () => {
    const result = validateContactSubmission({ category: "not-a-category", message: "Hi" });
    expect(result.ok).toBe(false);
  });
});

/* ─── sanitizeContext ─── */

describe("sanitizeContext", () => {
  it("allows alphanumeric, hyphen, and slash", () => {
    expect(sanitizeContext("/en/compress-pdf", "en")).toEqual({
      page: "/en/compress-pdf",
      locale: "en",
    });
  });

  it("strips path/script content and control characters", () => {
    expect(sanitizeContext("/en/<script>alert(1)</script>", "en")).toEqual({
      page: "/en/scriptalert1/script",
      locale: "en",
    });
  });

  it("returns null for empty or whitespace-only input", () => {
    expect(sanitizeContext("  ", "")).toEqual({ page: null, locale: null });
  });

  it("caps length at 120 characters", () => {
    const long = "a".repeat(200);
    expect(sanitizeContext(`/${long}`, long)).toEqual({ page: null, locale: null });
  });
});

/* ─── Rate limiting ─── */

describe("rate limiting", () => {
  it("records submissions and blocks the 4th in a short window", () => {
    expect(isRateLimited()).toBe(false);
    recordSubmission();
    recordSubmission();
    recordSubmission();
    // Three records are allowed; the 4th within the window is blocked.
    expect(isRateLimited()).toBe(true);

    recordSubmission();
    expect(isRateLimited()).toBe(true);
  });
});

/* ─── ContactForm component ─── */

describe("ContactForm", () => {
  it("submits with each category", async () => {
    for (const category of CONTACT_CATEGORIES) {
      // Reset the rate-limit store per category so every submit is allowed.
      memoryStore.clear();
      vi.mocked(fetch).mockClear();

      render(createElement(ContactForm, { locale: "en" }));
      selectCategory(category);
      typeMessage("This is a test message.");
      await submitForm();

      // Submission should reach the server (mocked fetch resolves).
      expect(fetch).toHaveBeenCalledWith(
        "/api/v1/support/contact",
        expect.objectContaining({ method: "POST" }),
      );

      cleanup();
    }
  });

  it("rejects a message over 2000 characters with an error", async () => {
    render(createElement(ContactForm, { locale: "en" }));
    typeMessage("x".repeat(MAX_MESSAGE_LENGTH + 1));
    await submitForm();

    expect(screen.getByRole("alert")).toBeTruthy();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("rejects a missing message", async () => {
    render(createElement(ContactForm, { locale: "en" }));
    await submitForm();

    expect(screen.getByRole("alert")).toBeTruthy();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("accepts an empty optional email", async () => {
    render(createElement(ContactForm, { locale: "en" }));
    typeMessage("No email here");
    await submitForm();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("rejects a badly formatted email", async () => {
    render(createElement(ContactForm, { locale: "en" }));
    typeMessage("Email test");
    typeEmail("not-an-email");
    await submitForm();

    expect(screen.getByRole("alert")).toBeTruthy();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("accepts a valid email", async () => {
    render(createElement(ContactForm, { locale: "en" }));
    typeMessage("Email test");
    typeEmail("user@example.com");
    await submitForm();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("blocks submission when the honeypot is filled", async () => {
    render(createElement(ContactForm, { locale: "en" }));
    // The honeypot input has no accessible label; grab it by name.
    const hp = document.querySelector('input[name="_hp"]') as HTMLInputElement;
    fireEvent.change(hp, { target: { value: "spam" } });
    typeMessage("This is spam");
    await submitForm();

    // No server call; form pretends success.
    expect(fetch).not.toHaveBeenCalled();
    expect(screen.getByRole("status")).toBeTruthy();
  });

  it("blocks the 4th submit in a short window via rate limiting", async () => {
    // Pre-populate the rate-limit window with 3 entries (fake timers set to a fixed now).
    window.localStorage.setItem(
      "papyr_contact_submissions",
      JSON.stringify([Date.now(), Date.now(), Date.now()]),
    );
    render(createElement(ContactForm, { locale: "en" }));
    typeMessage("Rate limited message");
    await submitForm();

    expect(screen.getByRole("alert")).toBeTruthy();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("clears the message input after a failed submit (never resurfaced)", async () => {
    render(createElement(ContactForm, { locale: "en" }));
    typeMessage("secret content that must not resurface");
    typeEmail("bad-email");
    await submitForm();

    expect(screen.getByRole("alert")).toBeTruthy();
    const textarea = screen.getByLabelText(EN.contact.messageLabel) as HTMLTextAreaElement;
    expect(textarea.value).toBe("");
  });

  it("falls back to a client-side confirmation when the endpoint is unavailable", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));
    render(createElement(ContactForm, { locale: "en" }));
    typeMessage("Fallback test");
    await submitForm();

    expect(screen.getByRole("status")).toBeTruthy();
    expect(screen.getByText(EN.contact.endpointUnavailable)).toBeTruthy();
  });
});

/* ─── Redaction via redactPayload ─── */

describe("analytics redaction", () => {
  it("never sends message, email, filename, or password fields", () => {
    const payload = {
      page: "/en/contact",
      locale: "en",
      message: "secret body",
      email: "user@example.com",
      filename: "tax-return.pdf",
      password: "hunter2",
      category: "bug",
      outcome: "attempt",
    };

    const redacted = redactPayload(payload);
    const json = JSON.stringify(redacted);

    expect(json).not.toContain("secret body");
    expect(json).not.toContain("user@example.com");
    expect(json).not.toContain("tax-return.pdf");
    expect(json).not.toContain("hunter2");
    expect(redacted).not.toHaveProperty("message");
    expect(redacted).not.toHaveProperty("email");
    expect(redacted).not.toHaveProperty("filename");
    expect(redacted).not.toHaveProperty("password");
  });

  it("sends only allowed fields through trackEvent", () => {
    trackEvent("contact_submit", {
      page: "/en/contact",
      locale: "en",
      message: "secret",
      email: "user@example.com",
      outcome: "attempt",
    });

    const sink = getVaSink();
    expect(sink).toBeDefined();
    const call = sink as unknown as {
      mock: { calls: Array<[string, Record<string, unknown>]> };
    };
    expect(call.mock.calls).toHaveLength(1);
    const payload = call.mock.calls[0][1];
    expect(JSON.stringify(payload)).not.toContain("secret");
    expect(JSON.stringify(payload)).not.toContain("user@example.com");
    expect(payload).not.toHaveProperty("message");
    expect(payload).not.toHaveProperty("email");
  });
});

/* ─── ResultProblemReport ─── */

describe("ResultProblemReport", () => {
  it("renders a compact trigger and opens the categorized form prefilled with context", () => {
    render(
      createElement(ResultProblemReport, {
        locale: "en",
        page: "/en/compress-pdf",
        localeContext: "en",
      }),
    );

    expect(screen.getByText(EN.contact.reportProblem)).toBeTruthy();

    fireEvent.click(screen.getByText(EN.contact.reportProblem));

    // Form appears with the category select and sanitized context intro.
    expect(screen.getByLabelText(EN.contact.categoryLabel)).toBeTruthy();
    expect(screen.getByText(EN.contact.reportIntro)).toBeTruthy();
  });
});