// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getMessages } from "@/lib/messages";

const mockUseTaskPolling = vi.fn();
vi.mock("@/hooks/useTaskPolling", () => ({
  useTaskPolling: (...args: unknown[]) => mockUseTaskPolling(...args),
}));

import { JpgToPdfTool } from "@/app/[locale]/jpg-to-pdf/page";

function makeJpeg(name: string, size = 64): File {
  return new File([new Uint8Array(size)], name, { type: "image/jpeg" });
}

function selectFiles(container: HTMLElement, files: File[]): void {
  const input = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(input, { target: { files } });
}

function idlePolling(): void {
  mockUseTaskPolling.mockReturnValue({ status: null, refresh: vi.fn(), stop: vi.fn() });
}

function stubAdmissionFetch(taskId = "task-j2p-1"): ReturnType<typeof vi.fn> {
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
          url: "https://cdn.example/result.pdf",
          expires_at: "2026-01-01T00:00:00Z",
        }),
      });
    }
    return Promise.resolve({ ok: false, status: 500 });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function submitImage(locale: "en" | "es" | "id" = "en"): Promise<ReturnType<typeof render>> {
  const rendered = render(<JpgToPdfTool locale={locale} />);
  selectFiles(rendered.container, [makeJpeg("one.jpg"), makeJpeg("two.jpeg")]);
  fireEvent.click(
    screen.getByRole("button", { name: getMessages(locale).tools.jpgToPdf.actions.convert }),
  );
  return rendered;
}

beforeEach(() => {
  idlePolling();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("JpgToPdfTool localized rendering", () => {
  it("renders the localized title, notes, and dropzone for each locale", () => {
    for (const locale of ["en", "es", "id"] as const) {
      const copy = getMessages(locale);
      const { unmount } = render(<JpgToPdfTool locale={locale} />);
      expect(
        screen.getByRole("heading", { level: 1, name: copy.tools.jpgToPdf.title }),
      ).toBeTruthy();
      expect(screen.getByTestId("dropzone")).toBeTruthy();
      expect(screen.getByText(copy.tools.jpgToPdf.paperNote)).toBeTruthy();
      expect(screen.getByText(copy.tools.jpgToPdf.metadataNote)).toBeTruthy();
      unmount();
    }
  });

  it("disables the convert action until at least one image is selected", () => {
    const copy = getMessages("en");
    const { container } = render(<JpgToPdfTool locale="en" />);
    const button = screen.getByRole("button", {
      name: copy.tools.jpgToPdf.actions.convert,
    }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);

    selectFiles(container, [makeJpeg("a.jpg")]);
    const enabledButton = screen.getByRole("button", {
      name: copy.tools.jpgToPdf.actions.convert,
    }) as HTMLButtonElement;
    expect(enabledButton.disabled).toBe(false);
  });

  it("restricts the file input to image/jpeg (JPG/JPEG)", () => {
    const { container } = render(<JpgToPdfTool locale="en" />);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input.getAttribute("accept")).toBe("image/jpeg");
  });
});

describe("JpgToPdfTool upload / admission contract", () => {
  it("POSTs selected images in order to the admission endpoint using the files field", async () => {
    const fetchMock = stubAdmissionFetch();
    await submitImage("en");

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/tools/jpg-to-pdf/tasks");
    expect(init.method).toBe("POST");
    const body = init.body as FormData;
    const names = body.getAll("files").map((entry) => (entry as File).name);
    expect(names).toEqual(["one.jpg", "two.jpeg"]);
  });

  it("shows the uploading label while the admission request is in flight", async () => {
    let resolveUpload: (value: unknown) => void = () => undefined;
    const pending = new Promise((resolve) => {
      resolveUpload = resolve;
    });
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(pending));

    const copy = getMessages("en");
    const { container } = render(<JpgToPdfTool locale="en" />);
    selectFiles(container, [makeJpeg("a.jpg")]);
    fireEvent.click(screen.getByRole("button", { name: copy.tools.jpgToPdf.actions.convert }));

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: copy.tools.jpgToPdf.actions.uploading }),
      ).toBeTruthy(),
    );
    resolveUpload({ ok: true, json: async () => ({ task_id: "t", expires_at: "" }) });
  });

  it("surfaces the error card when the admission request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await submitImage("en");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
  });
});

