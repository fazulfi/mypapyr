"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import type { ToolId } from "../lib/tool-ids";
import { fetchTaskStatus, type TaskStatus } from "../lib/taskPolling";

const POLL_INTERVAL_MS = 2000;
const TOKEN_PREFIX = "papyr:task:";

function tokenKey(toolId: string): string {
  return `${TOKEN_PREFIX}${toolId}`;
}

function readToken(toolId: string): string | null {
  try {
    return window.sessionStorage.getItem(tokenKey(toolId));
  } catch {
    return null;
  }
}

function writeToken(toolId: string, taskId: string): void {
  try {
    window.sessionStorage.setItem(tokenKey(toolId), taskId);
  } catch {
    // sessionStorage can be unavailable (e.g. privacy modes); polling must continue.
  }
}

function clearToken(toolId: string): void {
  try {
    window.sessionStorage.removeItem(tokenKey(toolId));
  } catch {
    // Ignore storage errors on stop; nothing else to clean up.
  }
}

export type UseTaskPollingOptions = {
  toolId: ToolId;
  taskId: string;
  enabled: boolean;
};

export function useTaskPolling({ toolId, taskId, enabled }: UseTaskPollingOptions): {
  status: TaskStatus | null;
  refresh(): void;
  stop(): void;
} {
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const activeRef = useRef(false);

  const stop = useCallback(() => {
    activeRef.current = false;
    clearToken(toolId);
  }, [toolId]);

  const refresh = useCallback(async () => {
    try {
      const next = await fetchTaskStatus({ baseUrl: "", capabilities: null }, taskId, toolId);
      setStatus(next);
      writeToken(toolId, taskId);
      if (next.state === "done" || next.state === "failed") {
        stop();
      }
    } catch {
      // Transient polling error: leave the last status and keep polling.
    }
  }, [taskId, toolId, stop]);

  useEffect(() => {
    if (!enabled) {
      return undefined;
    }
    activeRef.current = true;
    if (readToken(toolId) === taskId) {
      queueMicrotask(() => {
        if (activeRef.current) {
          void refresh();
        }
      });
    }
    const interval = window.setInterval(() => {
      if (!activeRef.current) {
        return;
      }
      void refresh();
    }, POLL_INTERVAL_MS);
    return () => {
      activeRef.current = false;
      window.clearInterval(interval);
    };
  }, [enabled, taskId, toolId, refresh]);

  return { status, refresh, stop };
}
