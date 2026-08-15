import { describe, expect, it } from "vitest";

import ogImage, {
  alt as ogAlt,
  size as ogSize,
  contentType as ogContentType,
} from "../opengraph-image";
import twitterImage, {
  alt as twitterAlt,
  size as twitterSize,
  contentType as twitterContentType,
} from "../twitter-image";

describe("T8 opengraph-image", () => {
  it("exports the correct size (1200x630)", () => {
    expect(ogSize).toEqual({ width: 1200, height: 630 });
  });

  it("exports PNG content type", () => {
    expect(ogContentType).toBe("image/png");
  });

  it("exports a non-empty alt text", () => {
    expect(ogAlt.trim()).not.toBe("");
  });

  it("exports a default async function that returns an ImageResponse", async () => {
    const response = await ogImage();
    expect(response).toBeDefined();
  });
});

describe("T8 twitter-image", () => {
  it("exports the correct size (1200x630)", () => {
    expect(twitterSize).toEqual({ width: 1200, height: 630 });
  });

  it("exports PNG content type", () => {
    expect(twitterContentType).toBe("image/png");
  });

  it("exports a non-empty alt text", () => {
    expect(twitterAlt.trim()).not.toBe("");
  });

  it("exports a default async function that returns an ImageResponse", async () => {
    const response = await twitterImage();
    expect(response).toBeDefined();
  });
});
