import type { Locale } from "../lib/i18n";

function FileIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="white"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M14.5 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

interface LogoLockupProps {
  size?: "navbar" | "footer";
  href?: string;
  locale?: Locale;
}

export function LogoLockup({ size = "navbar", href, locale }: LogoLockupProps): React.ReactElement {
  const resolvedHref = href ?? (locale ? `/${locale}` : "/");

  const isNavbar = size === "navbar";

  const markSize = isNavbar ? "h-7 w-7" : "h-6 w-6";
  const markRadius = isNavbar ? "rounded-md" : "rounded-[5px]";
  const textSize = isNavbar ? "text-[17px]" : "text-[15px]";
  const tracking = isNavbar ? "tracking-tight" : "";

  return (
    <a href={resolvedHref} aria-label="Papyr" className="flex shrink-0 items-center gap-2">
      <div className={`flex items-center justify-center bg-navy ${markSize} ${markRadius}`}>
        <FileIcon />
      </div>
      <span className={`font-semibold text-navy ${textSize} ${tracking}`}>Papyr</span>
    </a>
  );
}
