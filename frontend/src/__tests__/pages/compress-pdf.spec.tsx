// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CompressPdfTool } from "@/app/[locale]/compress-pdf/page";

vi.mock("@/hooks/useTaskPolling", () => ({
  useTaskPolling: () => ({ status: null, refresh: vi.fn(), stop: vi.fn() }),
}));

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("CompressPdfTool", () => {
  it("renders the compress title in English", () => {
    render(<CompressPdfTool locale="en" />);
    expect(screen.getByText("Compress PDF")).toBeTruthy();
    expect(screen.getByTestId("dropzone")).toBeTruthy();
  });

  it("has a Compress button", () => {
    render(<CompressPdfTool locale="en" />);
    expect(screen.getByRole("button", { name: "Compress" })).toBeTruthy();
  });
});
