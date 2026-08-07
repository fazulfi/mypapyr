import { buildZip, downloadBlob, type ZipEntry } from "./zip";

export async function fetchDownloadGrant(
  toolId: string,
  taskId: string,
  output: number,
): Promise<string | null> {
  const response = await fetch(`/api/v1/tools/${toolId}/tasks/${taskId}/download/${output}`);
  if (!response.ok) return null;
  const grant = (await response.json()) as { url: string };
  return grant.url;
}

export async function fetchAllOutputsAsZip(
  toolId: string,
  taskId: string,
  outputCount: number,
  entryName: (index: number) => string,
): Promise<Blob | null> {
  const entries: ZipEntry[] = [];
  for (let index = 0; index < outputCount; index += 1) {
    const url = await fetchDownloadGrant(toolId, taskId, index);
    if (url === null) return null;
    const response = await fetch(url);
    if (!response.ok) return null;
    const blob = await response.blob();
    entries.push({ name: entryName(index), blob });
  }
  return buildZip(entries);
}

export async function downloadTaskResult(options: {
  toolId: string;
  taskId: string;
  outputCount: number;
  entryName: (index: number) => string;
  zipFilename: string;
}): Promise<void> {
  const { toolId, taskId, outputCount, entryName, zipFilename } = options;
  if (outputCount <= 1) {
    const url = await fetchDownloadGrant(toolId, taskId, 0);
    if (url !== null) window.location.href = url;
    return;
  }
  const zipBlob = await fetchAllOutputsAsZip(toolId, taskId, outputCount, entryName);
  if (zipBlob !== null) downloadBlob(zipBlob, zipFilename);
}
