"use client";

import { useRef, useState, type ChangeEvent, type DragEvent } from "react";

import type { Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";

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
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={
        "flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors " +
        (dragging
          ? "border-accent bg-accent/5"
          : "border-slate-300 bg-slate-50 hover:border-accent")
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
      <p className="mb-4 text-sm text-slate-600">
        {copy.uploader.drop}{" "}
        <button
          type="button"
          onClick={openPicker}
          disabled={disabled}
          className="font-medium text-accent underline-offset-2 hover:underline disabled:cursor-not-allowed"
        >
          {copy.uploader.browse}
        </button>
      </p>
      {files.length > 0 && (
        <p className="text-xs text-slate-500" data-testid="file-count">
          {files.length} file{files.length === 1 ? "" : "s"} selected
        </p>
      )}
    </div>
  );
}
