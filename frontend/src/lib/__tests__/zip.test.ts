// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { unzipSync } from "fflate";

import { buildZip, downloadBlob } from "../zip";

function textBlob(text: string): Blob {
  return new Blob([text], { type: "text/plain" });
}

function decode(bytes: Uint8Array): string {
  return new TextDecoder().decode(bytes);
}

describe("lib/zip buildZip", () => {
  it("round-trips entries in input order with identical contents", async () => {
    const entries = [
      { name: "first.txt", blob: textBlob("alpha") },
      { name: "second.txt", blob: textBlob("beta") },
      { name: "third.txt", blob: textBlob("gamma") },
    ];
    const archive = await buildZip(entries);
    const extracted = unzipSync(new Uint8Array(await archive.arrayBuffer()));
    expect(Object.keys(extracted)).toEqual(["first.txt", "second.txt", "third.txt"]);
    expect(decode(extracted["first.txt"])).toBe("alpha");
    expect(decode(extracted["second.txt"])).toBe("beta");
    expect(decode(extracted["third.txt"])).toBe("gamma");
  });

  it("preserves binary bytes exactly", async () => {
    const bytes = new Uint8Array([0, 1, 2, 254, 255, 127, 42]);
    const archive = await buildZip([{ name: "bin.dat", blob: new Blob([bytes]) }]);
    const extracted = unzipSync(new Uint8Array(await archive.arrayBuffer()));
    expect(Array.from(extracted["bin.dat"])).toEqual(Array.from(bytes));
  });

  it("returns a single application/zip Blob", async () => {
    const archive = await buildZip([{ name: "a.txt", blob: textBlob("a") }]);
    expect(archive).toBeInstanceOf(Blob);
    expect(archive.type).toBe("application/zip");
  });
});

describe("lib/zip downloadBlob", () => {
  let createUrlSpy: ReturnType<typeof vi.spyOn>;
  let revokeUrlSpy: ReturnType<typeof vi.spyOn>;
  let clickSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.useFakeTimers();
    createUrlSpy = vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:mock-url");
    revokeUrlSpy = vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("clicks a temporary download anchor with the blob URL and filename", () => {
    const blob = textBlob("payload");
    let clickedDownload = "";
    let clickedHref = "";
    clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      clickedDownload = this.download;
      clickedHref = this.href;
    });

    downloadBlob(blob, "out.zip");

    expect(createUrlSpy).toHaveBeenCalledWith(blob);
    expect(clickSpy).toHaveBeenCalledTimes(1);
    expect(clickedDownload).toBe("out.zip");
    expect(clickedHref).toBe("blob:mock-url");
  });

  it("revokes the object URL after the click completes", () => {
    const blob = textBlob("payload");
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);

    downloadBlob(blob, "out.zip");
    expect(revokeUrlSpy).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1000);
    expect(revokeUrlSpy).toHaveBeenCalledTimes(1);
    expect(revokeUrlSpy).toHaveBeenCalledWith("blob:mock-url");
  });
});
