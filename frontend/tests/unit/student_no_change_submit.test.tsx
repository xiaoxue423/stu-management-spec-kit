import { describe, expect, it } from "vitest";

import { isStudentFormChanged } from "../../src/components/studentFormUtils";

describe("student no change submit", () => {
  it("returns false when edit payload is unchanged", () => {
    const base = {
      name: "张三",
      studentNo: "S001",
      gender: "male" as const,
      month: 6,
      subject: "math" as const,
      score: "90",
    };
    expect(isStudentFormChanged(base, base)).toBe(false);
  });

  it("returns true when any field changes", () => {
    const initial = {
      name: "张三",
      studentNo: "S001",
      gender: "male" as const,
      month: 6,
      subject: "math" as const,
      score: "90",
    };
    const current = { ...initial, score: "91" };
    expect(isStudentFormChanged(initial, current)).toBe(true);
  });
});
