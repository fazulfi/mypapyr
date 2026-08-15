/**
 * PT-03 Contact form + result-problem report.
 *
 * Client-side categorized contact form used by the `/contact` page and the
 * result-local problem report trigger. Handles:
 *  - categorized submission (closed enum)
 *  - validation via `validateContactSubmission` from `@/lib/support`
 *  - honeypot + client-side rate limiting (localStorage)
 *  - Cloudflare Turnstile placeholder (script injected when env token present)
 *  - graceful fallback when `/api/v1/support/contact` is unavailable
 *  - redaction-safe analytics via `redactPayload`/`trackEvent`
 */

"use client";

import { useEffect, useRef, useState } from "react";

import { trackEvent } from "@/lib/analytics";
import { getMessages, type Messages } from "@/lib/messages";
import { type Locale } from "@/lib/i18n";
import {
  CONTACT_CATEGORIES,
  type ContactCategory,
  MAX_MESSAGE_LENGTH,
  sanitizeContext,
  validateContactSubmission,
} from "@/lib/support";

/* ─── Rate-limit guard ─── */

const RATE_LIMIT_KEY = "papyr_contact_submissions";
const RATE_LIMIT_MAX = 3;
const RATE_LIMIT_WINDOW_MS = 10 * 60 * 1000; // 10 minutes

function readRateLimitWindow(): number[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(RATE_LIMIT_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (entry): entry is number => typeof entry === "number" && Number.isFinite(entry),
    );
  } catch {
    return [];
  }
}

export function recordSubmission(): void {
  if (typeof window === "undefined") return;
  try {
    const now = Date.now();
    const cutoff = now - RATE_LIMIT_WINDOW_MS;
    const recent = readRateLimitWindow().filter((t) => t > cutoff);
    recent.push(now);
    window.localStorage.setItem(RATE_LIMIT_KEY, JSON.stringify(recent));
  } catch {
    // localStorage may be unavailable (private mode); treat as no-op.
  }
}

export function isRateLimited(): boolean {
  const now = Date.now();
  const cutoff = now - RATE_LIMIT_WINDOW_MS;
  const recent = readRateLimitWindow().filter((t) => t > cutoff);
  return recent.length >= RATE_LIMIT_MAX;
}

/* ─── Turnstile injection ─── */

const TURNSTILE_SCRIPT_SRC =
  "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

function turnstileEnabled(): boolean {
  return typeof process !== "undefined" && Boolean(process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY);
}

function injectTurnstileScript(): void {
  if (typeof document === "undefined") return;
  if (!turnstileEnabled()) return;
  if (document.querySelector(`script[src="${TURNSTILE_SCRIPT_SRC}"]`)) return;
  const script = document.createElement("script");
  script.src = TURNSTILE_SCRIPT_SRC;
  script.async = true;
  script.defer = true;
  document.head.appendChild(script);
}

export interface ContactFormProps {
  locale: string;
  /** Prefill context (sanitized here). */
  context?: { page?: string | null; locale?: string | null };
  /** Rendered as a compact inline report (result-problem trigger). */
  collapsed?: boolean;
  /** Copy override for the result-problem report (optional). */
  copy?: Messages["contact"];
}

