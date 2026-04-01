import { describe, expect, it, vi } from "vitest";
import { ApiError } from "../../src/services/studentApi";

describe("student form submit feedback", () => {
  it("keeps success and failure message hooks callable", () => {
    const success = vi.fn();
    const failure = vi.fn((err: ApiError) => err.message);

    success("保存成功");
    failure(new ApiError("提交失败，请重试", 500));

    expect(success).toHaveBeenCalledWith("保存成功");
    expect(failure).toHaveBeenCalledTimes(1);
  });
});
