import { TOOL_IDS } from "./tool-ids";

export const productStatus = {
  available: [
    "frontend-shell",
    "backend-health",
    "deployment-templates",
    "continuous-integration",
  ] as const,
  plannedTools: TOOL_IDS,
} as const;
