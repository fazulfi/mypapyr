// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { locales } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

import { DoneCard } from "../states/DoneCard";
import { ErrorCard } from "../states/ErrorCard";
import { PreparingCard } from "../states/PreparingCard";
import { ProcessingCard } from "../states/ProcessingCard";
import { QueuedCard } from "../states/QueuedCard";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("components/states shimmer cards", () => {
  it("renders its localized queued label with a pulse skeleton for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { unmount } = render(<QueuedCard locale={locale} />);
      expect(screen.getByText(copy.states.queued)).toBeTruthy();
      const skeleton = screen.getByTestId("skeleton");
      expect(skeleton.className).toContain("animate-pulse");
      unmount();
    }
  });

  it("renders its localized preparing label with a pulse skeleton for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { unmount } = render(<PreparingCard locale={locale} />);
      expect(screen.getByText(copy.states.preparing)).toBeTruthy();
      const skeleton = screen.getByTestId("skeleton");
      expect(skeleton.className).toContain("animate-pulse");
      unmount();
    }
  });

  it("renders its localized processing label with a shimmer bar and file row for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { container, unmount } = render(<ProcessingCard locale={locale} />);
      expect(screen.getByText(copy.states.processing)).toBeTruthy();
      const fileChip = container.querySelector("[class*='bg-slate-100']") as HTMLElement;
      expect(fileChip).toBeTruthy();
      expect(fileChip.className).toContain("rounded-xl");
      const shimmer = container.querySelector("[class*='animate-shimmer']") as HTMLElement;
      expect(shimmer.className).toContain("animate-shimmer");
      unmount();
    }
  });
});

describe("components/states DoneCard", () => {
  it("renders the done label and both actions for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { unmount } = render(
        <DoneCard locale={locale} onDownload={() => undefined} onReset={() => undefined} />,
      );
      expect(screen.getByText(copy.states.done)).toBeTruthy();
      expect(screen.getByRole("button", { name: copy.states.download })).toBeTruthy();
      expect(screen.getByRole("button", { name: copy.reset.processAnother })).toBeTruthy();
      unmount();
    }
  });

  it("fires onDownload from the download button and onReset from the reset button", () => {
    const onDownload = vi.fn();
    const onReset = vi.fn();
    const copy = getMessages("en");
    render(<DoneCard locale="en" onDownload={onDownload} onReset={onReset} />);

    fireEvent.click(screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.reset.processAnother }));

    expect(onDownload).toHaveBeenCalledTimes(1);
    expect(onReset).toHaveBeenCalledTimes(1);
  });
});

describe("components/states ErrorCard", () => {
  it("renders the resolved messageKey text for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { unmount } = render(
        <ErrorCard
          locale={locale}
          messageKey="states.error"
          retryable={false}
          onReset={() => undefined}
        />,
      );
      expect(screen.getByText(copy.states.error)).toBeTruthy();
      unmount();
    }
  });

  it("falls back to the generic error copy when messageKey is null", () => {
    const copy = getMessages("es");
    render(<ErrorCard locale="es" messageKey={null} retryable={false} onReset={() => undefined} />);
    expect(screen.getByText(copy.states.error)).toBeTruthy();
  });

  it("surfaces the retryable flag honestly without faking success", () => {
    const { container } = render(
      <ErrorCard locale="en" messageKey={null} retryable={true} onReset={() => undefined} />,
    );
    const card = container.querySelector("[role='alert']") as HTMLElement;
    expect(card.dataset.retryable).toBe("true");
    expect(screen.queryByText(getMessages("en").states.done)).toBeNull();
  });

  it("exposes the reset action", () => {
    const onReset = vi.fn();
    const copy = getMessages("id");
    render(<ErrorCard locale="id" messageKey={null} retryable={false} onReset={onReset} />);
    fireEvent.click(screen.getByRole("button", { name: copy.states.retry }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });
});

describe("components/states rich reference markup", () => {
  it("renders the rose error card with alert title, message, and retry button for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { container, unmount } = render(
        <ErrorCard
          locale={locale}
          messageKey="states.error"
          retryable={true}
          onReset={() => undefined}
        />,
      );
      const card = container.querySelector("[role='alert']") as HTMLElement;
      expect(card.className).toContain("rounded-2xl");
      expect(card.className).toContain("border-rose-200");
      expect(card.className).toContain("bg-rose-50/50");
      expect(screen.getByText(copy.states.errorTitle)).toBeTruthy();
      expect(screen.getByText(copy.states.error)).toBeTruthy();
      expect(screen.getByRole("button", { name: copy.states.retry })).toBeTruthy();
      unmount();
    }
  });

  it("renders the compress done variant with before/after sizes, saved pill, and emerald check", () => {
    const copy = getMessages("en");
    const { container } = render(
      <DoneCard
        locale="en"
        onDownload={() => undefined}
        onReset={() => undefined}
        originalBytes={10 * 1024 * 1024}
        compressedBytes={2 * 1024 * 1024}
      />,
    );
    expect(screen.getByText(copy.states.complete)).toBeTruthy();
    const check = container.querySelector("[class*='bg-emerald-500']") as HTMLElement;
    expect(check).toBeTruthy();
    expect(check.className).toContain("rounded-full");
    const compare = container.querySelector("[class*='bg-slate-50 px-4']") as HTMLElement;
    expect(compare).toBeTruthy();
    expect(compare.className).toContain("rounded-xl");
    expect(screen.getByText(copy.states.before)).toBeTruthy();
    expect(screen.getByText(copy.states.after)).toBeTruthy();
    expect(screen.getByText("10.0 MB")).toBeTruthy();
    expect(screen.getByText("2.0 MB")).toBeTruthy();
    const pill = container.querySelector("[class*='bg-accent/10']") as HTMLElement;
    expect(pill).toBeTruthy();
    expect(pill.textContent).toBe("−80%");
    expect(screen.getByRole("button", { name: copy.states.downloadCta })).toBeTruthy();
  });

  it("hides the before/after comparison when no result sizes are provided", () => {
    const copy = getMessages("en");
    const { container } = render(
      <DoneCard locale="en" onDownload={() => undefined} onReset={() => undefined} />,
    );
    expect(screen.getByText(copy.states.done)).toBeTruthy();
    expect(container.querySelector("[class*='bg-slate-50 px-4']")).toBeNull();
    expect(container.querySelector("[class*='bg-emerald-500']")).toBeTruthy();
    expect(screen.queryByText(copy.states.before)).toBeNull();
  });
});
