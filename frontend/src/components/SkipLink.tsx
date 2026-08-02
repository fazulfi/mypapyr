interface SkipLinkProps {
  href?: string;
  label: string;
}

export function SkipLink({ href = "#main-content", label }: SkipLinkProps): React.ReactElement {
  return (
    <a
      href={href}
      className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:bg-[var(--color-accent)] focus:px-4 focus:py-2 focus:text-[var(--color-bg)]"
    >
      {label}
    </a>
  );
}
