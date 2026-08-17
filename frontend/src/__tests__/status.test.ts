// @vitest-environment node
/**
 * OP-02 status derivation (pure module tests).
 *
 * The derivation contract (P7 plan Task 2):
 * - one-region transient failure remains operational;
 * - sustained failures in at least two regions cross the configured
 *   consecutive-failure threshold and read down;
 * - a healthy observation resets a region's streak (recovery clears
 *   degraded/down);
 * - unknown/insufficient observations remain explicitly unknown;
 * - inputs and outputs carry only aggregate operational fields (no
 *   filenames, keys, URLs, or document metadata);
 * - the module is pure: no fetch, no I/O, no VPS dependency.
 */
import { describe, expect, it } from "vitest";

import {
  DEFAULT_THRESHOLDS,
  deriveStatus,
  type RegionObservation,
  type StatusSnapshot,
  type StatusThresholds,
} from "@/lib/status";

const T: StatusThresholds = { consecutiveFailures: 3, downRegions: 2 };

function snapshot(
  observedAt: number,
  regions: ReadonlyArray<readonly [string, boolean]>,
): StatusSnapshot {
  const observations: RegionObservation[] = regions.map(([region, reachable]) => ({
    region,
    reachable,
  }));
  return { observedAt, regions: observations };
}

/** A window of consecutive healthy rounds starting at `start` (ms). */
function healthyWindow(regionIds: readonly string[], rounds = 3, start = 1_000): StatusSnapshot[] {
  return Array.from({ length: rounds }, (_, i) =>
    snapshot(
      start + i * 1_000,
      regionIds.map((region) => [region, true] as const),
    ),
  );
}

/** Marks the last `count` rounds of `regionId` unreachable in the window. */
function failLastRounds(
  window: StatusSnapshot[],
  regionId: string,
  count: number,
): StatusSnapshot[] {
  return window.map((s, i) => {
    const failing = i >= window.length - count;
    return snapshot(
      s.observedAt,
      s.regions.map((r) => [r.region, r.region === regionId ? !failing : r.reachable] as const),
    );
  });
}

describe("OP-02 deriveStatus: thresholds contract", () => {
  it("defaults to 3 consecutive failures and 2 regions (owner default, R-12 gate)", () => {
    expect(DEFAULT_THRESHOLDS).toEqual({ consecutiveFailures: 3, downRegions: 2 });
  });

  it("rejects a non-integer or below-one consecutive-failure threshold", () => {
    for (const consecutiveFailures of [0, -1, 1.5]) {
      expect(() => deriveStatus([], { consecutiveFailures, downRegions: 2 })).toThrow(RangeError);
    }
  });

  it("rejects fewer than two regions for the down determination", () => {
    for (const downRegions of [0, 1]) {
      expect(() => deriveStatus([], { consecutiveFailures: 3, downRegions })).toThrow(RangeError);
    }
  });

  it("rejects a non-integer downRegions threshold", () => {
    for (const downRegions of [1.5, 2.5]) {
      expect(() => deriveStatus([], { consecutiveFailures: 3, downRegions })).toThrow(RangeError);
    }
  });
});

describe("OP-02 deriveStatus: transient one-region failure resilience", () => {
  it("keeps the service operational while a single region fails below the threshold", () => {
    const window = failLastRounds(healthyWindow(["eu", "us"], 5, 1_000), "eu", 2);
    const derived = deriveStatus(window, T);

    expect(derived.state).toBe("operational");
    expect(derived.sufficient).toBe(true);
    expect(derived.regions.find((r) => r.region === "eu")).toEqual({
      region: "eu",
      level: "degraded",
      consecutiveFailures: 2,
    });
    expect(derived.regions.find((r) => r.region === "us")).toEqual({
      region: "us",
      level: "operational",
      consecutiveFailures: 0,
    });
  });

  it("treats an isolated failure followed by health as a broken streak (trailing only)", () => {
    const window: StatusSnapshot[] = [
      snapshot(1_000, [
        ["eu", true],
        ["us", true],
      ]),
      snapshot(2_000, [
        ["eu", false],
        ["us", true],
      ]),
      snapshot(3_000, [
        ["eu", true],
        ["us", true],
      ]),
      snapshot(4_000, [
        ["eu", false],
        ["us", true],
      ]),
    ];
    const derived = deriveStatus(window, T);

    expect(derived.state).toBe("operational");
    expect(derived.regions.find((r) => r.region === "eu")?.consecutiveFailures).toBe(1);
    expect(derived.regions.find((r) => r.region === "eu")?.level).toBe("degraded");
  });
});

describe("OP-02 deriveStatus: missing region observations", () => {
  it("stops the backward scan at a missing observation without counting pre-gap failures", () => {
    const window: StatusSnapshot[] = [
      snapshot(1_000, [
        ["eu", false],
        ["us", true],
      ]),
      snapshot(2_000, [["us", true]]),
      snapshot(3_000, [
        ["eu", false],
        ["us", true],
      ]),
      snapshot(4_000, [
        ["eu", false],
        ["us", true],
      ]),
    ];
    const derived = deriveStatus(window, T);

    expect(derived.sufficient).toBe(true);
    // The trailing two failures count; the failure before the missing round
    // does not extend the streak past the gap.
    expect(derived.regions.find((r) => r.region === "eu")).toEqual({
      region: "eu",
      level: "degraded",
      consecutiveFailures: 2,
    });
    expect(derived.regions.find((r) => r.region === "us")).toEqual({
      region: "us",
      level: "operational",
      consecutiveFailures: 0,
    });
    expect(derived.state).toBe("operational");
  });

  it("reads a first-observed failing region as one failure with no prior history", () => {
    const window: StatusSnapshot[] = [
      snapshot(1_000, [["eu", true]]),
      snapshot(2_000, [["eu", true]]),
      snapshot(3_000, [["eu", true]]),
      snapshot(4_000, [
        ["eu", true],
        ["sin", false],
      ]),
    ];
    const derived = deriveStatus(window, T);

    expect(derived.sufficient).toBe(true);
    expect(derived.regions.find((r) => r.region === "sin")).toEqual({
      region: "sin",
      level: "degraded",
      consecutiveFailures: 1,
    });
    expect(derived.regions.find((r) => r.region === "eu")?.level).toBe("operational");
    expect(derived.state).toBe("operational");
  });
});

