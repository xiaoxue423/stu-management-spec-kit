export const GENDER_OPTIONS = ["male", "female"] as const;
export const SUBJECT_OPTIONS = ["math", "chinese", "english"] as const;
export const MONTH_OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] as const;

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
