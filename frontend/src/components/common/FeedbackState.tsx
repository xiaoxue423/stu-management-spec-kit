import { Alert, Button, Empty, Spin } from "antd";
import type { ReactNode } from "react";

interface Props {
  loading: boolean;
  error?: string;
  empty: boolean;
  onRetry?: () => void;
  children: ReactNode;
}

export function FeedbackState({ loading, error, empty, onRetry, children }: Props) {
  if (loading) return <Spin spinning />;
  if (error) {
    return (
      <Alert
        type="error"
        showIcon
        message={error}
        action={
          onRetry ? (
            <Button size="small" onClick={onRetry}>
              重试
            </Button>
          ) : null
        }
      />
    );
  }
  if (empty) return <Empty description="暂无学生数据" />;
  return <>{children}</>;
}
