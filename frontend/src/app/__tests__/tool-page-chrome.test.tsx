// @vitest-environment jsdom
import type { ReactNode } from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { Locale } from "@/lib/i18n";
import { locales } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

import { CompressPdfTool } from "../[locale]/compress-pdf/page";
import { MergePdfTool } from "../[locale]/merge-pdf/page";
import { SplitPdfTool } from "../[locale]/split-pdf/page";
import { JpgToPdfTool } from "../[locale]/jpg-to-pdf/page";
import { PdfToJpgTool } from "../[locale]/pdf-to-jpg/page";

type ToolId = "compress-pdf" | "merge-pdf" | "split-pdf" | "jpg-to-pdf" | "pdf-to-jpg";

const TOOL_IDS: readonly ToolId[] = [
  "compress-pdf",
  "merge-pdf",
  "split-pdf",
  "jpg-to-pdf",
  "pdf-to-jpg",
];

// Maps tool-page ids to their `tools.*` message key.
const TOOLS_KEY: Record<ToolId, keyof ReturnType<typeof getMessages>["tools"]> = {
  "compress-pdf": "compress",
  "merge-pdf": "merge",
  "split-pdf": "split",
  "jpg-to-pdf": "jpgToPdf",
  "pdf-to-jpg": "pdfToJpg",
};

const TOOL_COMPONENTS: Record<ToolId, (props: { locale: Locale }) => ReactNode> = {
  "compress-pdf": CompressPdfTool,
  "merge-pdf": MergePdfTool,
  "split-pdf": SplitPdfTool,
  "jpg-to-pdf": JpgToPdfTool,
  "pdf-to-jpg": PdfToJpgTool,
};

const MODEL_BY_TOOL: Record<ToolId, "server" | "client" | "hybrid"> = {
  "compress-pdf": "server",
  "merge-pdf": "client",
  "split-pdf": "client",
  "jpg-to-pdf": "hybrid",
  "pdf-to-jpg": "server",
};

let fetchMock = vi.fn();

function makeResponse(status: number, body?: unknown) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body ?? {},
  };
}

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

describe("T5 tool page chrome (icon chip header + feature badges + PrivacyNotice)", () => {
  it("defines toolPages.features and privacyNotice keys in every locale", () => {
    for (const locale of locales) {
      const copy = getMessages(locale);
      expect(copy.privacyNotice.model.server.trim()).not.toBe("");
      expect(copy.privacyNotice.model.client.trim()).not.toBe("");
      expect(copy.privacyNotice.model.hybrid.trim()).not.toBe("");
      for (const toolId of TOOL_IDS) {
        const features = copy.toolPages[toolId].features;
        expect(features).toHaveLength(3);
        for (const feature of features) {
          expect(feature.trim()).not.toBe("");
        }
      }
    }
  });

  it("localizes privacyNotice copy and tool feature badges per locale", () => {
    for (const model of ["server", "client", "hybrid"] as const) {
      const en = getMessages("en").privacyNotice.model[model];
      expect(getMessages("es").privacyNotice.model[model]).not.toBe(en);
      expect(getMessages("id").privacyNotice.model[model]).not.toBe(en);
    }
    for (const toolId of TOOL_IDS) {
      for (let i = 0; i < 3; i++) {
        const en = getMessages("en").toolPages[toolId].features[i];
        expect(getMessages("es").toolPages[toolId].features[i]).not.toBe(en);
        expect(getMessages("id").toolPages[toolId].features[i]).not.toBe(en);
      }
    }
  });

  it.each(TOOL_IDS)(
    "renders icon chip, h1, three feature badges, and PrivacyNotice on %s",
    (toolId) => {
      const locale = "en";
      const copy = getMessages(locale);
      const ToolComponent = TOOL_COMPONENTS[toolId];
      const { container } = render(<ToolComponent locale={locale} />);

      // Icon chip: h-16 w-16 rounded-2xl bg-accent/10 with the tool icon inside.
      const chip = container.querySelector(".rounded-2xl.bg-accent\\/10");
      expect(chip).not.toBeNull();
      expect(chip?.className).toContain("h-16");
      expect(chip?.className).toContain("w-16");
      expect(chip?.querySelector("svg")).not.toBeNull();

      // Page heading renders the localized tool title.
      const heading = screen.getByRole("heading", { level: 1 });
      expect(heading.textContent).toContain(copy.tools[TOOLS_KEY[toolId]].title);

      // Three feature badges, each with an icon and the localized feature label.
      const badges = container.querySelectorAll(".rounded-full.bg-accent\\/10");
      expect(badges).toHaveLength(3);
      const badgeTexts = Array.from(badges).map((badge) => badge.textContent ?? "");
      for (const feature of copy.toolPages[toolId].features) {
        expect(badgeTexts.some((text) => text.includes(feature))).toBe(true);
      }
      for (const badge of badges) {
        expect(badge.querySelector("svg")).not.toBeNull();
      }

      // PrivacyNotice renders the localized copy for the tool's processing model.
      const notice = container.querySelector(".border-slate-100");
      expect(notice).not.toBeNull();
      expect(notice?.textContent).toContain(copy.privacyNotice.model[MODEL_BY_TOOL[toolId]]);
      // The dropzone still renders below the chrome (existing tool-page tests
      // assert its behavior; Task 6 restyles it).
      expect(container.querySelector('[data-testid="dropzone"]')).not.toBeNull();
    },
  );

  it("renders the tool page chrome above the dropzone on every tool", () => {
    for (const toolId of TOOL_IDS) {
      cleanup();
      const ToolComponent = TOOL_COMPONENTS[toolId];
      const { container } = render(<ToolComponent locale="en" />);
      const chip = container.querySelector(".rounded-2xl.bg-accent\\/10");
      const badge = container.querySelector(".rounded-full.bg-accent\\/10");
      const dropzone = container.querySelector('[data-testid="dropzone"]');

      // All chrome elements must be present.
      expect(chip).not.toBeNull();
      expect(badge).not.toBeNull();
      expect(dropzone).not.toBeNull();
    }
  });
});