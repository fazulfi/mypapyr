import { zipSync } from "fflate";

export interface ZipEntry {
  name: string;
  blob: Blob;
}

export async function buildZip(entries: Array<ZipEntry>): Promise<Blob> {
  const files: Record<string, Uint8Array> = {};
  for (const entry of entries) {
    files[entry.name] = new Uint8Array(await entry.blob.arrayBuffer());
  }
  const archive = zipSync(files, { level: 0 });
  const bytes = new Uint8Array(archive);
  return new Blob([bytes], { type: "application/zip" });
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
