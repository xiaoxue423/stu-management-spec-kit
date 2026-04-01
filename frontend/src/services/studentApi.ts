import type {
  ApiErrorShape,
  CreateStudentPayload,
  ScoreDto,
  StudentDto,
  StudentView,
  UpdateStudentPayload,
  UpsertScorePayload,
} from "../types/student";

const BASE = "/api/v1/students";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, status: number, code = "API_ERROR") {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!resp.ok) {
    let errorPayload: { detail?: ApiErrorShape } | undefined;
    try {
      errorPayload = await resp.json();
    } catch {
      errorPayload = undefined;
    }
    const detail = errorPayload?.detail;
    throw new ApiError(detail?.message ?? `API error: ${resp.status}`, resp.status, detail?.code ?? "API_ERROR");
  }
  return resp.json();
}

function toStudentView(student: StudentDto): StudentView {
  return {
    id: student.id,
    name: student.name,
    studentNo: student.student_no,
    gender: student.gender,
    updatedAt: student.updated_at,
  };
}

export async function listStudents(): Promise<StudentView[]> {
  const data = await request<{ data: StudentDto[] }>(BASE);
  return data.data.map(toStudentView);
}

export async function createStudent(payload: CreateStudentPayload): Promise<StudentDto> {
  const data = await request<{ data: StudentDto }>(BASE, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return data.data;
}

export async function updateStudent(studentId: number, payload: UpdateStudentPayload): Promise<StudentDto> {
  const data = await request<{ data: StudentDto }>(`${BASE}/${studentId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return data.data;
}

export async function upsertScore(studentId: number, payload: UpsertScorePayload): Promise<ScoreDto> {
  const data = await request<{ data: ScoreDto }>(`${BASE}/${studentId}/scores`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return data.data;
}

export async function getEditForm(studentId: number): Promise<{ student: StudentDto; scores: ScoreDto[] }> {
  const data = await request<{ data: { student: StudentDto; scores: ScoreDto[] } }>(`${BASE}/${studentId}/edit-form`);
  return data.data;
}
