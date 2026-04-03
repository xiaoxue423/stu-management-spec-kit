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
  name: string;
  gender: Gender;
}

export interface UpdateStudentPayload {
  name: string;
  gender: Gender;
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

/**
 * 统一成功响应外层结构：
 * 后端约定大多数接口都返回 { data: ... }。
 */
export interface ApiSuccessResponse<T> {
  data: T;
}

/**
 * 统一错误响应外层结构：
 * FastAPI 在抛 HTTPException 时，错误内容放在 detail 字段。
 */
export interface ApiErrorResponse {
  detail: ApiErrorShape;
}

/**
 * GET /api/v1/students/{student_id}/edit-form 返回的数据体。
 * 用于“编辑学生”弹窗初始化：一次拿到学生信息 + 成绩列表。
 */
export interface EditFormData {
  student: StudentDto;
  scores: ScoreDto[];
}

/**
 * 仅用于前端联调时“看契约”更直观：
 * 把每个接口的请求与响应类型都集中定义。
 */
export interface StudentApiContract {
  listStudents: {
    request: void;
    response: ApiSuccessResponse<StudentDto[]>;
  };
  createStudent: {
    request: CreateStudentPayload;
    response: ApiSuccessResponse<StudentDto>;
  };
  updateStudent: {
    request: { studentId: number; payload: UpdateStudentPayload };
    response: ApiSuccessResponse<StudentDto>;
  };
  upsertScore: {
    request: { studentId: number; payload: UpsertScorePayload };
    response: ApiSuccessResponse<ScoreDto>;
  };
  getEditForm: {
    request: { studentId: number };
    response: ApiSuccessResponse<EditFormData>;
  };
}

export function toGenderLabel(gender: Gender): string {
  return GENDER_LABELS[gender];
}
