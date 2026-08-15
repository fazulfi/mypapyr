// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi, type Mock } from "vitest";

import { getMessages } from "@/lib/messages";

const mockUseTaskPolling = vi.fn();
vi.mock("@/hooks/useTaskPolling", () => ({
  useTaskPolling: (...args: unknown[]) => mockUseTaskPolling(...args),
}));

import { PdfToJpgTool } from "@/app/[locale]/pdf-to-jpg/page";

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

function stubFetch(taskId = "task-p2j-1"): Mock {
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
          url: "https://cdn.example/output.zip",
          expires_at: "2026-01-01T00:00:00Z",
        }),
      });
    }
    return Promise.resolve({ ok: false, status: 500 });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function submitPdf(locale: "en" | "es" | "id" = "en"): Promise<void> {
  const rendered = render(<PdfToJpgTool locale={locale} />);
  selectFiles(rendered.container, [makePdf("a.pdf")]);
  fireEvent.click(
    screen.getByRole("button", { name: getMessages(locale).tools.pdfToJpg.actions.convert }),
  );
}

function stubDownloadUrl(): void {
  Object.defineProperty(window, "location", {
    configurable: true,
    writable: true,
    value: { href: "" },
  });
}

beforeEach(() => {
  idlePolling();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("PdfToJpgTool localized rendering", () => {
  it("renders the localized title, description, dropzone and button for each locale", () => {
    for (const locale of ["en", "es", "id"] as const) {
      const copy = getMessages(locale);
      const { unmount } = render(<PdfToJpgTool locale={locale} />);
      expect(
        screen.getByRole("heading", { level: 1, name: copy.tools.pdfToJpg.title }),
      ).toBeTruthy();
      expect(screen.getByText(copy.tools.pdfToJpg.description)).toBeTruthy();
      expect(screen.getByTestId("dropzone")).toBeTruthy();
      expect(
        screen.getByRole("button", { name: copy.tools.pdfToJpg.actions.convert }),
      ).toBeTruthy();
      unmount();
    }
  });

  it("disables the convert action until a PDF is selected", () => {
    const copy = getMessages("en");
    const { container } = render(<PdfToJpgTool locale="en" />);
    const button = screen.getByRole("button", {
      name: copy.tools.pdfToJpg.actions.convert,
    }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);

    selectFiles(container, [makePdf("a.pdf")]);
    const enabled = screen.getByRole("button", {
      name: copy.tools.pdfToJpg.actions.convert,
    }) as HTMLButtonElement;
    expect(enabled.disabled).toBe(false);
  });

  it("shows the uploading label and disables controls while the admission request is in flight", async () => {
    const { promise, resolve } = Promise.withResolvers<{
      ok: boolean;
      json: () => Promise<object>;
    }>();
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(promise));

    const copy = getMessages("en");
    const { container } = render(<PdfToJpgTool locale="en" />);
    selectFiles(container, [makePdf("a.pdf")]);
    fireEvent.click(screen.getByRole("button", { name: copy.tools.pdfToJpg.actions.convert }));

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: copy.tools.pdfToJpg.actions.uploading }),
      ).toBeTruthy(),
    );
    const uploadingBtn = screen.getByRole("button", {
      name: copy.tools.pdfToJpg.actions.uploading,
    }) as HTMLButtonElement;
    expect(uploadingBtn.disabled).toBe(true);

    resolve({ ok: true, json: async () => ({ task_id: "t", expires_at: "" }) });
  });
});

describe("PdfToJpgTool upload / admission contract", () => {
  it("POSTs the selected PDF to the admission endpoint using the file field", async () => {
    const fetchMock = stubFetch();
    await submitPdf("en");

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/tools/pdf-to-jpg/tasks");
    expect(init.method).toBe("POST");
    const body = init.body as FormData;
    const names = body.getAll("file").map((entry) => (entry as File).name);
    expect(names).toEqual(["a.pdf"]);
  });

  it("surfaces the error card when the admission request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await submitPdf("en");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
  });

  it("does not submit when no file is selected", () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    render(<PdfToJpgTool locale="en" />);
    expect(mock).not.toHaveBeenCalled();
  });
});

