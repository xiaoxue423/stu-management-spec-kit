import { describe, expect, it } from "vitest";

import { validateStudentFormInput } from "../../src/components/studentFormUtils";

describe("student form validation", () => {
  it("rejects required fields", () => {
    const result = validateStudentFormInput({
      name: "",
      gender: "male",
      month: 1,
      subject: "math",
      score: "90",
    });
    expect(result).toBe("姓名必填");
  });

  it("rejects score out of range", () => {
    const result = validateStudentFormInput({
      name: "张三",
      gender: "male",
      month: 1,
      subject: "math",
      score: "101",
    });
    expect(result).toBe("分数必须在 0-100 范围内");
  });

  it("rejects score precision over 2 decimals", () => {
    const result = validateStudentFormInput({
      name: "张三",
      gender: "male",
      month: 1,
      subject: "math",
      score: "88.888",
    });
    expect(result).toBe("分数最多支持 2 位小数");
  });

  it("accepts valid payload", () => {
    const result = validateStudentFormInput({
      name: "张三",
      gender: "male",
      month: 1,
      subject: "math",
      score: "88.88",
    });
    expect(result).toBeNull();
  });

  it("rejects missing studentNo in edit mode only", () => {
    const result = validateStudentFormInput(
      {
        name: "张三",
        studentNo: "",
        gender: "male",
        month: 1,
        subject: "math",
        score: "88.88",
      },
      { requireStudentNo: true }
    );
    expect(result).toBe("学号必填");
  });
});