describe("OP-02 deriveStatus: N-consecutive failures across at least two regions", () => {
  it("reads down when two regions each cross the consecutive-failure threshold", () => {
    const window = failLastRounds(
      failLastRounds(healthyWindow(["eu", "us"], 5, 1_000), "eu", 3),
      "us",
      3,
    );
    const derived = deriveStatus(window, T);

    expect(derived.state).toBe("down");
    expect(derived.sufficient).toBe(true);
    for (const region of ["eu", "us"]) {
      expect(derived.regions.find((r) => r.region === region)?.level).toBe("down");
      expect(derived.regions.find((r) => r.region === region)?.consecutiveFailures).toBe(3);
    }
  });

  it("never reads down below the configured threshold, even with two regions failing", () => {
    const window = failLastRounds(
      failLastRounds(healthyWindow(["eu", "us"], 5, 1_000), "eu", 2),
      "us",
      2,
    );
    const derived = deriveStatus(window, T);

    expect(derived.state).toBe("degraded");
    expect(derived.regions.every((r) => r.level !== "down")).toBe(true);
  });

  it("reads degraded (not down) when only one region crosses the threshold", () => {
    const window = failLastRounds(healthyWindow(["eu", "us"], 5, 1_000), "eu", 3);
    const derived = deriveStatus(window, T);

    expect(derived.state).toBe("degraded");
    expect(derived.regions.find((r) => r.region === "eu")?.level).toBe("down");
    expect(derived.regions.find((r) => r.region === "us")?.level).toBe("operational");
  });
});

describe("OP-02 deriveStatus: recovery clears degraded and down", () => {
  it("clears a degraded region as soon as one healthy observation arrives", () => {
    const partial = failLastRounds(healthyWindow(["eu", "us"], 4, 1_000), "eu", 2);
    expect(deriveStatus(partial, T).state).toBe("operational");

    const recovered = [
      ...partial,
      snapshot(5_000, [
        ["eu", true],
        ["us", true],
      ]),
    ];
    const derived = deriveStatus(recovered, T);
    expect(derived.state).toBe("operational");
    expect(derived.regions.find((r) => r.region === "eu")).toEqual({
      region: "eu",
      level: "operational",
      consecutiveFailures: 0,
    });
  });

  it("clears a down state once both regions report healthy", () => {
    const failing = failLastRounds(
      failLastRounds(healthyWindow(["eu", "us"], 4, 1_000), "eu", 3),
      "us",
      3,
    );
    expect(deriveStatus(failing, T).state).toBe("down");

    const recovered = [
      ...failing,
      snapshot(5_000, [
        ["eu", true],
        ["us", true],
      ]),
      snapshot(6_000, [
        ["eu", true],
        ["us", true],
      ]),
    ];
    const derived = deriveStatus(recovered, T);
    expect(derived.state).toBe("operational");
    expect(derived.regions.every((r) => r.consecutiveFailures === 0)).toBe(true);
  });
});

describe("OP-02 deriveStatus: unknown and insufficient observations", () => {
  it("stays explicitly unknown with no snapshots", () => {
    const derived = deriveStatus([], T);

    expect(derived.state).toBe("unknown");
    expect(derived.sufficient).toBe(false);
    expect(derived.observedAt).toBeNull();
    expect(derived.regions).toEqual([]);
  });

  it("stays unknown while the window is shorter than the consecutive-failure threshold", () => {
    const partial = healthyWindow(["eu", "us"], 2, 1_000);
    const derived = deriveStatus(partial, T);

    expect(derived.state).toBe("unknown");
    expect(derived.sufficient).toBe(false);
    expect(derived.observedAt).toBe(2_000);
    expect(derived.regions).toHaveLength(2);
    expect(derived.regions.every((r) => r.level === "operational")).toBe(true);
  });

  it("stays unknown when fewer distinct regions are monitored than the down determination requires", () => {
    const singleRegion = healthyWindow(["eu"], 5, 1_000);
    const derived = deriveStatus(singleRegion, T);

    expect(derived.state).toBe("unknown");
    expect(derived.sufficient).toBe(false);
  });

  it("reflects the latest snapshot observedAt in the derived result", () => {
    const window = healthyWindow(["eu", "us"], 3, 42_000);
    expect(deriveStatus(window, T).observedAt).toBe(44_000);
  });
});

describe("OP-02 deriveStatus: aggregate-only output shape", () => {
  it("the derived payload exposes only aggregate operational fields", () => {
    const window = failLastRounds(healthyWindow(["eu", "us"], 4, 1_000), "eu", 2);
    const derived = deriveStatus(window, T);

    expect(Object.keys(derived).sort()).toEqual(["observedAt", "regions", "state", "sufficient"]);
    for (const region of derived.regions) {
      expect(Object.keys(region).sort()).toEqual(["consecutiveFailures", "level", "region"]);
    }
    const serialized = JSON.stringify(derived).toLowerCase();
    for (const sensitive of [
      "filename",
      "objectkey",
      "signedurl",
      "url",
      "password",
      "metadata",
      "payload",
    ]) {
      expect(serialized).not.toContain(sensitive);
    }
  });
});
