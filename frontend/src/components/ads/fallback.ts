/**
 * First-party house-promo fallback for the Adsterra slot (PT-02).
 *
 * When the provider invoke script errors, or no provider iframe appears
 * within `FALLBACK_TIMEOUT_MS` of injection, the reserved slot shows a
 * localized, clearly labeled Papyr promotion instead of staying empty.
 *
 * The fallback is fully first-party: an internal anchor to the localized
 * homepage, no analytics, no external requests, and no document metadata
 * mutation. It only ever runs client-side (the slot renders empty on SSR),
 * and only after ad injection was attempted — never when ads are disabled
 * (DNT/GPC/_papyrAdsDisabled) or on non-allowed pages, because the caller
 * only invokes it from the `AdSlot` effect that already applied those gates.
 */

import type { AdUnit } from "@/lib/ads";
import { LOCALE_COOKIE, defaultLocale, isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

/** How long to wait for an Adsterra iframe before showing the fallback. */
export const FALLBACK_TIMEOUT_MS = 5000;

/**
 * Returns the locale encoded in the first pathname segment, or `null` when
 * the path is not locale-prefixed (legacy paths, the bare root).
 */
export function localeFromPathname(pathname: string): Locale | null {
  const firstSegment = pathname.split("/")[1];
  if (firstSegment !== undefined && isLocale(firstSegment)) return firstSegment;
  return null;
}

function readCookie(name: string): string | null {
  for (const part of document.cookie.split(";")) {
    const entry = part.trim();
    if (entry.startsWith(`${name}=`)) {
      return decodeURIComponent(entry.slice(name.length + 1));
    }
  }
  return null;
}

/**
 * Resolves the active locale client-side: the locale-prefixed pathname wins
 * (canonical routing), then the `papyr_locale` preference cookie, then EN.
 * Never used during SSR (returns `defaultLocale` without touching `window`).
 */
export function resolveClientLocale(): Locale {
  if (typeof window === "undefined") return defaultLocale;
  // Tests may stub `window.location` to a bare `{ href }` object; treat a
  // missing `pathname` as "no locale on the path" instead of crashing.
  const pathname: string | undefined = window.location?.pathname;
  if (typeof pathname === "string") {
    const fromPath = localeFromPathname(pathname);
    if (fromPath !== null) return fromPath;
  }
  const fromCookie = readCookie(LOCALE_COOKIE);
  if (fromCookie !== null && isLocale(fromCookie)) return fromCookie;
  return defaultLocale;
}

/** True when the provider has injected its iframe into the slot. */
export function isSlotFilled(slotNode: HTMLElement): boolean {
  return slotNode.querySelector("iframe") !== null;
}

function createTextEl(className: string, text: string): HTMLSpanElement {
  const el = document.createElement("span");
  el.className = className;
  el.textContent = text;
  return el;
}

function createArrowIcon(): SVGSVGElement {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", "12");
  svg.setAttribute("height", "12");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "2");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  const chevron = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
  chevron.setAttribute("points", "6 9 12 15 18 9");
  svg.appendChild(chevron);
  return svg;
}

function createCta(label: string): HTMLSpanElement {
  const el = createTextEl(
    "inline-flex items-center gap-1 rounded-full bg-accent/10 px-3 py-1 text-xs font-semibold text-accent",
    label,
  );
  el.appendChild(createArrowIcon());
  return el;
}

/**
 * Renders the house-promo fallback into the reserved slot div, preserving
 * the slot's reserved dimensions and outer `data-testid="papyr-ad-slot"`.
 *
 * Two layouts share the reserved space: a vertical card for tall units
 * (e.g. 300x250, 160x600, 160x300) and a single-row banner for short units
 * (e.g. 728x90, 468x60, 320x50). The whole card is one accessible internal
 * anchor; the slot div's `aria-label` (localized "Advertisement") is left
 * untouched.
 */
export function showHouseFallback(slotNode: HTMLDivElement, locale: Locale, unit: AdUnit): void {
  if (slotNode.querySelector("[data-papyr-fallback='true']") !== null) return;

  const copy = getMessages(locale).ads.fallback;
  const anchor = document.createElement("a");
  anchor.href = `/${locale}`;
  anchor.dataset.papyrFallback = "true";
  anchor.className =
    "flex h-full w-full items-center justify-center overflow-hidden rounded-[10px] border border-slate-200 bg-white text-center transition-colors hover:border-accent/60";

  if (unit.height >= 120) {
    const stack = document.createElement("span");
    stack.className = "flex flex-col items-center justify-center gap-1.5 px-4 py-3";
    stack.append(
      createTextEl("text-[10px] font-semibold uppercase tracking-widest text-accent", copy.eyebrow),
      createTextEl("text-[15px] font-semibold leading-tight text-navy", copy.title),
      createTextEl("text-xs leading-snug text-slate-500", copy.body),
      createCta(copy.cta),
    );
    anchor.appendChild(stack);
  } else {
    const row = document.createElement("span");
    row.className = "flex items-center justify-center gap-2 px-3";
    row.append(
      createTextEl("text-[9px] font-semibold uppercase tracking-wider text-accent", copy.eyebrow),
      createTextEl("min-w-0 truncate text-[13px] font-semibold text-navy", copy.title),
      createArrowIcon(),
    );
    anchor.appendChild(row);
  }

  slotNode.appendChild(anchor);
}
