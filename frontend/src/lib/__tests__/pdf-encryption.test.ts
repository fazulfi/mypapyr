// @vitest-environment jsdom
// PT-04 (FR-SHARED-09): client-side encrypted PDF detection.

import { describe, expect, it, vi } from "vitest";

import { isEncryptedPdf, SCAN_BYTES } from "@/lib/pdf-encryption";

function makePdfBytes(marker: string): Uint8Array<ArrayBuffer> {
  return new TextEncoder().encode(marker);
}

function makeFile(name: string, content: string, mime = "application/pdf"): File {
  return new File([makePdfBytes(content)], name, { type: mime });
}

describe("isEncryptedPdf", () => {
  it("returns true for a PDF with /Encrypt in its header", async () => {
    const file = makeFile("locked.pdf", "%PDF-1.7\n1 0 obj\n<< /Encrypt 123 0 R >>\nendobj");
    await expect(isEncryptedPdf(file)).resolves.toBe(true);
  });

  it("returns true when /Encrypt is in the trailer", async () => {
    const file = makeFile(
      "trailer.pdf",
      "%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\ntrailer\n<< /Size 3 /Root 1 0 R /Encrypt 3 0 R >>",
    );
    await expect(isEncryptedPdf(file)).resolves.toBe(true);
  });

  it("returns false for a plain PDF without /Encrypt", async () => {
    const file = makeFile("plain.pdf", "%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\nendobj");
    await expect(isEncryptedPdf(file)).resolves.toBe(false);
  });

  it("returns false for a non-PDF file type", async () => {
    const file = new File(["hello"], "readme.txt", { type: "text/plain" });
    await expect(isEncryptedPdf(file)).resolves.toBe(false);
  });

  it("returns false for a file whose name does not end in .pdf", async () => {
    const file = new File(["hello"], "readme", { type: "application/pdf" });
    await expect(isEncryptedPdf(file)).resolves.toBe(false);
  });

  it("returns false when FileReader fails", async () => {
    // Stub FileReader to simulate read error
    vi.spyOn(globalThis, "FileReader").mockImplementation(() => {
      const reader = new (class {
        result: string | null = null;
        error = new DOMException("read error");
        onload: (() => void) | null = null;
        onerror: (() => void) | null = null;
        readAsText(_blob: Blob): void {
          this.onerror?.();
        }
      })();
      return reader as unknown as FileReader;
    });

    const file = makeFile("locked.pdf", "/Encrypt");
    await expect(isEncryptedPdf(file)).resolves.toBe(false);

    vi.restoreAllMocks();
  });

  it("reads only the first SCAN_BYTES of large files", async () => {
    // Create a large file with /Encrypt past SCAN_BYTES
    const header = "%PDF-1.7\n%";
    const large = header + "a".repeat(SCAN_BYTES - header.length + 100) + "/Encrypt";
    const file = makeFile("big.pdf", large);
    // /Encrypt is beyond the scan window, so should return false
    await expect(isEncryptedPdf(file)).resolves.toBe(false);
  });
});