describe("JpgToPdfTool polling / result states", () => {
  it("renders the queued card after admission while the task waits", async () => {
    mockUseTaskPolling.mockImplementation(
      ({ taskId, enabled }: { taskId: string; enabled: boolean }) =>
        enabled && taskId !== ""
          ? {
              status: { state: "queued", messageKey: null, retryable: false, outputCount: null },
              refresh: vi.fn(),
              stop: vi.fn(),
            }
          : { status: null, refresh: vi.fn(), stop: vi.fn() },
    );
    stubAdmissionFetch();
    await submitImage("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.queued)).toBeTruthy());
  });

  it("renders the processing card while the task is processing", async () => {
    mockUseTaskPolling.mockImplementation(
      ({ taskId, enabled }: { taskId: string; enabled: boolean }) =>
        enabled && taskId !== ""
          ? {
              status: {
                state: "processing",
                messageKey: null,
                retryable: false,
                outputCount: null,
              },
              refresh: vi.fn(),
              stop: vi.fn(),
            }
          : { status: null, refresh: vi.fn(), stop: vi.fn() },
    );
    stubAdmissionFetch();
    await submitImage("en");
    await waitFor(() => expect(screen.getByText(getMessages("en").states.processing)).toBeTruthy());
  });

  it("fetches the single download grant and offers download plus reset when done", async () => {
    mockUseTaskPolling.mockImplementation(
      ({ taskId, enabled }: { taskId: string; enabled: boolean }) =>
        enabled && taskId !== ""
          ? {
              status: { state: "done", messageKey: null, retryable: false, outputCount: 1 },
              refresh: vi.fn(),
              stop: vi.fn(),
            }
          : { status: null, refresh: vi.fn(), stop: vi.fn() },
    );
    const fetchMock = stubAdmissionFetch("task-j2p-9");
    await submitImage("en");

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/tools/jpg-to-pdf/tasks/task-j2p-9/download/0",
      ),
    );
    const copy = getMessages("en");
    expect(screen.getByRole("button", { name: copy.states.download })).toBeTruthy();
    expect(screen.getByRole("button", { name: copy.reset.processAnother })).toBeTruthy();
  });

  it("renders the localized error card with the stable message key on failure", async () => {
    mockUseTaskPolling.mockImplementation(
      ({ taskId, enabled }: { taskId: string; enabled: boolean }) =>
        enabled && taskId !== ""
          ? {
              status: {
                state: "failed",
                messageKey: "tools.jpgToPdf.errors.fileTooLarge",
                retryable: false,
                outputCount: null,
              },
              refresh: vi.fn(),
              stop: vi.fn(),
            }
          : { status: null, refresh: vi.fn(), stop: vi.fn() },
    );
    stubAdmissionFetch();
    await submitImage("es");
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    expect(screen.getByText(getMessages("es").tools.jpgToPdf.errors.fileTooLarge)).toBeTruthy();
  });

  it("resets back to the idle dropzone from the process-another action", async () => {
    mockUseTaskPolling.mockImplementation(
      ({ taskId, enabled }: { taskId: string; enabled: boolean }) =>
        enabled && taskId !== ""
          ? {
              status: { state: "done", messageKey: null, retryable: false, outputCount: 1 },
              refresh: vi.fn(),
              stop: vi.fn(),
            }
          : { status: null, refresh: vi.fn(), stop: vi.fn() },
    );
    stubAdmissionFetch();
    await submitImage("en");

    const copy = getMessages("en");
    await waitFor(() => screen.getByRole("button", { name: copy.states.download }));
    fireEvent.click(screen.getByRole("button", { name: copy.reset.processAnother }));

    expect(screen.getByTestId("dropzone")).toBeTruthy();
  });
});
