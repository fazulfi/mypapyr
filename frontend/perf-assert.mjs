#!/usr/bin/env node
/**
 * Papyr performance assertion runner (VL-04, R-27).
 *
 * Replaces LHCI: runs Lighthouse directly (lighthouse CLI --output=json) against
 * the built app, parses the JSON report, and fails closed when any Core Web
 * Vital or category threshold is not met.
 *
 * Thresholds (per docs/specifications, R-27 / DEC-200 / DEC-201):
 *   - performance / accessibility / best-practices / seo categories >= 0.9
 *   - FCP <= 1800 ms, LCP <= 2500 ms, CLS <= 0.1, TBT <= 300 ms
 *
 * Usage:
 *   node perf-assert.mjs [baseUrl]
 *   (baseUrl defaults to http://localhost:3000; the server must already be running)
 */
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const BASE_URL = process.argv[2] ?? "http://localhost:3000";
const URLS = [`${BASE_URL}/en`, `${BASE_URL}/en/compress-pdf`];
const OUTPUT_DIR = join(ROOT, ".lighthouseci");
const OUT_FILE = join(OUTPUT_DIR, "report.json");

const CATEGORY_MIN = 0.9;
const METRICS = {
  "first-contentful-paint": { max: 1800, label: "FCP" },
  "largest-contentful-paint": { max: 2500, label: "LCP" },
  "cumulative-layout-shift": { max: 0.1, label: "CLS" },
  "total-blocking-time": { max: 300, label: "TBT" },
};

if (!existsSync(OUTPUT_DIR)) {
  mkdirSync(OUTPUT_DIR, { recursive: true });
}

const lighthouseBin = join(ROOT, "node_modules", "lighthouse", "cli", "index.js");
if (!existsSync(lighthouseBin)) {
  console.error("perf-assert: lighthouse CLI not found at", lighthouseBin);
  process.exit(1);
}

/** @param {string} url */
function runLighthouse(url) {
  const json = execFileSync(
    process.execPath,
    [
      lighthouseBin,
      url,
      "--output=json",
      "--output-path=stdout",
      "--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage",
      "--only-categories=performance,accessibility,best-practices,seo",
    ],
    { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], timeout: 180000 },
  );
  return JSON.parse(json);
}

const failures = [];
let passed = 0;

for (const url of URLS) {
  const report = runLighthouse(url);
  const { categories, audits } = report;

  for (const [id, category] of Object.entries(categories)) {
    const score = category.score ?? 0;
    if (score < CATEGORY_MIN) {
      failures.push(`${url} category ${id}: ${Math.round(score * 100)} (min ${CATEGORY_MIN * 100})`);
    } else {
      passed += 1;
    }
  }

  for (const [id, { max, label }] of Object.entries(METRICS)) {
    const audit = audits[id];
    const value = audit?.numericValue ?? Number.POSITIVE_INFINITY;
    if (value > max) {
      failures.push(`${url} ${label}: ${Math.round(value)} ms (max ${max})`);
    } else {
      passed += 1;
    }
  }
}

writeFileSync(OUT_FILE, JSON.stringify({ passed, failures, generatedAt: new Date().toISOString() }, null, 2));

if (failures.length > 0) {
  console.error("perf-assert: FAIL");
  for (const failure of failures) {
    console.error(`  - ${failure}`);
  }
  process.exit(1);
}

console.log(`perf-assert: PASS (${passed} assertions)`);
