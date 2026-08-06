export type TaskState = "queued" | "processing" | "done" | "failed";

export interface TaskStatus {
  taskId: string;
  tool: string;
  state: TaskState;
  progressValue: number | null;
  progressTotal: number | null;
  expiresAt: string | null;
  errorCategory: string | null;
  messageKey: string | null;
  retryable: boolean;
  outputCount: number | null;
  totalBytes: number | null;
}

export interface Capabilities {
  maxRetries: number;
  defaultTimeoutSeconds: number;
  maxWaitSeconds: number;
  retentionSeconds: number;
}

export const FALLBACK_CAPABILITIES: Capabilities = {
  maxRetries: 3,
  defaultTimeoutSeconds: 180,
  maxWaitSeconds: 900,
  retentionSeconds: 3600,
};

export interface CapabilitiesLike {
  baseUrl: string;
  capabilities: Capabilities | null;
}

export class TaskPollingError extends Error {
  readonly retryable: boolean;

  constructor(message: string, retryable: boolean) {
    super(message);
    this.name = "TaskPollingError";
    this.retryable = retryable;
  }
}

export function capabilitiesFor(api: CapabilitiesLike): Capabilities {
  return api.capabilities ?? FALLBACK_CAPABILITIES;
}

function parseState(value: unknown): TaskState {
  const raw = typeof value === "string" ? value : "";
  return raw === "queued" || raw === "processing" || raw === "done" || raw === "failed"
    ? raw
    : "queued";
}

function stringOrNull(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function numberOrNull(value: unknown): number | null {
  return typeof value === "number" ? value : null;
}

function recordOrNull(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null ? (value as Record<string, unknown>) : null;
}

export async function fetchTaskStatus(
  api: CapabilitiesLike,
  taskId: string,
  toolId: string,
  retries?: number,
): Promise<TaskStatus> {
  const maxRetries = retries ?? capabilitiesFor(api).maxRetries;
  const url = `${api.baseUrl}/api/v1/tools/${toolId}/tasks/${taskId}/status`;
  let lastError: unknown = null;

  for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new TaskPollingError(
          `Task status request failed with HTTP ${response.status}`,
          false,
        );
      }
      const json: Record<string, unknown> = await response.json();
      const progress = recordOrNull(json.progress);
      const result = recordOrNull(json.result);
      const error = recordOrNull(json.error);
      return {
        taskId: String(json.task_id ?? ""),
        tool: String(json.tool ?? toolId),
        state: parseState(json.state),
        progressValue: numberOrNull(progress?.value),
        progressTotal: numberOrNull(progress?.total),
        expiresAt: stringOrNull(json.expires_at),
        errorCategory: stringOrNull(error?.category),
        messageKey: stringOrNull(error?.message_key),
        retryable: error?.retryable === true,
        outputCount: numberOrNull(result?.output_count),
        totalBytes: numberOrNull(result?.total_bytes),
      };
    } catch (error) {
      if (error instanceof TaskPollingError) {
        throw error;
      }
      lastError = error;
    }
  }

  throw new TaskPollingError(
    `Task status request failed after ${maxRetries + 1} attempt(s): ${String(lastError)}`,
    true,
  );
}
