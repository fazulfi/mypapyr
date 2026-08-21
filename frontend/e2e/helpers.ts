import { expect, type Page, type Route } from "@playwright/test";

export type Locale = "en" | "es" | "id";
export type ToolId = "compress-pdf" | "merge-pdf" | "split-pdf" | "jpg-to-pdf" | "pdf-to-jpg";
export type ToolState = "queued" | "processing" | "done" | "failed";

export interface ToolFixture {
  id: ToolId;
  hrefs: Record<Locale, string>;
  submitText: Record<Locale, string>;
  accept: string;
  maxFiles: number;
  fileKind: "pdf" | "jpg";
}

export const toolFixtures: Record<ToolId, ToolFixture> = {
  "compress-pdf": {
    id: "compress-pdf",
    hrefs: { en: "/en/compress-pdf", es: "/es/comprimir-pdf", id: "/id/kompres-pdf" },
    submitText: { en: "Compress", es: "Comprimir", id: "Kompres" },
    accept: "application/pdf",
    maxFiles: 1,
    fileKind: "pdf",
  },
  "merge-pdf": {
    id: "merge-pdf",
    hrefs: { en: "/en/merge-pdf", es: "/es/combinar-pdf", id: "/id/gabungkan-pdf" },
    submitText: { en: "Merge PDFs", es: "Unir PDF", id: "Gabung PDF" },
    accept: "application/pdf",
    maxFiles: 20,
    fileKind: "pdf",
  },
  "split-pdf": {
    id: "split-pdf",
    hrefs: { en: "/en/split-pdf", es: "/es/dividir-pdf", id: "/id/pisahkan-pdf" },
    submitText: { en: "Split PDF", es: "Dividir PDF", id: "Pisah PDF" },
    accept: "application/pdf",
    maxFiles: 1,
    fileKind: "pdf",
  },
  "jpg-to-pdf": {
    id: "jpg-to-pdf",
    hrefs: { en: "/en/jpg-to-pdf", es: "/es/jpg-a-pdf", id: "/id/gambar-ke-pdf" },
    submitText: { en: "Convert to PDF", es: "Convertir a PDF", id: "Konversi ke PDF" },
    accept: "image/jpeg",
    maxFiles: 50,
    fileKind: "jpg",
  },
  "pdf-to-jpg": {
    id: "pdf-to-jpg",
    hrefs: { en: "/en/pdf-to-jpg", es: "/es/pdf-a-jpg", id: "/id/pdf-ke-gambar" },
    submitText: { en: "Convert to JPG", es: "Convertir a JPG", id: "Konversi ke JPG" },
    accept: "application/pdf",
    maxFiles: 1,
    fileKind: "pdf",
  },
};

export const minimalPdf = Buffer.from(
  "%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n" +
    "2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n" +
    "3 0 obj\n<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>\nendobj\n" +
    "xref\n0 4\n0000000000 65535 f \ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF",
);

export const minimalJpg = Buffer.from([0xff, 0xd8, 0xff, 0xd9]);

export type StatusController = {
  readonly taskId: string;
  setState: (state: ToolState) => void;
  advance: () => ToolState;
  getState: () => ToolState;
};

export interface ServerFlowOptions {
  states?: ToolState[];
  initialState?: ToolState;
  outputCount?: number;
  downloadUrl?: string;
  taskId?: string;
  error?: { category: string; message_key: string; retryable: boolean };
  autoAdvance?: boolean;
}

function responseBody(
  tool: ToolFixture,
  taskId: string,
  state: ToolState,
  outputCount: number,
  error?: ServerFlowOptions["error"],
): string {
  return JSON.stringify({
    task_id: taskId,
    tool: tool.id,
    state,
    progress: { value: state === "done" ? 100 : 0, total: 100 },
    result: { output_count: outputCount, total_bytes: 2048 },
    ...(state === "failed" && error !== undefined ? { error } : {}),
  });
}

export async function submitToolFlow(
  page: Page,
  tool: ToolFixture,
  locale: Locale,
  files: Array<{ name: string; mimeType: string; buffer: Buffer }>,
): Promise<void> {
  const admission = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      response.url().includes(`/api/v1/tools/${tool.id}/tasks`),
  );
  await page.locator('input[type="file"]').setInputFiles(files);
  await page.getByRole("button", { name: tool.submitText[locale], exact: true }).click();
  const response = await admission;
  expect(response.status()).toBe(202);
  const body = (await response.json()) as { task_id?: unknown };
  expect(typeof body.task_id).toBe("string");
}

export async function interceptServerToolFlow(
  page: Page,
  tool: ToolFixture,
  options: ServerFlowOptions = {},
): Promise<StatusController> {
  const taskId = options.taskId ?? `task-${tool.id}-${Date.now()}`;
  const states = options.states ?? ["queued", "processing", "done"];
  let stateIndex = Math.max(0, states.indexOf(options.initialState ?? states[0]));
  let currentState = states[stateIndex] ?? "queued";
  const outputCount = options.outputCount ?? 1;
  const controller: StatusController = {
    taskId,
    setState: (next) => {
      currentState = next;
      stateIndex = Math.max(0, states.indexOf(next));
    },
    advance: () => {
      stateIndex = Math.min(stateIndex + 1, states.length - 1);
      currentState = states[stateIndex] ?? currentState;
      return currentState;
    },
    getState: () => currentState,
  };

  await page.route(`**/api/v1/tools/${tool.id}/tasks`, (route: Route) =>
    route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({ task_id: taskId }),
    }),
  );
  await page.route(`**/api/v1/tools/${tool.id}/tasks/*/status`, (route: Route) => {
    const body = responseBody(tool, taskId, currentState, outputCount, options.error);
    if (
      options.autoAdvance !== false &&
      states.length > 1 &&
      currentState !== "done" &&
      currentState !== "failed"
    ) {
      controller.advance();
    }
    return route.fulfill({ status: 200, contentType: "application/json", body });
  });
  await page.route(`**/api/v1/tools/${tool.id}/tasks/*/download/*`, (route: Route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ url: options.downloadUrl ?? "https://example.com/dl" }),
    }),
  );
  return controller;
}

export function fileForTool(
  tool: ToolFixture,
  index = 0,
): {
  name: string;
  mimeType: string;
  buffer: Buffer;
} {
  if (tool.fileKind === "jpg") {
    return { name: `input-${index + 1}.jpg`, mimeType: "image/jpeg", buffer: minimalJpg };
  }
  return { name: `input-${index + 1}.pdf`, mimeType: "application/pdf", buffer: minimalPdf };
}
