import { describe, expect, it, vi } from "vitest";

import { createStudent, upsertScore } from "../../src/services/studentApi";

describe("student create flow", () => {
  it("creates student then upserts score", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ data: { id: 1, student_no: "0001", name: "张三", gender: "male" } }), {
          status: 200,
        })
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ data: { id: 1, student_id: 1, month: 6, subject: "math", score: "90", updated_at: "" } }),
          { status: 200 }
        )
      );

    const student = await createStudent({ name: "张三", gender: "male" });
    const score = await upsertScore(student.id, { month: 6, subject: "math", score: 90 });

    expect(student.id).toBe(1);
    expect(student.student_no).toBe("0001");
    expect(score.student_id).toBe(1);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    fetchMock.mockRestore();
  });
});
