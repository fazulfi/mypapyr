/**
 * DEC-062: Papyr's automated accessibility baseline targets WCAG 2.2 AA.
 * Keep the complete WCAG 2.2 A/AA rule set enabled, including target-size,
 * so exceptions remain explicit and reviewable rather than hidden in tooling.
 */
module.exports = {
  runOnly: {
    type: "tag",
    values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
  },
  rules: {
    "target-size": { enabled: true },
  },
};
