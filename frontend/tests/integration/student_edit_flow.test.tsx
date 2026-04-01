import { describe, expect, it, vi } from "vitest";

import { getEditForm, updateStudent } from "../../src/services/studentApi";

describe("student edit flow", () => {
  it("loads edit-form then updates student", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            data: {
              student: { id: 1, student_no: "S001", name: "张三", gender: "male", updated_at: "2026-01-01T00:00:00" },
              scores: [{ id: 1, student_id: 1, month: 6, subject: "math", score: "90", updated_at: "" }],
            },
          }),
          { status: 200 }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            data: { id: 1, student_no: "S001", name: "李四", gender: "female", updated_at: "2026-01-02T00:00:00" },
          }),
          { status: 200 }
        )
      );

    const editForm = await getEditForm(1);
    const updated = await updateStudent(1, {
      studentNo: editForm.student.student_no,
      name: "李四",
      gender: "female",
      updatedAt: editForm.student.updated_at!,
    });

    expect(editForm.student.id).toBe(1);
    expect(updated.name).toBe("李四");
    expect(fetchMock).toHaveBeenCalledTimes(2);
    fetchMock.mockRestore();
  });
});