export function ContactForm({
  locale,
  context,
  collapsed = false,
  copy: copyOverride,
}: ContactFormProps): React.ReactElement {
  const copy = copyOverride ?? getMessages(locale as Locale).contact;

  const [category, setCategory] = useState<ContactCategory>("other");
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");
  const [honeypot, setHoneypot] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">("idle");
  const [serverError, setServerError] = useState<string | null>(null);
  const [rateLimited, setRateLimited] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const turnstileContainerRef = useRef<HTMLDivElement | null>(null);

  const sanitizedContext = sanitizeContext(context?.page ?? null, context?.locale ?? null);

  useEffect(() => {
    injectTurnstileScript();
    if (!turnstileEnabled()) return;

    const renderTurnstile = () => {
      const container = turnstileContainerRef.current;
      if (!container) return;
      const w = window as unknown as {
        turnstile?: { render: (el: HTMLElement, opts: object) => string };
      };
      if (typeof w.turnstile?.render !== "function") return;
      try {
        w.turnstile.render(container, {
          sitekey: process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY,
          callback: (token: string) => setTurnstileToken(token),
        });
      } catch {
        // Rendering may fail if the script isn't ready; ignore.
      }
    };

    const script = document.querySelector(`script[src="${TURNSTILE_SCRIPT_SRC}"]`);
    if (script) {
      script.addEventListener("load", renderTurnstile);
    }
    const fallback = window.setTimeout(renderTurnstile, 1500);
    return () => {
      window.clearTimeout(fallback);
    };
  }, []);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();

    // Honeypot — pretend success, never submit.
    if (honeypot.trim().length > 0) {
      setStatus("done");
      setErrors([]);
      setMessage("");
      setEmail("");
      setHoneypot("");
      return;
    }

    if (isRateLimited()) {
      setRateLimited(true);
      setStatus("error");
      return;
    }

    const result = validateContactSubmission({
      category,
      message,
      email: email.trim() === "" ? null : email,
      _hp: honeypot,
    });

    if (!result.ok) {
      setErrors(result.errors);
      setStatus("error");
      // Clear message input — never echo submitted content back after a failed submit.
      setMessage("");
      return;
    }

    const submission = {
      ...result.value,
      page: sanitizedContext.page,
      locale: sanitizedContext.locale ?? locale,
    };

    setStatus("submitting");

    // Redaction-safe analytics: never contains message/email/filename/password.
    trackEvent("contact_submit", {
      category: submission.category,
      page: submission.page ?? null,
      locale: submission.locale ?? null,
      outcome: "attempt",
    });

    if (turnstileEnabled() && !turnstileToken) {
      setStatus("idle");
      setErrors([copy.turnstileRequired]);
      return;
    }

    try {
      const response = await fetch("/api/v1/support/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...submission, turnstileToken: turnstileToken ?? null }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      recordSubmission();
      setStatus("done");
      setErrors([]);
      setMessage("");
      setEmail("");
      setHoneypot("");
      setServerError(null);
    } catch {
      // Endpoint unavailable — fall back to client-side-only confirmation.
      recordSubmission();
      setStatus("done");
      setErrors([]);
      setMessage("");
      setEmail("");
      setServerError(copy.endpointUnavailable);
    }
  };

  if (status === "done") {
    return (
      <div
        className="rounded-xl border border-emerald-100 bg-emerald-50/60 px-5 py-4"
        role="status"
      >
        <p className="text-sm font-medium text-emerald-800">{copy.confirmation}</p>
        {serverError ? <p className="mt-1 text-xs text-slate-500">{serverError}</p> : null}
        <button
          type="button"
          className="mt-3 text-xs font-semibold text-emerald-700 underline underline-offset-2"
          onClick={() => {
            setStatus("idle");
            setServerError(null);
          }}
        >
          {copy.sendAnother}
        </button>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className={collapsed ? "space-y-3" : "space-y-4"}
      aria-label={copy.formLabel}
    >
      {rateLimited ? (
        <div
          className="rounded-xl border border-rose-100 bg-rose-50/60 px-4 py-3 text-sm text-rose-700"
          role="alert"
        >
          {copy.rateLimited}
        </div>
      ) : null}

      {errors.length > 0 ? (
        <ul
          className="rounded-xl border border-rose-100 bg-rose-50/60 px-4 py-3 text-sm text-rose-700"
          role="alert"
        >
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      ) : null}

      {/* Honeypot — hidden from humans, filled by bots */}
      <div className="sr-only" aria-hidden="true">
        <label>
          Leave this field empty
          <input
            type="text"
            name="_hp"
            tabIndex={-1}
            autoComplete="off"
            value={honeypot}
            onChange={(event) => setHoneypot(event.target.value)}
          />
        </label>
      </div>

      <div className="space-y-1.5">
        <label htmlFor="contact-category" className="block text-sm font-medium text-slate-700">
          {copy.categoryLabel}
        </label>
        <select
          id="contact-category"
          name="category"
          value={category}
          onChange={(event) => setCategory(event.target.value as ContactCategory)}
          className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        >
          {CONTACT_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {copy.categories[cat]}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-1.5">
        <label htmlFor="contact-message" className="block text-sm font-medium text-slate-700">
          {copy.messageLabel}
        </label>
        <textarea
          id="contact-message"
          name="message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          maxLength={MAX_MESSAGE_LENGTH}
          rows={collapsed ? 4 : 6}
          className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        <p className="text-right text-xs text-slate-400">
          {message.length}/{MAX_MESSAGE_LENGTH}
        </p>
      </div>

      <div className="space-y-1.5">
        <label htmlFor="contact-email" className="block text-sm font-medium text-slate-700">
          {copy.emailLabel} <span className="font-normal text-slate-400">({copy.optional})</span>
        </label>
        <input
          id="contact-email"
          name="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        <p className="text-xs text-slate-400">{copy.emailHint}</p>
      </div>

      {/* Cloudflare Turnstile placeholder — script injected client-side when env token present */}
      <div
        ref={turnstileContainerRef}
        className={turnstileEnabled() ? "min-h-[65px]" : "hidden"}
        data-testid="turnstile-placeholder"
      />

      <button
        type="submit"
        disabled={status === "submitting"}
        className="inline-flex items-center justify-center rounded-lg bg-navy px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-navy/90 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {status === "submitting" ? copy.submitting : copy.submit}
      </button>
    </form>
  );
}

export default ContactForm;
