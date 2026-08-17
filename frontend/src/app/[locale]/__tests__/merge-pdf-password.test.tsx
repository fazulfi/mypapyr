// @vitest-environment jsdom
// PT-04 (FR-SHARED-09 / FR-MERGE-04): encrypted-PDF password flow on the
// Merge tool page — detection, per-file PasswordInput rendering, submit-time
// password_<i> fields, reset clearing, and the never-persist guarantee.

import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { neverPersist } from "@/lib/password";
import { MergePdfTool } from "@/app/[locale]/merge-pdf/page";

const { isEncryptedPdf } = vi.hoisted(() => ({
  isEncryptedPdf: vi.fn(async (_file: File) => false),
}));

vi.mock("@/lib/pdf-encryption", () => ({ isEncryptedPdf }));

const { fetchMock } = vi.hoisted(() => ({ fetchMock: vi.fn() }));

vi.mock("@/lib/taskPolling", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/taskPolling")>();
  return { ...actual, fetchTaskStatus: fetchMock };
});

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  localStorage.clear();
  sessionStorage.clear();
});

function makeFile(name: string, size = 1024, lastModified = 100): File {
  return new File([new Uint8Array(size)], name, { type: "application/pdf", lastModified });
}

function filesFor(...names: string[]): File[] {
  return names.map((name, i) => makeFile(name, 100 + i, i + 1));
}

function selectFiles(files: File[]): void {
  render(<MergePdfTool locale="en" />);
  const input = document.querySelector("input[type='file']") as HTMLInputElement;
  fireEvent.change(input, { target: { files } });
}

describe("MergePdfTool encrypted-password flow", () => {
  it("detects encrypted files lazily and renders one PasswordInput per locked file", async () => {
    const plain = makeFile("plain.pdf", 100, 1);
    const locked = makeFile("locked.pdf", 200, 2);
    isEncryptedPdf.mockImplementation(async (file: File) => file.name === "locked.pdf");

    selectFiles([plain, locked]);
    await act(async () => {});

    const labels = screen.getAllByLabelText(/password/i);
    expect(labels).toHaveLength(1);
    expect(screen.getByText("Password for locked.pdf")).toBeTruthy();
    expect(screen.queryByText("Password for plain.pdf")).toBeNull();
  });

  it("submits password_<i> fields only for encrypted files, in files order", async () => {
    const plain = makeFile("plain.pdf", 100, 1);
    const locked = makeFile("locked.pdf", 200, 2);
    isEncryptedPdf.mockImplementation(async (file: File) => file.name === "locked.pdf");

    selectFiles([plain, locked]);
    await act(async () => {});

    const input = screen.getByLabelText(/password/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "s3cret" } });

    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ task_id: "t-1" }), {
        status: 202,
        headers: { "Content-Type": "application/json" },
      }),
    );

    fireEvent.click(screen.getByRole("button", { name: "Merge PDFs" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/tools/merge-pdf/tasks",
        expect.objectContaining({ method: "POST" }),
      );
    });

    const body = fetchMock.mock.calls[0][1] as { body: FormData };
    const form = body.body;
    expect(form.getAll("files")).toHaveLength(2);
    expect(form.get("password_0")).toBeNull();
    expect(form.get("password_1")).toBe("s3cret");

    // The password must never be written to any persistent store.
    expect(neverPersist("s3cret")).toBe(true);
  });

  it("keeps passwords per file id across a reorder via dropzone onChange", async () => {
    const first = makeFile("a.pdf", 100, 1);
    const second = makeFile("b.pdf", 200, 2);
    isEncryptedPdf.mockResolvedValue(true);

    selectFiles([first, second]);
    await act(async () => {});

    const inputs = screen.getAllByLabelText(/password/i);
    fireEvent.change(inputs[0], { target: { value: "pw-a" } });
    fireEvent.change(inputs[1], { target: { value: "pw-b" } });

    // Reordering through the Dropzone replaces the file list; ids stay stable.
    fireEvent.change(document.querySelector("input[type='file']") as HTMLInputElement, {
      target: { files: [second, first] },
    });
    await act(async () => {});

    const after = screen.getAllByLabelText(/password/i);
    expect(after).toHaveLength(2);
    const valueById = new Map<string, string>();
    const labels = screen.getAllByText(/^Password for /) as HTMLElement[];
    for (let i = 0; i < labels.length; i++) {
      const label = labels[i];
      const name = label.textContent?.replace("Password for ", "") ?? "";
      valueById.set(name, (after[i] as HTMLInputElement).value);
    }
    expect(valueById.get("a.pdf")).toBe("pw-a");
    expect(valueById.get("b.pdf")).toBe("pw-b");
  });

  it("clears all passwords on reset", async () => {
    const locked = makeFile("locked.pdf", 200, 2);
    const plain = makeFile("plain.pdf", 100, 1);
    isEncryptedPdf.mockImplementation(async (file: File) => file.name === "locked.pdf");

    selectFiles([locked, plain]);
    await act(async () => {});
    const input = screen.getByLabelText(/password/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "s3cret" } });

    // Complete a task so the DoneCard with "Process another file" appears.
    // The page's plain fetch() calls pass a string URL and await a Response;
    // fetchTaskStatus calls pass an {baseUrl, capabilities} object and await
    // a parsed TaskStatus — route on the arg type and return the right shape.
    fetchMock
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ task_id: "t-1" }), {
          status: 202,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockImplementation(async (url: unknown, ..._rest: unknown[]) => {
        if (typeof url !== "string") {
          return {
            task_id: "t-1",
            tool: "merge-pdf",
            state: "done",
            progress: null,
            expires_at: null,
            result: { output_count: 1, total_bytes: 10 },
          };
        }
        if (url.includes("/download")) {
          return new Response(JSON.stringify({ url: "https://example.com/out" }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }
        return new Response("{}", { status: 404 });
      });

    fireEvent.click(screen.getByRole("button", { name: "Merge PDFs" }));

    // useTaskPolling polls on a 2000 ms interval, so the done card appears
    // only after the first poll fires — give findBy enough headroom.
    const reset = await screen.findByRole(
      "button",
      { name: /process another file/i },
      {
        timeout: 4000,
      },
    );
    await act(async () => {
      fireEvent.click(reset);
    });

    expect(screen.queryByLabelText(/password/i)).toBeNull();
    expect(neverPersist("s3cret")).toBe(true);
  });

  it("renders no PasswordInput when no file is encrypted", async () => {
    isEncryptedPdf.mockResolvedValue(false);
    selectFiles(filesFor("a.pdf", "b.pdf"));
    await act(async () => {});
    expect(screen.queryByLabelText(/password/i)).toBeNull();
  });

  it("fails a submit with a too-long password instead of uploading", async () => {
    const locked = makeFile("locked.pdf", 200, 2);
    const plain = makeFile("plain.pdf", 100, 1);
    isEncryptedPdf.mockImplementation(async (file: File) => file.name === "locked.pdf");
    selectFiles([locked, plain]);
    await act(async () => {});

    const input = screen.getByLabelText(/password/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "x".repeat(1025) } });
    fireEvent.click(screen.getByRole("button", { name: "Merge PDFs" }));

    expect(fetchMock).not.toHaveBeenCalled();
  });
});
