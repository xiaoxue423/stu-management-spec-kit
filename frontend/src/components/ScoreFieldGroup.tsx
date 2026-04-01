import { Input, Select, Space } from "antd";
import { MONTH_OPTIONS, SUBJECT_OPTIONS } from "../types/student";

interface Props {
  month: number;
  subject: string;
  score: string;
  onMonthChange: (value: number) => void;
  onSubjectChange: (value: string) => void;
  onScoreChange: (value: string) => void;
}

export function ScoreFieldGroup(props: Props) {
  return (
    <Space>
      <Select
        value={props.month}
        options={MONTH_OPTIONS.map((month) => ({ value: month, label: `${month} 月` }))}
        onChange={props.onMonthChange}
        style={{ width: 120 }}
      />
      <Select
        value={props.subject}
        options={SUBJECT_OPTIONS.map((subject) => ({ value: subject, label: subject }))}
        onChange={props.onSubjectChange}
        style={{ width: 140 }}
      />
      <Input
        value={props.score}
        onChange={(e) => props.onScoreChange(e.target.value)}
        placeholder="0-100，最多2位小数"
        style={{ width: 180 }}
      />
    </Space>
  );
}
