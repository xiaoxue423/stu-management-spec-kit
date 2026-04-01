import { useEffect, useMemo, useState } from "react";
import { Alert, Button, Form, Input, Modal, Select, Space } from "antd";
import { createStudent, getEditForm, updateStudent, upsertScore } from "../services/studentApi";
import { GENDER_LABELS, GENDER_OPTIONS, Subject } from "../types/student";
import { ScoreFieldGroup } from "./ScoreFieldGroup";
import {
  StudentFormDraft,
  isStudentFormChanged,
  validateStudentFormInput,
} from "./studentFormUtils";

type Mode = "create" | "edit";

interface Props {
  open: boolean;
  mode: Mode;
  studentId?: number;
  onClose: () => void;
  onSuccess: () => void;
}

export function StudentFormModal(props: Props) {
  const [form] = Form.useForm();
  const [name, setName] = useState("");
  const [studentNo, setStudentNo] = useState("");
  const [gender, setGender] = useState<(typeof GENDER_OPTIONS)[number]>("male");
  const [month, setMonth] = useState(1);
  const [subject, setSubject] = useState("math");
  const [score, setScore] = useState("");
  const [updatedAt, setUpdatedAt] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [initialDraft, setInitialDraft] = useState<StudentFormDraft | null>(null);

  const scoreNumber = useMemo(() => Number(score), [score]);

  useEffect(() => {
    if (!props.open) {
      form.resetFields();
      setError("");
      setInitialDraft(null);
      return;
    }
    if (props.mode === "create") {
      setName("");
      setStudentNo("");
      setGender("male");
      setMonth(1);
      setSubject("math");
      setScore("");
      setUpdatedAt("");
      return;
    }
    if (!props.open || props.mode !== "edit" || !props.studentId) return;
    getEditForm(props.studentId)
      .then((data) => {
        setName(data.student.name);
        setStudentNo(data.student.student_no);
        setGender(data.student.gender);
        setUpdatedAt(data.student.updated_at);
        if (data.scores[0]) {
          setMonth(data.scores[0].month);
          setSubject(data.scores[0].subject as Subject);
          setScore(data.scores[0].score);
          setInitialDraft({
            name: data.student.name,
            studentNo: data.student.student_no,
            gender: data.student.gender,
            month: data.scores[0].month,
            subject: data.scores[0].subject,
            score: data.scores[0].score,
          });
          return;
        }
        setInitialDraft({
          name: data.student.name,
          studentNo: data.student.student_no,
          gender: data.student.gender,
          month: 1,
          subject: "math",
          score: "",
        });
      })
      .catch(() => setError("加载回显数据失败"));
  }, [form, props.open, props.mode, props.studentId]);

  if (!props.open) return null;

  async function submit() {
    const draft: StudentFormDraft = {
      name,
      studentNo,
      gender,
      month,
      subject: subject as Subject,
      score,
    };
    const validationMessage = validateStudentFormInput(draft);
    if (validationMessage) {
      setError(validationMessage);
      return;
    }
    if (props.mode === "edit" && !isStudentFormChanged(initialDraft, draft)) {
      setError("未检测到变更");
      return;
    }
    setError("");
    try {
      setSubmitting(true);
      const student =
        props.mode === "create"
          ? await createStudent({ name, studentNo, gender })
          : await updateStudent(props.studentId!, { name, studentNo, gender, updatedAt });
      await upsertScore(student.id, { month, subject: subject as "math" | "chinese" | "english", score: scoreNumber });
      props.onSuccess();
      props.onClose();
    } catch {
      setError("提交失败，请重试");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={props.open}
      title={props.mode === "create" ? "新建学生" : "编辑学生"}
      footer={null}
      onCancel={props.onClose}
      destroyOnClose
    >
      <Form form={form} layout="vertical">
        <Form.Item label="姓名" required>
          <Input value={name} onChange={(e) => setName(e.target.value)} />
        </Form.Item>
        <Form.Item label="学号" required>
          <Input value={studentNo} onChange={(e) => setStudentNo(e.target.value)} />
        </Form.Item>
        <Form.Item label="性别" required>
          <Select
            value={gender}
            options={GENDER_OPTIONS.map((item) => ({ value: item, label: GENDER_LABELS[item] }))}
            onChange={(value) => setGender(value)}
          />
        </Form.Item>
        <Form.Item label="成绩信息">
          <ScoreFieldGroup
            month={month}
            subject={subject}
            score={score}
            onMonthChange={setMonth}
            onSubjectChange={setSubject}
            onScoreChange={setScore}
          />
        </Form.Item>
        {error ? (
          <Form.Item>
            <Alert type="error" showIcon message={error} />
          </Form.Item>
        ) : null}
        <Space>
          <Button type="primary" loading={submitting} onClick={submit}>
            保存
          </Button>
          <Button onClick={props.onClose}>取消</Button>
        </Space>
      </Form>
    </Modal>
  );
}
