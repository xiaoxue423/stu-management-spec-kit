import { App as AntdApp } from "antd";
import { StudentListPage } from "./pages/StudentListPage";

export function App() {
  return (
    <AntdApp>
      <StudentListPage />
    </AntdApp>
  );
}
