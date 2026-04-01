export const GENDER_OPTIONS = ["male", "female"] as const;
export const SUBJECT_OPTIONS = ["math", "chinese", "english"] as const;
export const MONTH_OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] as const;
export const GENDER_LABELS: Record<Gender, "男" | "女"> = {
  male: "男",
  female: "女",
};
export const SUBJECT_LABELS: Record<Subject, "数学" | "语文" | "英语"> = {
  math: "数学",
  chinese: "语文",
  english: "英语",
};

export type Gender = (typeof GENDER_OPTIONS)[number];
export type Subject = (typeof SUBJECT_OPTIONS)[number];
export type Month = (typeof MONTH_OPTIONS)[number];

export interface StudentDto {
  id: number;
  student_no: string;
  name: string;
  gender: Gender;
  updated_at?: string;
}

export interface StudentView {
  id: number;
  name: string;
  studentNo: string;
  gender: Gender;
  updatedAt?: string;
}

export interface ScoreDto {
  id: number;
  student_id: number;
  month: number;
  subject: Subject;
  score: string;
  updated_at?: string;
}

export interface CreateStudentPayload {
  studentNo: string;
  name: string;
  gender: Gender;
}

export interface UpdateStudentPayload extends CreateStudentPayload {
  updatedAt: string;
}

export interface UpsertScorePayload {
  month: number;
  subject: Subject;
  score: number;
}

export interface ApiErrorShape {
  code: string;
  message: string;
}

export function toGenderLabel(gender: Gender): string {
  return GENDER_LABELS[gender];
}
