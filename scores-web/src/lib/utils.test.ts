import { describe, expect, it } from "vitest";

import { cn } from "./utils";

describe("cn utility", () => {
  it("merges class names intelligently", () => {
    const result = cn("px-4", null, "py-2", "px-4");
    expect(result.includes("px-4")).toBe(true);
    expect(result.includes("py-2")).toBe(true);
    const occurrences = result.split("px-4").length - 1;
    expect(occurrences).toBe(1);
  });
});