describe("PdfToJpgTool polling / result states", () => {
  it("renders the queued card after admission while the task waits", async () => {
    pollingWithStatus({ state: "queued", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdf("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.queued)).toBeTruthy());
  });

  it("renders the processing card while the task is processing", async () => {
    pollingWithStatus({ state: "processing", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdf("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.processing)).toBeTruthy());
  });

  it("fetches the download grant on download and offers download plus reset", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    const fetchMock = stubFetch("task-p2j-9");
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.states.download }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/tools/pdf-to-jpg/tasks/task-p2j-9/download/0",
      ),
    );
    expect(screen.getByRole("button", { name: copy.states.download })).toBeTruthy();
    expect(screen.getByRole("button", { name: copy.reset.processAnother })).toBeTruthy();
  });

  it("renders the localized error card with the stable message key on failure", async () => {
    pollingWithStatus({
      state: "failed",
      messageKey: "tools.pdfToJpg.errors.fileTooLarge",
      retryable: true,
      outputCount: null,
    });
    stubFetch();
    await submitPdf("id");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.getByText(getMessages("id").tools.pdfToJpg.errors.fileTooLarge)).toBeTruthy();
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

  it("resets back to the idle dropzone from the error card retry action", async () => {
    pollingWithStatus({
      state: "failed",
      messageKey: null,
      retryable: false,
      outputCount: null,
    });
    stubFetch();
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.retry }));
    fireEvent.click(screen.getByRole("button", { name: copy.states.retry }));

    expect(screen.getByTestId("dropzone")).toBeTruthy();
  });

  it("redirects to the granted download URL when download is clicked", async () => {
    stubDownloadUrl();
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    const fetchMock = stubFetch("task-p2j-dl");
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.states.download }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/tools/pdf-to-jpg/tasks/task-p2j-dl/download/0",
      ),
    );
    await waitFor(() => expect(window.location.href).toBe("https://cdn.example/output.zip"));
  });

  it("leaves the page unchanged when download is clicked without a granted URL", async () => {
    stubDownloadUrl();
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: RequestInfo) => {
        const target = String(url);
        if (target.endsWith("/tasks")) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ task_id: "task-p2j-nodl", expires_at: "" }),
          });
        }
        return Promise.resolve({ ok: false, status: 404 });
      }),
    );
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.states.download }));

    expect(window.location.href).toBe("");
  });

  it("keeps the downloadUrl null and does not crash when the grant request rejects", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: RequestInfo) => {
        const target = String(url);
        if (target.endsWith("/tasks")) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ task_id: "task-p2j-rej", expires_at: "" }),
          });
        }
        return Promise.reject(new Error("network down"));
      }),
    );
    await submitPdf("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    expect(screen.getByRole("button", { name: copy.reset.processAnother })).toBeTruthy();
  });
});

describe("PdfToJpgTool AdSlot rendering", () => {
  it("renders the AdSlot on the done phase", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdf("en");

    await waitFor(() =>
      expect(screen.getAllByLabelText("Advertisement").length).toBeGreaterThan(0),
    );
  });

  it("renders the AdSlot on the error phase", async () => {
    pollingWithStatus({
      state: "failed",
      messageKey: null,
      retryable: false,
      outputCount: null,
    });
    stubFetch();
    await submitPdf("en");

    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.getAllByLabelText("Advertisement").length).toBeGreaterThan(0);
  });

  it("renders the immediate leaderboard AdSlot on the idle phase (owner decision 2026-08-15)", () => {
    render(<PdfToJpgTool locale="en" />);
    expect(screen.getAllByLabelText("Advertisement").length).toBeGreaterThan(0);
  });

  it("renders the immediate AdSlot on the queued phase", async () => {
    pollingWithStatus({ state: "queued", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdf("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.queued)).toBeTruthy());
    expect(screen.getAllByLabelText("Advertisement").length).toBeGreaterThan(0);
  });

  it("renders the immediate AdSlot on the processing phase", async () => {
    pollingWithStatus({ state: "processing", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdf("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.processing)).toBeTruthy());
    expect(screen.getAllByLabelText("Advertisement").length).toBeGreaterThan(0);
  });
});
