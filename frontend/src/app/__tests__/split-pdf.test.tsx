// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { locales } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

import { SplitPdfTool } from "../[locale]/split-pdf/page";

function makePdf(): File {
  return new File([new Uint8Array(1024)], "test.pdf", { type: "application/pdf" });
}

function makeResponse(
  status: number,
  body?: unknown,
): {
  ok: boolean;
  status: number;
  json: () => Promise<unknown>;
} {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body ?? {},
  };
}

function selectFile(): void {
  const fileInput = screen.getByLabelText(getMessages("en").uploader.browse);
  fireEvent.change(fileInput, { target: { files: [makePdf()] } });
}

function typeRanges(locale: "en", value: string): HTMLInputElement {
  const rangeInput = screen.getByLabelText(getMessages(locale).tools.split.ranges.label);
  fireEvent.change(rangeInput, { target: { value } });
  return rangeInput as HTMLInputElement;
}

let fetchMock = vi.fn();

beforeEach(() => {
  window.sessionStorage.clear();
  fetchMock = vi.fn().mockResolvedValue(makeResponse(202, { task_id: "t-1" }));
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("split-pdf ranges input labels and accessibility", () => {
  it("exposes the labelled optional range field with help copy in every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { unmount } = render(<SplitPdfTool locale={locale} />);
      const input = screen.getByLabelText(copy.tools.split.ranges.label);
      expect(input.getAttribute("aria-describedby")).toBe("split-ranges-help");
      expect(input.getAttribute("placeholder")).toBeNull();
      expect(screen.getByText(copy.tools.split.ranges.help)).toBeTruthy();
      unmount();
    }
  });

  it("shows the default one-per-page note while ranges are empty", () => {
    const copy = getMessages("en");
    render(<SplitPdfTool locale="en" />);
    expect(screen.getByText(copy.tools.split.ranges.previewHeading)).toBeTruthy();
    expect(screen.getByText(copy.tools.split.ranges.defaultNote)).toBeTruthy();
  });
});

describe("split-pdf ranges submission contract", () => {
  it("omits the ranges field from the multipart body by default", async () => {
    render(<SplitPdfTool locale="en" />);
    selectFile();
    fireEvent.click(
      screen.getByRole("button", { name: getMessages("en").tools.split.actions.split }),
    );
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [, options] = fetchMock.mock.calls[0];
    const form = options.body as FormData;
    expect(form.get("file")).toBeInstanceOf(File);
    expect(form.get("ranges")).toBeNull();
  });

  it("submits canonicalized ranges with surrounding whitespace removed", async () => {
    render(<SplitPdfTool locale="en" />);
    selectFile();
    typeRanges("en", " 1-3 , 5 ");
    fireEvent.click(
      screen.getByRole("button", { name: getMessages("en").tools.split.actions.split }),
    );
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [, options] = fetchMock.mock.calls[0];
    const form = options.body as FormData;
    expect(form.get("ranges")).toBe("1-3,5");
  });
});

describe("split-pdf ordered live preview", () => {
  it("renders each comma token as an ordered output, preserving duplicates and overlaps", () => {
    render(<SplitPdfTool locale="en" />);
    typeRanges("en", "2-4,1,2-4");
    expect(screen.getByText(getMessages("en").tools.split.ranges.previewHeading)).toBeTruthy();
    const outputs = screen.getAllByRole("listitem").map((item) => item.textContent ?? "");
    expect(outputs).toEqual(["Output 1: pages 2-4", "Output 2: page 1", "Output 3: pages 2-4"]);
  });

  it("localizes the preview for Spanish and Indonesian", () => {
    for (const locale of ["es", "id"] as const) {
      const copy = getMessages(locale);
      const { unmount } = render(<SplitPdfTool locale={locale} />);
      const input = screen.getByLabelText(copy.tools.split.ranges.label);
      fireEvent.change(input, { target: { value: "3" } });
      expect(
        screen.getByText(
          copy.tools.split.ranges.previewItemSingle.replace("{index}", "1").replace("{pages}", "3"),
        ),
      ).toBeTruthy();
      unmount();
    }
  });
});

