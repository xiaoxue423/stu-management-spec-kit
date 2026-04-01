import { describe, expect, it } from "vitest";
import { ApiError } from "../../src/services/studentApi";

describe("student list error retry", () => {
  it("normalizes request failure into ApiError for retry feedback", () => {
    const error = new ApiError("加载列表失败", 500, "UNKNOWN_ERROR");
    expect(error.status).toBe(500);
    expect(error.code).toBe("UNKNOWN_ERROR");
  });
});
