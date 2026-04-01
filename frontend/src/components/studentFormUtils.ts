import type { Gender, Subject } from "../types/student";

export interface StudentFormDraft {
  name: string;
  studentNo?: string;
  gender: Gender;
  month: number;
  subject: Subject;
  score: string;
}

export function validateStudentFormInput(draft: StudentFormDraft, options?: { requireStudentNo?: boolean }): string | null {
  if (!draft.name.trim()) {
    return "姓名必填";
  }
  if (options?.requireStudentNo && !draft.studentNo?.trim()) {
    return "学号必填";
  }

  const scoreNumber = Number(draft.score);
  if (!Number.isFinite(scoreNumber) || scoreNumber < 0 || scoreNumber > 100) {
    return "分数必须在 0-100 范围内";
  }
  if (!/^\d+(\.\d{1,2})?$/.test(draft.score)) {
    return "分数最多支持 2 位小数";
  }
  return null;
}

export function isStudentFormChanged(initial: StudentFormDraft | null, current: StudentFormDraft): boolean {
  if (!initial) {
    return true;
  }
  return (
    initial.name !== current.name ||
    initial.studentNo !== current.studentNo ||
    initial.gender !== current.gender ||
    initial.month !== current.month ||
    initial.subject !== current.subject ||
    initial.score !== current.score
  );
}
