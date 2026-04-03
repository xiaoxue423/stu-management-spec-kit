# 学生成绩模块调用流程（前端视角）

这份文档对应后端路由文件 `backend/src/api/student_scores.py`，用于前端联调时快速定位“请求发到哪里、后端做了什么、返回长什么样”。

## 1) 总入口

- 路由前缀：`/api/v1/students`
- 路由层职责：参数接收与校验、调用 service、包装响应、统一错误结构
- 成功响应：`{ data: ... }`
- 失败响应：`{ detail: { code, message } }`

## 2) 接口流程图（文字版）

### A. 学生列表

前端页面加载  
-> `listStudents()`  
-> `GET /api/v1/students`  
-> 后端查询学生列表  
-> 返回 `{ data: StudentDto[] }`  
-> 前端 `toStudentView` 做字段映射（`student_no -> studentNo`、`updated_at -> updatedAt`）

---

### B. 新建学生

前端点“新建并保存”  
-> `createStudent(payload)`  
-> `POST /api/v1/students`  
-> body: `{ name, gender }`  
-> 后端创建学生  
-> 返回 `{ data: StudentDto }`  
-> 前端刷新列表

---

### C. 编辑学生基本信息

前端点“编辑”  
-> `getEditForm(studentId)`（先拉取编辑初始化数据）  
-> `GET /api/v1/students/{studentId}/edit-form`  
-> 返回 `{ data: { student, scores } }`

用户修改后保存  
-> `updateStudent(studentId, payload)`  
-> `PUT /api/v1/students/{studentId}`  
-> body: `{ name, gender, updatedAt }`  
-> 后端更新学生信息  
-> 返回 `{ data: StudentDto }`

---

### D. 录入/更新成绩（upsert）

编辑弹窗里填写某月某科成绩并保存  
-> `upsertScore(studentId, payload)`  
-> `POST /api/v1/students/{studentId}/scores`  
-> body: `{ month, subject, score }`  
-> 后端按“存在则更新，不存在则新增”处理  
-> 返回 `{ data: ScoreDto }`

## 3) 错误处理约定（前端要点）

- 后端业务异常会被封装成：
  - HTTP 状态码：按业务场景返回（如 400/404/409）
  - 响应体：`{ detail: { code, message } }`
- 前端当前实现（`studentApi.ts`）会：
  - 读取 `detail.message` 作为错误提示
  - 读取 `detail.code` 作为 `ApiError.code` 便于分支处理
  - 未知结构时兜底 `API_ERROR`

## 4) 联调 checklist

- `PUT` 的时间字段是 `updatedAt`（驼峰）  
- 列表展示字段需要映射：`student_no -> studentNo`  
- 分数字段后端用 Decimal，前端输入建议保证可转成数字  
- 统一按 `data` 取成功数据，按 `detail` 取失败详情
