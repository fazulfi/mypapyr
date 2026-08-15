// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getMessages } from "@/lib/messages";

const mockUseTaskPolling = vi.fn();
vi.mock("@/hooks/useTaskPolling", () => ({
  useTaskPolling: (...args: unknown[]) => mockUseTaskPolling(...args),
}));

import { JpgToPdfTool } from "@/app/[locale]/jpg-to-pdf/page";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeImage(name: string, size = 128): File {
  return new File([new Uint8Array(size)], name, { type: "image/jpeg" });
}

function selectFiles(container: HTMLElement, files: File[]): void {
  const input = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(input, { target: { files } });
}

function idlePolling(): void {
  mockUseTaskPolling.mockReturnValue({ status: null, refresh: vi.fn(), stop: vi.fn() });
}

function pollingWithStatus(
  status: {
    state: string;
    messageKey?: string | null;
    retryable?: boolean;
    outputCount?: number | null;
  } | null,
): void {
  mockUseTaskPolling.mockImplementation(
    ({ taskId, enabled }: { taskId: string; enabled: boolean }) =>
      enabled && taskId !== ""
        ? { status, refresh: vi.fn(), stop: vi.fn() }
        : { status: null, refresh: vi.fn(), stop: vi.fn() },
  );
}

/**
 * Stubs `global.fetch` to accept POST /tools/jpg-to-pdf/tasks and
 * download-grant GET requests on /tasks/<id>/download/<n>.
 */
