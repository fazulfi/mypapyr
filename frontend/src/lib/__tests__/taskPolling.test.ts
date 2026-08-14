import { afterEach, describe, expect, it, vi } from "vitest";

import {
  FALLBACK_CAPABILITIES,
  TaskPollingError,
  capabilitiesFor,
  fetchTaskStatus,
  type Capabilities,
  type CapabilitiesLike,
} from "../taskPolling";

function api(baseUrl = "", capabilities: Capabilities | null = null): CapabilitiesLike {
  return { baseUrl, capabilities };
}

function okJson(payload: Record<string, unknown>): Response {
  return {
    ok: true,
    status: 200,
    json: async () => payload,
  } as unknown as Response;
}

function badJsonResponse(status: number): Response {
  return { ok: false, status, json: async () => ({}) } as unknown as Response;
}

const FULL_PAYLOAD = {
  task_id: "t-1",
  tool: "compress-pdf",
  state: "processing",
  progress: { unit: "engine_progress", value: 50, total: 100 },
  expires_at: "2026-08-06T12:00:00Z",
};

describe("lib/taskPolling capabilitiesFor", () => {
  it("falls back to the client defaults when capabilities are absent", () => {
    expect(capabilitiesFor(api())).toBe(FALLBACK_CAPABILITIES);
  });

  it("returns the provided capabilities when present", () => {
    const caps: Capabilities = {
      maxRetries: 5,
      defaultTimeoutSeconds: 60,
      maxWaitSeconds: 300,
      retentionSeconds: 1800,
    };
    expect(capabilitiesFor(api("", caps))).toBe(caps);
  });
});

describe("lib/taskPolling fetchTaskStatus", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("maps a full snake_case backend response into a camelCase TaskStatus", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(okJson(FULL_PAYLOAD)));

    const status = await fetchTaskStatus(api("https://api.example.test"), "t-1", "compress-pdf");

    expect(status.taskId).toBe("t-1");
    expect(status.tool).toBe("compress-pdf");
    expect(status.state).toBe("processing");
    expect(status.progressValue).toBe(50);
    expect(status.progressTotal).toBe(100);
    expect(status.expiresAt).toBe("2026-08-06T12:00:00Z");
    expect(status.errorCategory).toBeNull();
    expect(status.messageKey).toBeNull();
    expect(status.retryable).toBe(false);
    expect(status.outputCount).toBeNull();
    expect(status.totalBytes).toBeNull();

    const fetchMock = vi.mocked(fetch);
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.example.test/api/v1/tools/compress-pdf/tasks/t-1/status",
    );
  });

  it("nulls absent optional fields and falls back the tool to the tool id", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(okJson({ task_id: "t-1", state: "unknown" })));

    const status = await fetchTaskStatus(api(), "t-1", "compress-pdf");

    expect(status.tool).toBe("compress-pdf");
    expect(status.progressValue).toBeNull();
    expect(status.progressTotal).toBeNull();
    expect(status.expiresAt).toBeNull();
    expect(status.errorCategory).toBeNull();
    expect(status.messageKey).toBeNull();
    expect(status.outputCount).toBeNull();
    expect(status.totalBytes).toBeNull();
    expect(status.retryable).toBe(false);
    expect(status.state).toBe("queued");
  });

  it("retries on network failure using the fallback maxRetries, then succeeds", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("network down"))
      .mockRejectedValueOnce(new TypeError("network down"))
      .mockResolvedValueOnce(
        okJson({
          task_id: "t-1",
          state: "failed",
          error: {
            code: "engine_error",
            category: "engine",
            retryable: true,
            message_key: "errors.engine",
          },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    const status = await fetchTaskStatus(api(), "t-1", "compress-pdf");

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(status.state).toBe("failed");
    expect(status.retryable).toBe(true);
    expect(status.errorCategory).toBe("engine");
    expect(status.messageKey).toBe("errors.engine");
    expect(status.outputCount).toBeNull();
  });

  it("throws TaskPollingError with retryable=false on non-2xx without retrying", async () => {
    const fetchMock = vi.fn().mockResolvedValue(badJsonResponse(500));
    vi.stubGlobal("fetch", fetchMock);

    const promise = fetchTaskStatus(api(), "t-1", "compress-pdf");
    await expect(promise).rejects.toBeInstanceOf(TaskPollingError);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    try {
      await fetchTaskStatus(api(), "t-1", "compress-pdf");
    } catch (error) {
      expect(error).toBeInstanceOf(TaskPollingError);
      expect((error as TaskPollingError).retryable).toBe(false);
    }
  });

  it("throws a non-retryable terminal TaskPollingError on 404", async () => {
    const fetchMock = vi.fn().mockResolvedValue(badJsonResponse(404));
    vi.stubGlobal("fetch", fetchMock);

    const promise = fetchTaskStatus(api(), "gone-task", "compress-pdf");
    await expect(promise).rejects.toBeInstanceOf(TaskPollingError);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    try {
      await fetchTaskStatus(api(), "gone-task", "compress-pdf");
    } catch (error) {
      expect(error).toBeInstanceOf(TaskPollingError);
      const pollingError = error as TaskPollingError;
      expect(pollingError.retryable).toBe(false);
      expect(pollingError.message).toContain("404");
    }
  });

  it("throws a retryable TaskPollingError after exhausting network retries", async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError("network down"));
    vi.stubGlobal("fetch", fetchMock);

    const promise = fetchTaskStatus(api(), "t-1", "compress-pdf", 1);
    await expect(promise).rejects.toBeInstanceOf(TaskPollingError);
    expect(fetchMock).toHaveBeenCalledTimes(2);

    try {
      await fetchTaskStatus(api(), "t-1", "compress-pdf", 1);
    } catch (error) {
      expect((error as TaskPollingError).retryable).toBe(true);
    }
  });
});
