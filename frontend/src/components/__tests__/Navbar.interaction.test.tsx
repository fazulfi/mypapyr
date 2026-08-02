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
    const event = new MouseEvent("click", { bubbles: true, cancelable: true });
    // jsdom does not implement anchor navigation; prevent the default so the
    // interaction still exercises the component state change without emitting
    // "Not implemented: navigation to another Document" warnings.
    if (el instanceof HTMLAnchorElement) {
      event.preventDefault();
    }
    el.dispatchEvent(event);
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
    if (container && container.parentNode) {
      act(() => {
        container.parentNode!.removeChild(container);
      });
    }
  });

  describe("mobile toggle", () => {
    it("opens mobile menu on hamburger click and shows navClose label", () => {
      container = render(<Navbar locale="en" />);
      const hamburger = container.querySelector('button[aria-label="Open navigation"]');
      expect(hamburger).toBeTruthy();

      const mobMenuBefore = container.querySelector(".border-t.border-slate-200");
      expect(mobMenuBefore).toBeNull();

      fireClick(hamburger!);

      const mobMenuAfter = container.querySelector(".border-t.border-slate-200");
      expect(mobMenuAfter).toBeTruthy();

      const closeLabel = container.querySelector('button[aria-label="Close navigation"]');
      expect(closeLabel).toBeTruthy();
    });

    it("toggles aria-expanded on hamburger when opening and closing", () => {
      container = render(<Navbar locale="en" />);
      const hamburger = container.querySelector('button[aria-expanded="false"]');
      expect(hamburger).toBeTruthy();

      fireClick(hamburger!);

      const expandedBtn = container.querySelector('button[aria-expanded="true"]');
      expect(expandedBtn).toBeTruthy();

      fireClick(hamburger!);

      const collapsedBtn = container.querySelector('button[aria-expanded="false"]');
      expect(collapsedBtn).toBeTruthy();
      const mobMenuClosed = container.querySelector(".border-t.border-slate-200");
      expect(mobMenuClosed).toBeNull();
    });
  });

  describe("desktop category dropdown", () => {
    it("opens dropdown on click and shows tool links", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      );

      expect(basicBtn).toBeTruthy();
      expect(basicBtn!.getAttribute("aria-expanded")).toBe("false");

      fireClick(basicBtn!);

      expect(basicBtn!.getAttribute("aria-expanded")).toBe("true");

      const dropdown = container.querySelector('[id^="nav-dropdown-"]');
      expect(dropdown).toBeTruthy();
      expect(dropdown!.textContent).toContain("Compress PDF");
      expect(dropdown!.textContent).toContain("Merge PDF");
      expect(dropdown!.textContent).toContain("Split PDF");
    });

    it("closes dropdown on second click (toggle)", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      );

      fireClick(basicBtn!);
      expect(basicBtn!.getAttribute("aria-expanded")).toBe("true");

      fireClick(basicBtn!);
      expect(basicBtn!.getAttribute("aria-expanded")).toBe("false");

      const dropdown = container.querySelector('[id^="nav-dropdown-"]');
      expect(dropdown).toBeNull();
    });
  });

  describe("keyboard Escape", () => {
    it("closes open dropdown on Escape key", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      );

      fireClick(basicBtn!);
      expect(basicBtn!.getAttribute("aria-expanded")).toBe("true");

      fireKeydown("Escape");

      expect(basicBtn!.getAttribute("aria-expanded")).toBe("false");
      const dropdown = container.querySelector('[id^="nav-dropdown-"]');
      expect(dropdown).toBeNull();
    });

    it("closes mobile menu on Escape key", () => {
      container = render(<Navbar locale="en" />);
      const hamburger = container.querySelector('button[aria-label="Open navigation"]');
      fireClick(hamburger!);

      const mobMenu = container.querySelector(".border-t.border-slate-200");
      expect(mobMenu).toBeTruthy();

      fireKeydown("Escape");

      const mobMenuClosed = container.querySelector(".border-t.border-slate-200");
      expect(mobMenuClosed).toBeNull();
    });
  });

  describe("click outside", () => {
    it("closes open dropdown when clicking outside", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      );

      fireClick(basicBtn!);
      expect(basicBtn!.getAttribute("aria-expanded")).toBe("true");

      const outsideDiv = document.createElement("div");
      document.body.appendChild(outsideDiv);
      fireMousedown(outsideDiv);
      document.body.removeChild(outsideDiv);

      expect(basicBtn!.getAttribute("aria-expanded")).toBe("false");
    });
  });

  describe("navigation link close behavior", () => {
    it("closes mobile menu when a tool link is clicked", () => {
      container = render(<Navbar locale="en" />);
      const hamburger = container.querySelector('button[aria-label="Open navigation"]');
      fireClick(hamburger!);

      const mobMenu = container.querySelector(".border-t.border-slate-200");
      expect(mobMenu).toBeTruthy();

      const firstToolLink = mobMenu!.querySelector("a");
      expect(firstToolLink).toBeTruthy();
      fireClick(firstToolLink!);

      const mobMenuClosed = container.querySelector(".border-t.border-slate-200");
      expect(mobMenuClosed).toBeNull();
    });

    it("closes desktop dropdown when a tool link is clicked", () => {
      container = render(<Navbar locale="en" />);

      const basicBtn = Array.from(container.querySelectorAll("button[aria-expanded]")).find((btn) =>
        btn.textContent?.includes("Basic"),
      );

      fireClick(basicBtn!);
      const dropdown = container.querySelector('[id^="nav-dropdown-"]');
      expect(dropdown).toBeTruthy();

      const firstLink = dropdown!.querySelector("a");
      expect(firstLink).toBeTruthy();
      fireClick(firstLink!);

      expect(basicBtn!.getAttribute("aria-expanded")).toBe("false");
    });
  });

  describe("equivalent locale path", () => {
    it("LanguageSwitcher links have correct locale-prefixed hrefs", () => {
      container = render(<Navbar locale="en" />);

      const langLinks = container.querySelectorAll("a[lang]");
      const hrefs = Array.from(langLinks).map((a) => a.getAttribute("href"));
      expect(hrefs).toContain("/en/compress-pdf");
      expect(hrefs).toContain("/es/comprimir-pdf");
      expect(hrefs).toContain("/id/kompres-pdf");
    });

    it("LanguageSwitcher marks current locale with aria-current", () => {
      container = render(<Navbar locale="es" />);

      const currentLink = container.querySelector('a[aria-current="page"]');
      expect(currentLink).toBeTruthy();
      expect(currentLink!.textContent).toBe("Español");
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
