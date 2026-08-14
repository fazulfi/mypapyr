// @vitest-environment jsdom

import { act } from "react";
import { createRoot } from "react-dom/client";
import { describe, expect, it, vi, afterEach } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: vi.fn(() => "/en/compress-pdf"),
}));

import { Navbar } from "../Navbar";

let activeRoot: ReturnType<typeof createRoot> | null = null;

function render(jsx: React.ReactElement): HTMLElement {
  const container = document.createElement("div");
  document.body.appendChild(container);
  const root = createRoot(container);
  activeRoot = root;
  act(() => {
    root.render(jsx);
  });
  return container;
}

function fireClick(el: Element): void {
  act(() => {
    el.dispatchEvent(new MouseEvent("click", { bubbles: true }));
  });
}

function fireKeydown(key: string): void {
  act(() => {
    document.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true }));
  });
}

function fireMousedown(el: Element): void {
  act(() => {
    el.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
  });
}

describe("SH-05 Navbar — DOM interaction", () => {
  let container: HTMLElement;

  afterEach(() => {
    if (activeRoot) {
      act(() => {
        activeRoot!.unmount();
      });
      activeRoot = null;
    }
    document.body.innerHTML = "";
  });

  describe("mobile toggle", () => {
    it("hamburger toggles mobile menu open and closed", () => {
      container = render(<Navbar locale="en" />);

      const toggle = container.querySelector('button[aria-label*="navigation" i]') as HTMLButtonElement;
      expect(toggle).toBeTruthy();
      expect(toggle.getAttribute("aria-expanded")).toBe("false");

      fireClick(toggle);
      expect(toggle.getAttribute("aria-expanded")).toBe("true");

      fireClick(toggle);
      expect(toggle.getAttribute("aria-expanded")).toBe("false");
    });
  });

  describe("desktop category dropdown", () => {
    it("clicking a category button expands its menu", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      ) as HTMLButtonElement;
      expect(basicBtn).toBeTruthy();
      expect(basicBtn.getAttribute("aria-expanded")).toBe("false");

      fireClick(basicBtn);
      expect(basicBtn.getAttribute("aria-expanded")).toBe("true");
    });
  });

  describe("keyboard Escape", () => {
    it("pressing Escape closes any open category dropdown", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      ) as HTMLButtonElement;
      fireClick(basicBtn);
      expect(basicBtn.getAttribute("aria-expanded")).toBe("true");

      fireKeydown("Escape");
      expect(basicBtn.getAttribute("aria-expanded")).toBe("false");
    });
  });

  describe("click outside", () => {
    it("clicking outside closes an open dropdown", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      ) as HTMLButtonElement;
      fireClick(basicBtn);
      expect(basicBtn.getAttribute("aria-expanded")).toBe("true");

      const outside = document.createElement("div");
      document.body.appendChild(outside);
      fireMousedown(outside);
      expect(basicBtn.getAttribute("aria-expanded")).toBe("false");
    });
  });

  describe("navigation link close behavior", () => {
    it("closes desktop dropdown when a tool link is clicked", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      ) as HTMLButtonElement;
      fireClick(basicBtn);
      expect(basicBtn.getAttribute("aria-expanded")).toBe("true");

      const link = container.querySelector('a[href*="compress-pdf"]') as HTMLAnchorElement;
      expect(link).toBeTruthy();
      fireClick(link);

      expect(basicBtn.getAttribute("aria-expanded")).toBe("false");
    });
  });

  describe("equivalent locale path", () => {
    it("LanguageSwitcher renders a <select> with one <option> per locale", () => {
      container = render(<Navbar locale="en" />);

      const select = container.querySelector("select");
      expect(select).toBeTruthy();

      const options = Array.from(select!.querySelectorAll("option"));
      const values = options.map((o) => o.getAttribute("value"));
      expect(values).toEqual(["en", "es", "id"]);
    });

    it("LanguageSwitcher marks the current locale as selected", () => {
      container = render(<Navbar locale="es" />);

      const select = container.querySelector("select") as HTMLSelectElement;
      expect(select).toBeTruthy();
      expect(select.value).toBe("es");
    });

    it("active tool link gets accent styling in dropdown", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      );

      fireClick(basicBtn!);

      const activeLink = container.querySelector('[class*="bg-accent/10"]');
      expect(activeLink).toBeTruthy();
      expect(activeLink!.textContent).toContain("Compress PDF");
    });
  });
});
