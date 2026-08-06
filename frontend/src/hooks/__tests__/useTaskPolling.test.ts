// @vitest-environment jsdom
import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useTaskPolling } from "../useTaskPolling";

const TOOL_ID = "compress-pdf";
const TASK_ID = "t-1";
const KEY = "papyr:task:" + TOOL_ID;

function payload(status: string): Record<string, unknown> {
  const body: Record<string, unknown> = {
    task_id: TASK_ID,
    tool: TOOL_ID,
    state: status,
    progress: { unit: "engine_progress", value: 50, total: 100 },
    expires_at: null,
  };
  if (status === "done") {
    body.result = { output_count: 1, total_bytes: 1024 };
  }
  if (status === "failed") {
    body.error = {
      code: "engine_error",
      category: "engine",
      retryable: false,
      message_key: "errors.engine",
    };
  }
  return body;
}

function okJson(body: Record<string, unknown>): Response {
  return { ok: true, status: 200, json: async () => body } as unknown as Response;
}

async function advance(ms: number): Promise<void> {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}

async function flushMicrotasks(): Promise<void> {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(0);
  });
}

describe("hooks/useTaskPolling", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    window.sessionStorage.clear();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("polls every 2000ms while enabled with a task id", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("processing")));
    vi.stubGlobal("fetch", fetchMock);

    renderHook(() => useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }));
    await flushMicrotasks();
    expect(fetchMock).not.toHaveBeenCalled();

    await advance(2000);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await advance(2000);
    expect(fetchMock).toHaveBeenCalledTimes(2);

    await advance(2000);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("writes the resume token on successful fetch", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("processing")));
    vi.stubGlobal("fetch", fetchMock);

    renderHook(() => useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }));
    await advance(2000);

    expect(window.sessionStorage.getItem(KEY)).toBe(TASK_ID);
  });

  it("stops polling once the task is done", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("done")));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() =>
      useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }),
    );
    await advance(2000);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(result.current.status?.state).toBe("done");

    await advance(4000);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("stops polling once the task failed", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("failed")));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() =>
      useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }),
    );
    await advance(2000);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(result.current.status?.state).toBe("failed");

    await advance(4000);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("stop() removes the sessionStorage token and halts polling", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("processing")));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() =>
      useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }),
    );
    await advance(2000);
    expect(window.sessionStorage.getItem(KEY)).toBe(TASK_ID);

    act(() => {
      result.current.stop();
    });
    expect(window.sessionStorage.getItem(KEY)).toBeNull();

    await advance(4000);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("resumes immediately on mount when the stored token matches the task id", async () => {
    window.sessionStorage.setItem(KEY, TASK_ID);
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("processing")));
    vi.stubGlobal("fetch", fetchMock);

    renderHook(() => useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }));
    await flushMicrotasks();

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("does not resume on mount when the stored token differs from the task id", async () => {
    window.sessionStorage.setItem(KEY, "some-other-task");
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("processing")));
    vi.stubGlobal("fetch", fetchMock);

    renderHook(() => useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }));
    await flushMicrotasks();
    expect(fetchMock).not.toHaveBeenCalled();

    await advance(2000);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("never fetches while disabled", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("processing")));
    vi.stubGlobal("fetch", fetchMock);

    renderHook(() => useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: false }));
    await flushMicrotasks();

    await advance(6000);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("refresh() fetches on demand and reports the latest status", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okJson(payload("done")));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() =>
      useTaskPolling({ toolId: TOOL_ID, taskId: TASK_ID, enabled: true }),
    );
    await flushMicrotasks();
    expect(result.current.status).toBeNull();

    await act(async () => {
      await result.current.refresh();
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(result.current.status?.state).toBe("done");
  });
});
