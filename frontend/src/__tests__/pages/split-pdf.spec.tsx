// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getMessages } from "@/lib/messages";

const mockUseTaskPolling = vi.fn();
vi.mock("@/hooks/useTaskPolling", () => ({
  useTaskPolling: (...args: unknown[]) => mockUseTaskPolling(...args),
}));

const mockBuildZip = vi.fn();
const mockDownloadBlob = vi.fn();
vi.mock("@/lib/zip", () => ({
  buildZip: (...args: unknown[]) => mockBuildZip(...args),
  downloadBlob: (...args: unknown[]) => mockDownloadBlob(...args),
}));

import { SplitPdfTool } from "@/app/[locale]/split-pdf/page";

function makePdf(name: string, size = 128): File {
  return new File([new Uint8Array(size)], name, { type: "application/pdf" });
}

function selectFiles(container: HTMLElement, files: File[]): void {
  const input = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(input, { target: { files } });
}

function idlePolling(): void {
  mockUseTaskPolling.mockReturnValue({ status: null, refresh: vi.fn(), stop: vi.fn() });
}

function pollingWithStatus(status: unknown): void {
  mockUseTaskPolling.mockImplementation(
    ({ taskId, enabled }: { taskId: string; enabled: boolean }) =>
      enabled && taskId !== ""
        ? { status, refresh: vi.fn(), stop: vi.fn() }
        : { status: null, refresh: vi.fn(), stop: vi.fn() },
  );
}

function stubFetch(taskId = "task-spl-1"): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn().mockImplementation((url: RequestInfo) => {
    const target = String(url);
    if (target.endsWith("/tasks")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ task_id: taskId, expires_at: "2026-01-01T00:00:00Z" }),
      });
    }
    if (target.includes("/download/")) {
      const index = target.split("/download/")[1] ?? "0";
      return Promise.resolve({
        ok: true,
        json: async () => ({
          url: "https://cdn.example/split-" + index + ".pdf",
          expires_at: "2026-01-01T00:00:00Z",
        }),
      });
    }
    if (target.startsWith("https://cdn.example/")) {
      return Promise.resolve({
        ok: true,
        blob: async () => new Blob([new Uint8Array(16)], { type: "application/pdf" }),
      });
    }
    return Promise.resolve({ ok: false, status: 500 });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function submitPdf(locale: "en" | "es" | "id" = "en"): Promise<ReturnType<typeof render>> {
  const rendered = render(<SplitPdfTool locale={locale} />);
  selectFiles(rendered.container, [makePdf("document.pdf")]);
  fireEvent.click(
    screen.getByRole("button", { name: getMessages(locale).tools.split.actions.split }),
  );
  return rendered;
}

beforeEach(() => {
  idlePolling();
  mockBuildZip.mockReset();
  mockDownloadBlob.mockReset();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("SplitPdfTool localized rendering", () => {
  it("renders the localized title and dropzone for each locale", () => {
    for (const locale of ["en", "es", "id"] as const) {
      const copy = getMessages(locale);
      const { unmount } = render(<SplitPdfTool locale={locale} />);
      expect(screen.getByRole("heading", { level: 1, name: copy.tools.split.title })).toBeTruthy();
      expect(screen.getByTestId("dropzone")).toBeTruthy();
      unmount();
    }
  });

  it("disables the split action until a PDF is selected", () => {
    const copy = getMessages("en");
    const { container } = render(<SplitPdfTool locale="en" />);
    const button = screen.getByRole("button", {
      name: copy.tools.split.actions.split,
    }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);

    selectFiles(container, [makePdf("a.pdf")]);
    const enabled = screen.getByRole("button", {
      name: copy.tools.split.actions.split,
    }) as HTMLButtonElement;
    expect(enabled.disabled).toBe(false);
  });

  it("restricts the file input to application/pdf", () => {
    const { container } = render(<SplitPdfTool locale="en" />);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input.getAttribute("accept")).toBe("application/pdf");
  });
});

describe("SplitPdfTool upload / admission contract", () => {
  it("POSTs the PDF to the admission endpoint using the file field", async () => {
    const fetchMock = stubFetch();
    await submitPdf("en");

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/tools/split-pdf/tasks");
    expect(init.method).toBe("POST");
    const body = init.body as FormData;
    const files = body.getAll("file");
    expect(files).toHaveLength(1);
    expect((files[0] as File).name).toBe("document.pdf");
  });

  it("shows the uploading label while the admission request is in flight", async () => {
    let resolveUpload: (value: unknown) => void = () => undefined;
    const pending = new Promise((resolve) => {
      resolveUpload = resolve;
    });
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(pending));

    const copy = getMessages("en");
    const { container } = render(<SplitPdfTool locale="en" />);
    selectFiles(container, [makePdf("a.pdf")]);
    fireEvent.click(screen.getByRole("button", { name: copy.tools.split.actions.split }));

    await waitFor(() =>
      expect(screen.getByRole("button", { name: copy.tools.split.actions.uploading })).toBeTruthy(),
    );
    resolveUpload({ ok: true, json: async () => ({ task_id: "t", expires_at: "" }) });
  });

  it("surfaces the error card when the admission request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await submitPdf("en");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
  });
});

describe("SplitPdfTool polling / result states", () => {
  it("renders the queued card after admission while the task waits", async () => {
    pollingWithStatus({ state: "queued", messageKey: null, retryable: false, outputCount: null });
    stubFetch();
    await submitPdf("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.queued)).toBeTruthy());
  });

  it("renders the processing card while the task is processing", async () => {
    pollingWithStatus({
      state: "processing",
      messageKey: null,
      retryable: false,
      outputCount: null,
    });
    stubFetch();
    await submitPdf("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.processing)).toBeTruthy());
  });

  it("offers download plus reset when done and fetches the grant on download", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    const fetchMock = stubFetch("task-spl-9");
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.states.download }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/v1/tools/split-pdf/tasks/task-spl-9/download/0"),
    );
    expect(screen.getByRole("button", { name: copy.reset.processAnother })).toBeTruthy();
  });

  it("packages every output into a ZIP for a multi-output result (no index-0-only)", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 3 });
    const zipBlob = new Blob([new Uint8Array(8)], { type: "application/zip" });
    mockBuildZip.mockResolvedValue(zipBlob);
    const fetchMock = stubFetch("task-spl-multi");
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.states.download }));

    await waitFor(() => expect(mockBuildZip).toHaveBeenCalledTimes(1));
    const entries = mockBuildZip.mock.calls[0][0] as Array<{ name: string }>;
    expect(entries.map((entry) => entry.name)).toEqual([
      "split-1.pdf",
      "split-2.pdf",
      "split-3.pdf",
    ]);

    await waitFor(() => expect(mockDownloadBlob).toHaveBeenCalledWith(zipBlob, "split-pdf.zip"));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/tools/split-pdf/tasks/task-spl-multi/download/0",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/tools/split-pdf/tasks/task-spl-multi/download/1",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/tools/split-pdf/tasks/task-spl-multi/download/2",
    );
  });

  it("renders the localized error card with the stable message key on failure", async () => {
    pollingWithStatus({
      state: "failed",
      messageKey: "tools.split.errors.fileTooLarge",
      retryable: false,
      outputCount: null,
    });
    stubFetch();
    await submitPdf("es");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.getByText(getMessages("es").tools.split.errors.fileTooLarge)).toBeTruthy();
  });

  it("resets back to the idle dropzone from the process-another action", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.reset.processAnother }));
    fireEvent.click(screen.getByRole("button", { name: copy.reset.processAnother }));

    expect(screen.getByTestId("dropzone")).toBeTruthy();
  });
});
