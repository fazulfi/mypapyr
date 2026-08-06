import { describe, expect, it } from "vitest";

import { STATE_MESSAGE_KEY, type ToolState } from "../toolState";

const ALL_STATES: ToolState[] = [
  "idle",
  "preparing",
  "ready",
  "uploading",
  "queued",
  "processing",
  "finalizing",
  "done",
  "error",
];

describe("lib/toolState", () => {
  it("covers every tool state exactly once", () => {
    expect(Object.keys(STATE_MESSAGE_KEY).sort()).toEqual([...ALL_STATES].sort());
  });

  it("maps the five card states to states.* message keys", () => {
    expect(STATE_MESSAGE_KEY.queued).toBe("states.queued");
    expect(STATE_MESSAGE_KEY.preparing).toBe("states.preparing");
    expect(STATE_MESSAGE_KEY.processing).toBe("states.processing");
    expect(STATE_MESSAGE_KEY.done).toBe("states.done");
    expect(STATE_MESSAGE_KEY.error).toBe("states.error");
  });

  it("maps the transitional states to null", () => {
    expect(STATE_MESSAGE_KEY.idle).toBeNull();
    expect(STATE_MESSAGE_KEY.ready).toBeNull();
    expect(STATE_MESSAGE_KEY.uploading).toBeNull();
    expect(STATE_MESSAGE_KEY.finalizing).toBeNull();
  });
});