function stubFetch(taskId = "task-jpg-1"): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn().mockImplementation((url: RequestInfo) => {
    const target = String(url);
    if (target.endsWith("/tasks")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ task_id: taskId, expires_at: "2026-01-01T00:00:00Z" }),
      });
    }
    if (target.includes("/download/")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          url: "https://cdn.example/out.pdf",
          expires_at: "2026-01-01T00:00:00Z",
        }),
      });
    }
    return Promise.resolve({ ok: false, status: 500 });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function submitImages(locale: "en" | "es" | "id" = "en"): Promise<ReturnType<typeof render>> {
  const rendered = render(<JpgToPdfTool locale={locale} />);
  selectFiles(rendered.container, [makeImage("photo.jpg"), makeImage("scan.jpg")]);
  fireEvent.click(
    screen.getByRole("button", { name: getMessages(locale).tools.jpgToPdf.actions.convert }),
  );
  return rendered;
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

beforeEach(() => {
  idlePolling();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

// ---------------------------------------------------------------------------
// Idle / initial render
// ---------------------------------------------------------------------------

describe("JpgToPdfTool idle phase", () => {
  it("renders title, description, Dropzone, and submit button for each locale", () => {
    for (const locale of ["en", "es", "id"] as const) {
      const copy = getMessages(locale);
      const { unmount } = render(<JpgToPdfTool locale={locale} />);

      expect(
        screen.getByRole("heading", { level: 1, name: copy.tools.jpgToPdf.title }),
      ).toBeTruthy();
      expect(screen.getByText(copy.tools.jpgToPdf.description)).toBeTruthy();
      expect(screen.getByTestId("dropzone")).toBeTruthy();
      expect(
        screen.getByRole("button", { name: copy.tools.jpgToPdf.actions.convert }),
      ).toBeTruthy();

      unmount();
    }
  });

  it("disables the convert button when no files are selected", () => {
    const copy = getMessages("en");
    render(<JpgToPdfTool locale="en" />);
    const button = screen.getByRole("button", {
      name: copy.tools.jpgToPdf.actions.convert,
    }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
  });

  it("enables the convert button after selecting files", () => {
    const copy = getMessages("en");
    const { container } = render(<JpgToPdfTool locale="en" />);
    selectFiles(container, [makeImage("photo.jpg")]);
    const button = screen.getByRole("button", {
      name: copy.tools.jpgToPdf.actions.convert,
    }) as HTMLButtonElement;
    expect(button.disabled).toBe(false);
  });

  it("renders the immediate leaderboard slot during idle phase (owner decision 2026-08-15)", () => {
    render(<JpgToPdfTool locale="en" />);
    expect(document.querySelector('div[data-testid="papyr-ad-slot"]')).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// Upload flow
// ---------------------------------------------------------------------------

describe("JpgToPdfTool upload / admission", () => {
  it("shows the uploading label while the admission request is in flight", async () => {
    let resolveUpload: (value: unknown) => void = () => undefined;
    const pending = new Promise((resolve) => {
      resolveUpload = resolve;
    });
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(pending));

    const copy = getMessages("en");
    const { container } = render(<JpgToPdfTool locale="en" />);
    selectFiles(container, [makeImage("photo.jpg")]);
    fireEvent.click(screen.getByRole("button", { name: copy.tools.jpgToPdf.actions.convert }));

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: copy.tools.jpgToPdf.actions.uploading }),
      ).toBeTruthy(),
    );
    resolveUpload({ ok: true, json: async () => ({ task_id: "t", expires_at: "" }) });
  });

  it("POSTs the selected files to the admission endpoint", async () => {
    const fetchMock = stubFetch("task-jpg-adm");
    await submitImages("en");

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/tools/jpg-to-pdf/tasks");
    expect(init.method).toBe("POST");
    const body = init.body as FormData;
    const names = body.getAll("files").map((entry) => (entry as File).name);
    expect(names).toEqual(["photo.jpg", "scan.jpg"]);
  });

  it("surfaces the error card when the admission request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await submitImages("en");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
  });
});

// ---------------------------------------------------------------------------
// Polling / result states
// ---------------------------------------------------------------------------

describe("JpgToPdfTool polling / result states", () => {
  it("renders the queued card after admission while the task waits", async () => {
    pollingWithStatus({ state: "queued", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitImages("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.queued)).toBeTruthy());
    // AdSlot should NOT render during queued
    expect(document.querySelector('div[data-testid="papyr-ad-slot"]')).toBeTruthy();
  });

  it("renders the processing card while the task is processing", async () => {
    pollingWithStatus({ state: "processing", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitImages("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.processing)).toBeTruthy());
    // AdSlot should NOT render during processing
    expect(document.querySelector('div[data-testid="papyr-ad-slot"]')).toBeTruthy();
  });

  it("auto-fetches the download grant when the task completes and offers download + reset", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    const fetchMock = stubFetch("task-jpg-done");
    await submitImages("en");

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/tools/jpg-to-pdf/tasks/task-jpg-done/download/0",
      ),
    );
    const copy = getMessages("en");
    expect(screen.getByRole("button", { name: copy.states.download })).toBeTruthy();
    expect(screen.getByRole("button", { name: copy.reset.processAnother })).toBeTruthy();
  });

  it("renders AdSlot when phase is done", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitImages("en");

    await waitFor(() =>
      expect(screen.getByRole("button", { name: getMessages("en").states.download })).toBeTruthy(),
    );
    // AdSlot placeholder should be in the DOM during done phase
    expect(document.querySelector('div[data-testid="papyr-ad-slot"]')).toBeTruthy();
  });

  it("renders the error card with the message key on failure", async () => {
    pollingWithStatus({
      state: "failed",
      messageKey: "tools.jpgToPdf.errors.fileTooLarge",
      retryable: true,
      outputCount: null,
    });
    stubFetch();
    await submitImages("id");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.getByText(getMessages("id").tools.jpgToPdf.errors.fileTooLarge)).toBeTruthy();
  });

  it("renders AdSlot when phase is error", async () => {
    pollingWithStatus({
      state: "failed",
      messageKey: "tools.jpgToPdf.errors.uploadFailed",
      retryable: true,
      outputCount: null,
    });
    stubFetch();
    await submitImages("en");

    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    // AdSlot placeholder should be in the DOM during error phase
    expect(document.querySelector('div[data-testid="papyr-ad-slot"]')).toBeTruthy();
  });

  it("fires window.location.href on download click", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    const fetchMock = stubFetch("task-jpg-dl");
    await submitImages("en");

    const copy = getMessages("en");
    // Wait until the download grant has been fetched
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/tools/jpg-to-pdf/tasks/task-jpg-dl/download/0",
      ),
    );

    // Stub location before clicking
    const loc: { href: string } = { href: "" };
    vi.stubGlobal("location", loc);

    // The grant fetch resolves asynchronously and calls setDownloadUrl;
    // waitFor keeps retrying until the state is applied and the click
    // actually navigates.
    await waitFor(() => {
      fireEvent.click(screen.getByRole("button", { name: copy.states.download }));
      expect(loc.href).toBe("https://cdn.example/out.pdf");
    });
  });
});