describe("split-pdf client validation blocks submission without POST", () => {
  const cases = [
    { spec: "abc", error: "malformed" },
    { spec: "1,,2", error: "malformed" },
    { spec: "1 - 3", error: "malformed" },
    { spec: "1-2-3", error: "malformed" },
    { spec: "5-2", error: "reversed" },
    { spec: "0", error: "zero" },
    { spec: "0-5", error: "zero" },
  ] as const;

  it.each(cases)("rejects $spec with the localized $error error", ({ spec, error }) => {
    const copy = getMessages("en");
    render(<SplitPdfTool locale="en" />);
    selectFile();
    const input = typeRanges("en", spec);
    expect(screen.getByText(copy.tools.split.ranges.errors[error])).toBeTruthy();
    expect(input.getAttribute("aria-invalid")).toBe("true");
    expect(input.getAttribute("aria-describedby")).toBe("split-ranges-help split-ranges-error");
    expect(screen.queryByText(copy.tools.split.ranges.previewHeading)).toBeNull();
    const splitButton = screen.getByRole("button", {
      name: copy.tools.split.actions.split,
    }) as HTMLButtonElement;
    expect(splitButton.disabled).toBe(true);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects more than 100 outputs", () => {
    const copy = getMessages("en");
    render(<SplitPdfTool locale="en" />);
    selectFile();
    const spec = Array.from({ length: 101 }, (_, index) => `${index + 1}`).join(",");
    typeRanges("en", spec);
    expect(screen.getByText(copy.tools.split.ranges.errors.tooManyOutputs)).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects specs longer than 2000 characters", () => {
    const copy = getMessages("en");
    render(<SplitPdfTool locale="en" />);
    selectFile();
    const spec = Array(65).fill("123456789012345-123456789012345").join(",");
    typeRanges("en", spec);
    expect(screen.getByText(copy.tools.split.ranges.errors.tooLong)).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe("split-pdf server rejection mapping", () => {
  it("maps a 400 error.badRequest after admission to localized guidance without page numbers", async () => {
    const copy = getMessages("en");
    fetchMock = vi
      .fn()
      .mockResolvedValue(makeResponse(400, { detail: { messageKey: "error.badRequest" } }));
    vi.stubGlobal("fetch", fetchMock);
    render(<SplitPdfTool locale="en" />);
    selectFile();
    typeRanges("en", "1-999");
    fireEvent.click(screen.getByRole("button", { name: copy.tools.split.actions.split }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    await waitFor(() =>
      expect(screen.getByText(copy.tools.split.ranges.errors.serverRejected)).toBeTruthy(),
    );
    expect(screen.getByLabelText(copy.tools.split.ranges.label)).toBeTruthy();
  });

  it("keeps the generic error card for non-badRequest failures", async () => {
    const copy = getMessages("en");
    fetchMock = vi.fn().mockResolvedValue(makeResponse(503));
    vi.stubGlobal("fetch", fetchMock);
    render(<SplitPdfTool locale="en" />);
    selectFile();
    typeRanges("en", "1-3");
    fireEvent.click(screen.getByRole("button", { name: copy.tools.split.actions.split }));
    await waitFor(() => expect(screen.getByText(copy.states.error)).toBeTruthy());
  });
});

describe("split-pdf reset", () => {
  it("clears the range input and restores the default preview", async () => {
    const copy = getMessages("en");
    fetchMock = vi.fn().mockResolvedValue(makeResponse(503));
    vi.stubGlobal("fetch", fetchMock);
    render(<SplitPdfTool locale="en" />);
    selectFile();
    typeRanges("en", "1-3");
    fireEvent.click(screen.getByRole("button", { name: copy.tools.split.actions.split }));
    await waitFor(() => expect(screen.getByText(copy.states.error)).toBeTruthy());
    fireEvent.click(screen.getByRole("button", { name: copy.reset.processAnother }));
    const input = screen.getByLabelText(copy.tools.split.ranges.label) as HTMLInputElement;
    expect(input.value).toBe("");
    expect(screen.getByText(copy.tools.split.ranges.defaultNote)).toBeTruthy();
  });
});
