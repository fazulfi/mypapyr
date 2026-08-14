// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { locales } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

import { Dropzone } from "../uploader/Dropzone";

function makeFile(name: string, type: string, size: number): File {
  const file = new File([new Uint8Array(size)], name, { type });
  Object.defineProperty(file, "size", { value: size });
  return file;
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("components/Dropzone labels", () => {
  it("renders the localized drop text, browse CTA, and hidden a11y label for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { unmount } = render(
        <Dropzone files={[]} onChange={() => undefined} locale={locale} />,
      );
      expect(screen.getByText((content) => content.includes(copy.uploader.drop))).toBeTruthy();
      expect(screen.getByText((content) => content.includes(copy.uploader.browseCta))).toBeTruthy();
      expect(screen.getByLabelText(copy.uploader.browse)).toBeTruthy();
      unmount();
    }
  });
});

describe("components/Dropzone filtering", () => {
  it("passes oversized files through unchanged when no size limit is set", () => {
    const onChange = vi.fn();
    const { container } = render(
      <Dropzone files={[]} onChange={onChange} locale="en" accept={["application/pdf"]} />,
    );
    const input = container.querySelector("input[type='file']") as HTMLInputElement;
    const files = [makeFile("a.pdf", "application/pdf", 1_000_000)];
    fireEvent.change(input, { target: { files } });
    expect(onChange).toHaveBeenCalledWith([files[0]]);
  });

  it("silently excludes files that exceed maxSizeBytes", () => {
    const onChange = vi.fn();
    const { container } = render(
      <Dropzone files={[]} onChange={onChange} locale="en" maxSizeBytes={100} />,
    );
    const input = container.querySelector("input[type='file']") as HTMLInputElement;
    const small = makeFile("ok.txt", "text/plain", 50);
    const big = makeFile("big.txt", "text/plain", 500);
    fireEvent.change(input, { target: { files: [small, big] } });
    expect(onChange).toHaveBeenCalledWith([small]);
  });

  it("silently excludes files whose type is not accepted", () => {
    const onChange = vi.fn();
    const { container } = render(
      <Dropzone files={[]} onChange={onChange} locale="en" accept={["application/pdf"]} />,
    );
    const input = container.querySelector("input[type='file']") as HTMLInputElement;
    const pdf = makeFile("a.pdf", "application/pdf", 10);
    const png = makeFile("b.png", "image/png", 10);
    fireEvent.change(input, { target: { files: [pdf, png] } });
    expect(onChange).toHaveBeenCalledWith([pdf]);
  });

  it("keeps only the first maxFiles files after filtering", () => {
    const onChange = vi.fn();
    const { container } = render(
      <Dropzone
        files={[]}
        onChange={onChange}
        locale="en"
        accept={["application/pdf"]}
        maxFiles={2}
      />,
    );
    const input = container.querySelector("input[type='file']") as HTMLInputElement;
    const one = makeFile("1.pdf", "application/pdf", 10);
    const two = makeFile("2.pdf", "application/pdf", 10);
    const three = makeFile("3.pdf", "application/pdf", 10);
    fireEvent.change(input, { target: { files: [one, two, three] } });
    expect(onChange).toHaveBeenCalledWith([one, two]);
  });

  it("applies the same filters to dropped files", () => {
    const onChange = vi.fn();
    const { container } = render(
      <Dropzone
        files={[]}
        onChange={onChange}
        locale="en"
        accept={["application/pdf"]}
        maxSizeBytes={100}
        maxFiles={1}
      />,
    );
    const zone = container.firstElementChild as HTMLElement;
    const ok = makeFile("ok.pdf", "application/pdf", 50);
    const big = makeFile("big.pdf", "application/pdf", 500);
    const png = makeFile("img.png", "image/png", 10);
    fireEvent.drop(zone, { dataTransfer: { files: [ok, big, png] } });
    expect(onChange).toHaveBeenCalledWith([ok]);
  });

  it("reports an empty selection when every file is filtered out", () => {
    const onChange = vi.fn();
    const { container } = render(
      <Dropzone files={[]} onChange={onChange} locale="en" accept={["application/pdf"]} />,
    );
    const input = container.querySelector("input[type='file']") as HTMLInputElement;
    const png = makeFile("b.png", "image/png", 10);
    fireEvent.change(input, { target: { files: [png] } });
    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("does not open the picker while disabled", () => {
    const onChange = vi.fn();
    const { container } = render(<Dropzone files={[]} onChange={onChange} locale="en" disabled />);
    const input = container.querySelector("input[type='file']") as HTMLInputElement;
    expect(input.disabled).toBe(true);
    const zone = container.firstElementChild as HTMLElement;
    fireEvent.click(zone);
    expect(onChange).not.toHaveBeenCalled();
  });
});

describe("components/Dropzone rich reference markup", () => {
  it("renders the accent icon chip, hero copy, and localized size hint for every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      const { container, unmount } = render(
        <Dropzone
          files={[]}
          onChange={() => undefined}
          locale={locale}
          accept={["application/pdf"]}
          maxSizeBytes={20 * 1024 * 1024}
        />,
      );
      const zone = container.firstElementChild as HTMLElement;
      expect(zone.className).toContain("rounded-2xl");
      expect(zone.className).toContain("border-dashed");
      expect(zone.className).toContain("bg-white");
      expect(zone.className).toContain("border-slate-300 hover:border-accent/50");
      const chip = zone.querySelector("[class*='bg-accent/10']") as HTMLElement;
      expect(chip).toBeTruthy();
      expect(chip.className).toContain("rounded-xl");
      expect(zone.querySelector("svg[width='26']")).toBeTruthy();
      expect(screen.getByText(copy.uploader.dropHint.replace("{size}", "20"))).toBeTruthy();
      unmount();
    }
  });

  it("switches to the accent drag state on dragOver and back on dragLeave", () => {
    const { container } = render(<Dropzone files={[]} onChange={() => undefined} locale="en" />);
    const zone = container.firstElementChild as HTMLElement;
    fireEvent.dragOver(zone);
    expect(zone.className).toContain("border-accent bg-accent/5");
    fireEvent.dragLeave(zone);
    expect(zone.className).toContain("border-slate-300 hover:border-accent/50");
  });
});
