import { describe, expect, it } from "vitest";
import { toGenderLabel } from "../../src/types/student";

describe("student list empty state", () => {
  it("keeps Chinese gender mapping usable for empty/list rendering", () => {
    expect(toGenderLabel("male")).toBe("男");
    expect(toGenderLabel("female")).toBe("女");
  });
});
