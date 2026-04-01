import { useEffect, useState } from "react";
import { Button, Table, Typography, message } from "antd";
import type { ColumnsType } from "antd/es/table";
import { FeedbackState } from "../components/common/FeedbackState";
import { StudentFormModal } from "../components/StudentFormModal";
import { listStudents } from "../services/studentApi";
import { toGenderLabel, type StudentView } from "../types/student";

export function StudentListPage() {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<"create" | "edit">("create");
  const [editingId, setEditingId] = useState<number | undefined>();
  const [rows, setRows] = useState<StudentView[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [messageApi, contextHolder] = message.useMessage();

  const columns: ColumnsType<StudentView> = [
    {
      title: "姓名",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "学号",
      dataIndex: "studentNo",
      key: "studentNo",
    },
    {
      title: "性别",
      dataIndex: "gender",
      key: "gender",
      render: (value: StudentView["gender"]) => toGenderLabel(value),
    },
    {
      title: "操作",
      key: "action",
      render: (_, row) => (
        <Button
          onClick={() => {
            setMode("edit");
            setEditingId(row.id);
            setOpen(true);
          }}
        >
          编辑
        </Button>
      ),
    },
  ];

  const refresh = async () => {
    setIsLoading(true);
    try {
      const students = await listStudents();
      setRows(students);
      setError("");
    } catch (e) {
      setRows([]);
      setError(e instanceof Error ? e.message : "加载列表失败");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="page-container">
      {contextHolder}
      <div className="page-header">
        <Typography.Title level={2} className="page-title">
          学生列表
        </Typography.Title>
        <Button
          type="primary"
          onClick={() => {
            setMode("create");
            setEditingId(undefined);
            setOpen(true);
          }}
        >
          新建
        </Button>
      </div>
      <div className="page-error">
        <FeedbackState loading={isLoading} error={error} empty={rows.length === 0} onRetry={refresh}>
          <Table rowKey="id" columns={columns} dataSource={rows} pagination={false} />
        </FeedbackState>
      </div>

      <StudentFormModal
        open={open}
        mode={mode}
        studentId={editingId}
        onClose={() => setOpen(false)}
        onSuccess={async () => {
          await refresh();
          void messageApi.success("保存成功");
        }}
      />
    </div>
  );
}
