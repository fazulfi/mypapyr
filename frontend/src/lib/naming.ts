export type FileNamingScope = "source" | "zip" | "one-per-page";

const ILLEGAL_CHARS = /[\u0000-\u001f\u007f<>:"/\\|?*]/g;
const TRAILING_DOTS_OR_SPACES = /[. ]+$/;
export const MAX_FILENAME_LENGTH = 120;

function sanitize(original: string): string {
  const cleaned = original.replace(ILLEGAL_CHARS, "").replace(TRAILING_DOTS_OR_SPACES, "");
  const dotIndex = cleaned.lastIndexOf(".");
  const hasExtension = dotIndex > 0;
  const base = hasExtension ? cleaned.slice(0, dotIndex) : cleaned;
  const extension = hasExtension ? cleaned.slice(dotIndex) : "";

  if (base === "" && extension === "") {
    return "document";
  }

  const maxBase = Math.max(0, MAX_FILENAME_LENGTH - extension.length);
  const truncatedBase = base.slice(0, maxBase);
  if (truncatedBase === "" && extension !== "") {
    return `document${extension}`.slice(0, MAX_FILENAME_LENGTH);
  }
  return truncatedBase + extension;
}

export function safeFileName(original: string, scope: FileNamingScope): string {
  switch (scope) {
    case "source":
      return sanitize(original);
    case "zip":
      return sanitize(original);
    case "one-per-page":
      return sanitize(original);
  }
}

export function disambiguateName(name: string, used: ReadonlySet<string>): string {
  if (!used.has(name)) {
    return name;
  }
  const dotIndex = name.lastIndexOf(".");
  const hasExtension = dotIndex > 0;
  const base = hasExtension ? name.slice(0, dotIndex) : name;
  const extension = hasExtension ? name.slice(dotIndex) : "";
  let counter = 2;
  let candidate = hasExtension ? `${base} ${counter}${extension}` : `${name} ${counter}`;
  while (used.has(candidate)) {
    counter += 1;
    candidate = hasExtension ? `${base} ${counter}${extension}` : `${name} ${counter}`;
  }
  return candidate;
}
