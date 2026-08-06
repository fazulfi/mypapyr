export type ToolState =
  | "idle"
  | "preparing"
  | "ready"
  | "uploading"
  | "queued"
  | "processing"
  | "finalizing"
  | "done"
  | "error";

/**
 * Maps every tool state to the message key rendered by its state card.
 * Transitional states (idle, ready, uploading, finalizing) carry no card
 * copy of their own; the five card states resolve to `states.*` keys.
 */
export const STATE_MESSAGE_KEY: Record<ToolState, string | null> = {
  idle: null,
  preparing: "states.preparing",
  ready: null,
  uploading: null,
  queued: "states.queued",
  processing: "states.processing",
  finalizing: null,
  done: "states.done",
  error: "states.error",
};
