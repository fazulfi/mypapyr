export const colors = {
  navy: "#1e3a5f",
  accent: "#2563eb",
  bg: "#f9fafb",
  foreground: "#171717",
} as const;

/**
 * Required supporting language per UX 10.1: Tailwind slate scale (fills
 * slate-100, borders slate-200, tertiary text slate-400/300, secondary text
 * slate-500), emerald-500 for success checks, and rose-50/rose-200/rose-500
 * for error states. Values mirror the installed Tailwind v4 default theme.
 */
export const supportColors = {
  "slate-100": "oklch(96.8% 0.007 247.896)",
  "slate-200": "oklch(92.9% 0.013 255.508)",
  "slate-300": "oklch(86.9% 0.022 252.894)",
  "slate-400": "oklch(70.4% 0.04 256.788)",
  "slate-500": "oklch(55.4% 0.046 257.417)",
  "emerald-500": "oklch(69.6% 0.17 162.48)",
  "rose-50": "oklch(96.9% 0.015 12.422)",
  "rose-200": "oklch(89.2% 0.058 10.001)",
  "rose-500": "oklch(64.5% 0.246 16.439)",
} as const;

export const spacing = {
  xs: "0.25rem",
  sm: "0.5rem",
  md: "0.75rem",
  lg: "1rem",
  xl: "1.5rem",
  "2xl": "2rem",
  "3xl": "3rem",
} as const;

export const fontFamily = {
  sans: 'var(--font-dm-sans), "DM Sans", system-ui, sans-serif',
  mono: 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace',
} as const;

export const designTokens = { colors, supportColors, spacing, fontFamily } as const;
