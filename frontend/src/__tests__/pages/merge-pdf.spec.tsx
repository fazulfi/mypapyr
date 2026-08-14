// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getMessages } from "@/lib/messages";

const mockUseTaskPolling = vi.fn();
vi.mock("@/hooks/useTaskPolling", () => ({
  useTaskPolling: (...args: unknown[]) => mockUseTaskPolling(...args),
}));

import { MergePdfTool } from "@/app/[locale]/merge-pdf/page";

function makePdf(name: string, size = 128): File {
  return new File([new Uint8Array(size)], name, { type: "application/pdf" });
}

function makeNonPdf(name: string): File {
  return new File([new Uint8Array(128)], name, { type: "text/plain" });
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

function stubFetch(taskId = "task-mrg-1"): ReturnType<typeof vi.fn> {
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
          url: "https://cdn.example/merged.pdf",
          expires_at: "2026-01-01T00:00:00Z",
        }),
      });
    }
    return Promise.resolve({ ok: false, status: 500 });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function submitPdfs(locale: "en" | "es" | "id" = "en", fileNames?: string[]): Promise<void> {
  const rendered = render(<MergePdfTool locale={locale} />);
  const names = fileNames || ["a.pdf", "b.pdf"];
  selectFiles(
    rendered.container,
    names.map((n) => makePdf(n)),
  );
  fireEvent.click(
    screen.getByRole("button", { name: getMessages(locale).tools.merge.actions.merge }),
  );
}

beforeEach(() => {
  idlePolling();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("MergePdfTool localized rendering", () => {
  it("renders the localized title, description, dropzone and button for each locale", () => {
    for (const locale of ["en", "es", "id"] as const) {
      const copy = getMessages(locale);
      const { unmount } = render(<MergePdfTool locale={locale} />);
      expect(screen.getByRole("heading", { level: 1, name: copy.tools.merge.title })).toBeTruthy();
      expect(screen.getByText(copy.tools.merge.description)).toBeTruthy();
      expect(screen.getByTestId("dropzone")).toBeTruthy();
      expect(screen.getByRole("button", { name: copy.tools.merge.actions.merge })).toBeTruthy();
      unmount();
    }
  });

  it("disables the merge action until at least two PDFs are selected", () => {
    const copy = getMessages("en");
    const { container } = render(<MergePdfTool locale="en" />);
    const button = screen.getByRole("button", {
      name: copy.tools.merge.actions.merge,
    }) as HTMLButtonElement;

    // Initially disabled (no files)
    expect(button.disabled).toBe(true);

    // One file still disabled (needs >= 2)
    selectFiles(container, [makePdf("one.pdf")]);
    const oneFileBtn = screen.getByRole("button", {
      name: copy.tools.merge.actions.merge,
    }) as HTMLButtonElement;
    expect(oneFileBtn.disabled).toBe(true);

    // Two files enables
    selectFiles(container, [makePdf("one.pdf"), makePdf("two.pdf")]);
    const twoFilesBtn = screen.getByRole("button", {
      name: copy.tools.merge.actions.merge,
    }) as HTMLButtonElement;
    expect(twoFilesBtn.disabled).toBe(false);
  });

  it("restricts the file input to application/pdf", () => {
    const { container } = render(<MergePdfTool locale="en" />);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input.getAttribute("accept")).toBe("application/pdf");
  });

  it("filters out non-PDF files from the selected set", () => {
    const { container } = render(<MergePdfTool locale="en" />);
    selectFiles(container, [makePdf("ok.pdf"), makeNonPdf("notes.txt")]);
    const mergeBtn = screen.getByRole("button", {
      name: getMessages("en").tools.merge.actions.merge,
    }) as HTMLButtonElement;
    // Only the PDF remains -> still only one file -> disabled
    expect(mergeBtn.disabled).toBe(true);
  });
});

describe("MergePdfTool upload / admission contract", () => {
  it("POSTs selected PDFs in order to the admission endpoint using the files field", async () => {
    const fetchMock = stubFetch();
    await submitPdfs("en", ["first.pdf", "second.pdf"]);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/tools/merge-pdf/tasks");
    expect(init.method).toBe("POST");
    const body = init.body as FormData;
    const names = body.getAll("files").map((entry) => (entry as File).name);
    expect(names).toEqual(["first.pdf", "second.pdf"]);
  });

  it("surfaces the error alert when the admission request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await submitPdfs("en");
    await waitFor(() =>
      expect(screen.getByText(getMessages("en").tools.merge.errors.uploadFailed)).toBeTruthy(),
    );
  });
});

describe("MergePdfTool polling / result states", () => {
  it("renders the queued card after admission while the task waits", async () => {
    pollingWithStatus({ state: "queued", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdfs("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.queued)).toBeTruthy());
  });

  it("renders the processing card while the task is processing", async () => {
    pollingWithStatus({ state: "processing", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdfs("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.processing)).toBeTruthy());
  });

  it("fetches the download grant on demand and offers download plus reset when done", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    const fetchMock = stubFetch("task-mrg-9");
    await submitPdfs("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.states.download }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith("/api/v1/tools/merge-pdf/tasks/task-mrg-9/download/0"),
    );
    expect(screen.getByRole("button", { name: copy.reset.processAnother })).toBeTruthy();
  });

  it("renders the localized error card with the stable message key on failure", async () => {
    pollingWithStatus({
      state: "failed",
      errorCategory: "tools.merge.errors.fileTooLarge",
      retryable: false,
      outputCount: null,
    });
    stubFetch();
    await submitPdfs("id");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.getByText(getMessages("id").tools.merge.errors.fileTooLarge)).toBeTruthy();
  });

  it("resets back to the idle dropzone from the process-another action", async () => {
    pollingWithStatus({ state: "done", messageKey: null, retryable: false, outputCount: 1 });
    stubFetch();
    await submitPdfs("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.reset.processAnother }));
    fireEvent.click(screen.getByRole("button", { name: copy.reset.processAnother }));

    expect(screen.getByTestId("dropzone")).toBeTruthy();
  });
});
