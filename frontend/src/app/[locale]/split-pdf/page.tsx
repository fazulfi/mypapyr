"use client";

import { useRouter } from "next/navigation";
import React from "react";

import Dropzone from "@/components/uploader/Dropzone";
import DoneCard from "@/components/states/DoneCard";
import ErrorCard from "@/components/states/ErrorCard";
import PreparingCard from "@/components/states/PreparingCard";
import ProcessingCard from "@/components/states/ProcessingCard";
import QueuedCard from "@/components/states/QueuedCard";
import useTaskPolling from "@/hooks/useTaskPolling";
import { getMessages } from "@/lib/messages";
import { ToolId } from "@/lib/tool-ids";

type PageProps = { params?: Promise<{ locale: string }> };

export default async function CompressPdfPage({ params }: PageProps) {
  const messages = await getMessages(params?.locale || "en");

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <main className="container mx-auto p-4">
        <h1>{messages.tools.split.title}</h1>
        <p>{messages.tools.split.description}</p>
      </main>
    </div>
  );
}
