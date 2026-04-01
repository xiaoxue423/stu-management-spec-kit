import { describe, expect, it } from "vitest";

describe("student list empty state", () => {
  it("has a placeholder for empty state assertion", () => {
    expect([]).toHaveLength(0);
  });
});
