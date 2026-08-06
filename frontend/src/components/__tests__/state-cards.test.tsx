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

  it("renders its localized processing label with a pulse skeleton for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { unmount } = render(<ProcessingCard locale={locale} />);
      expect(screen.getByText(copy.states.processing)).toBeTruthy();
      const skeleton = screen.getByTestId("skeleton");
      expect(skeleton.className).toContain("animate-pulse");
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
    fireEvent.click(screen.getByRole("button", { name: copy.reset.processAnother }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });
});
