/**
 * OP-02 public-status derivation.
 *
 * Pure, privacy-safe, and VPS-independent: derives an observed-availability
 * label from approved aggregate snapshots only. The module performs no
 * fetch, no I/O, and touches no document metadata, filenames, object keys,
 * signed URLs, or queue payloads.
 *
 * Contract-first (P7 plan Task 2, decision record 4): the live multi-region
 * snapshot producer is owner-gated under R-12 and out of branch scope.
 * Pages render from the safe inputs below (`EMPTY_SNAPSHOTS`) until an
 * approved producer is wired; any producer must feed this module snapshots
 * whose regions report aggregate reachability only.
 */

export interface RegionObservation {
  region: string;
  reachable: boolean;
}

export interface StatusSnapshot {
  observedAt: number;
  regions: readonly RegionObservation[];
}

export interface StatusThresholds {
  consecutiveFailures: number;
  downRegions: number;
}

export type RegionLevel = "operational" | "degraded" | "down";
export type GlobalAvailability = "operational" | "degraded" | "down" | "unknown";

export interface RegionDerivedStatus {
  region: string;
  level: RegionLevel;
  consecutiveFailures: number;
}

export interface DerivedStatus {
  state: GlobalAvailability;
  regions: readonly RegionDerivedStatus[];
  sufficient: boolean;
  observedAt: number | null;
}

export const DEFAULT_THRESHOLDS: StatusThresholds = Object.freeze({
  consecutiveFailures: 3,
  downRegions: 2,
});

export const EMPTY_SNAPSHOTS: readonly StatusSnapshot[] = Object.freeze([]);

function validateThresholds(thresholds: StatusThresholds): void {
  if (!Number.isInteger(thresholds.consecutiveFailures) || thresholds.consecutiveFailures < 1) {
    throw new RangeError("consecutiveFailures must be an integer >= 1");
  }
  if (!Number.isInteger(thresholds.downRegions) || thresholds.downRegions < 2) {
    throw new RangeError("downRegions must be an integer >= 2");
  }
}

function trailingConsecutiveFailures(snapshots: readonly StatusSnapshot[], region: string): number {
  let failures = 0;
  for (let i = snapshots.length - 1; i >= 0; i -= 1) {
    const observation = snapshots[i]?.regions.find((entry) => entry.region === region);
    if (observation === undefined) {
      return failures;
    }
    if (!observation.reachable) {
      failures += 1;
    } else {
      return failures;
    }
  }
  return failures;
}

export function deriveStatus(
  snapshots: readonly StatusSnapshot[],
  thresholds: StatusThresholds = DEFAULT_THRESHOLDS,
): DerivedStatus {
  validateThresholds(thresholds);
  const minFailures = thresholds.consecutiveFailures;
  const minRegions = thresholds.downRegions;

  const latest = snapshots.length > 0 ? snapshots[snapshots.length - 1] : null;
  const observedAt = latest !== null ? latest.observedAt : null;
  const currentRegions = latest !== null ? latest.regions : [];

  const regionRows: RegionDerivedStatus[] = [];
  let downRegionCount = 0;
  let subThresholdRegionCount = 0;
  for (const observation of currentRegions) {
    const consecutiveFailures = trailingConsecutiveFailures(snapshots, observation.region);
    let level: RegionLevel;
    if (consecutiveFailures >= minFailures) {
      level = "down";
      downRegionCount += 1;
    } else if (consecutiveFailures > 0) {
      level = "degraded";
      subThresholdRegionCount += 1;
    } else {
      level = "operational";
    }
    regionRows.push({ region: observation.region, level, consecutiveFailures });
  }

  const insufficient = snapshots.length < minFailures || currentRegions.length < minRegions;
  if (insufficient) {
    return { state: "unknown", regions: regionRows, sufficient: false, observedAt };
  }

  let state: GlobalAvailability;
  if (downRegionCount >= minRegions) {
    state = "down";
  } else if (downRegionCount > 0 || subThresholdRegionCount >= minRegions) {
    state = "degraded";
  } else {
    state = "operational";
  }
  return { state, regions: regionRows, sufficient: true, observedAt };
}
