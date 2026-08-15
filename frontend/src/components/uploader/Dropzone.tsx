"use client";

import { useRef, useState, type ChangeEvent, type DragEvent } from "react";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

function UploadIcon(): React.ReactElement {
  return (
    <svg
      width="26"
      height="26"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

export interface DropzoneProps {
  files: File[];
  onChange: (files: File[]) => void;
  disabled?: boolean;
  accept?: string[];
  maxFiles?: number;
  maxSizeBytes?: number;
  locale: Locale;
}

function passesFilters(
  file: File,
  accept: string[] | undefined,
  maxSizeBytes: number | undefined,
): boolean {
  if (accept !== undefined && accept.length > 0 && !accept.includes(file.type)) {
    return false;
  }
  if (maxSizeBytes !== undefined && file.size > maxSizeBytes) {
    return false;
  }
  return true;
}

export function Dropzone({
  files,
  onChange,
  disabled = false,
  accept,
  maxFiles,
  maxSizeBytes,
  locale,
}: DropzoneProps): React.ReactElement {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const copy = getMessages(locale);

  const filterFiles = (incoming: File[]): File[] => {
    const filtered = incoming.filter((file) => passesFilters(file, accept, maxSizeBytes));
    return maxFiles === undefined ? filtered : filtered.slice(0, maxFiles);
  };

  const openPicker = (): void => {
    if (disabled) {
      return;
    }
    inputRef.current?.click();
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement>): void => {
    const incoming = Array.from(event.target.files ?? []);
    onChange(filterFiles(incoming));
    event.target.value = "";
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    if (!disabled) {
      setDragging(true);
    }
  };

  const handleDragLeave = (): void => {
    setDragging(false);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    setDragging(false);
    if (disabled) {
      return;
    }
    onChange(filterFiles(Array.from(event.dataTransfer.files)));
  };
  return (
    <div
      data-testid="dropzone"
      role="button"
      tabIndex={0}
      onClick={openPicker}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          openPicker();
        }
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={
        "cursor-pointer rounded-2xl border-2 border-dashed bg-white px-5 py-14 text-center transition-all " +
        (dragging ? "border-accent bg-accent/5" : "border-slate-300 hover:border-accent/50")
      }
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        className="hidden"
        accept={accept === undefined ? undefined : accept.join(",")}
        aria-label={copy.uploader.browse}
        disabled={disabled}
        onChange={handleChange}
      />
      <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-xl bg-accent/10 text-accent">
        <UploadIcon />
      </div>
      <p className="mb-2 text-base font-semibold tracking-tight text-navy">
        {copy.uploader.drop}
        <br />
        {copy.uploader.browseCta}
      </p>
      {maxSizeBytes !== undefined && (
        <p className="text-xs text-slate-400">
          {copy.uploader.dropHint.replace(
            "{size}",
            String(Math.round(maxSizeBytes / (1024 * 1024))),
          )}
        </p>
      )}
      {files.length > 0 && (
        <p className="mt-2 text-xs text-slate-500" data-testid="file-count">
          {files.length} file{files.length === 1 ? "" : "s"} selected
        </p>
      )}
    </div>
  );
}
