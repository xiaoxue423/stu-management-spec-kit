# 任务: switch-antd-components

**输入**: 来自 `/specs/003-switch-antd-components/` 的设计文档  
**前置条件**: `design.md`(必需)、`spec.md`(必需)

**测试**: 规范已明确关键路径与回归验证要求，包含测试任务。  
**组织结构**: 任务按用户故事分组，确保可独立实现与验证。

## 格式: `[ID] [P?] [Story] 描述`
- **[P]**: 可并行（不同文件、无直接依赖）
- **[Story]**: 所属用户故事（US1、US2、US3）

## 路径约定
- 前端: `frontend/src/`、`frontend/tests/`
- 后端（仅回归校验）: `backend/src/`、`backend/tests/`

---

## 阶段 1: 设置（共享基础）

**目的**: 为 antd 统一改造准备依赖与基础结构

- [ ] T001 [P] [Setup] 在 `frontend/package.json` 安装并声明 `antd` 依赖，确认构建脚本可用。
- [ ] T002 [Setup] 在 `frontend/src/main.tsx` 接入 antd 全局样式入口，确保页面样式可加载。
- [ ] T003 [P] [Setup] 在 `frontend/src/styles/` 新增统一交互样式约束文件（如按钮间距、容器间距、空态布局）。
- [ ] T004 [Setup] 在 `frontend/src/App.tsx` 或根布局挂载全局消息上下文（用于统一成功/失败提示）。

---

## 阶段 2: 基础（阻塞前置）

**目的**: 在任何用户故事开始前完成的公共能力

**⚠️ 关键**: 本阶段未完成前不得进入 US1/US2/US3

- [ ] T005 [P] [Foundation] 在 `frontend/src/types/student.ts` 统一前端学生展示模型（含 `studentNo` 映射字段）。
- [ ] T006 [Foundation] 在 `frontend/src/services/studentApi.ts` 统一 API 响应映射与错误归一化（字段映射、错误对象结构）。
- [ ] T007 [P] [Foundation] 在 `frontend/src/components/common/` 新增通用反馈组件（加载、空状态、错误重试容器）。
- [ ] T008 [Foundation] 在 `frontend/src/pages/StudentListPage.tsx` 预留统一状态机骨架（`loading/success/error/empty`）。
- [ ] T009 [Foundation] 在 `frontend/tests/integration/student-list-foundation.test.tsx` 建立基础回归测试骨架（渲染+状态切换）。

**检查点**: 基础就绪，可并行推进用户故事阶段。

---

## 阶段 3: 用户故事 1 - 统一控件风格与主要交互（P1）🎯 MVP

**目标**: 列表/表格/主操作按钮/加载反馈统一为 antd 组件体验。  
**独立测试**: 打开页面并完成“加载 -> 浏览列表 -> 点击主操作”闭环，无原生主流程控件。

### 测试任务（先写后改）
- [ ] T010 [P] [US1] 在 `frontend/tests/integration/student-list-ui-consistency.test.tsx` 编写列表加载成功与失败反馈一致性测试。
- [ ] T011 [P] [US1] 在 `frontend/tests/unit/student-list-actions.test.tsx` 编写主操作按钮状态（可点击/加载/禁用）测试。

### 实现任务
- [ ] T012 [US1] 在 `frontend/src/pages/StudentListPage.tsx` 将原生按钮/表格替换为 antd `Button` + `Table`。
- [ ] T013 [US1] 在 `frontend/src/pages/StudentListPage.tsx` 接入 antd `Spin` / `Alert` / `Empty` 统一加载、错误、空态反馈。
- [ ] T014 [P] [US1] 在 `frontend/src/components/StudentFormModal.tsx` 统一触发入口按钮与弹窗标题/操作区风格。
- [ ] T015 [US1] 在 `frontend/src/services/studentApi.ts` 对齐列表数据映射，确保 `student_no -> studentNo` 渲染稳定。
- [ ] T016 [US1] 在 `frontend/tests/integration/student-list-ui-consistency.test.tsx` 补齐重试路径断言并通过。

**检查点**: US1 可单独演示并满足 MVP。

---

## 阶段 4: 用户故事 2 - 输入校验与反馈一致（P2）

**目标**: 新建/编辑表单输入、校验、提交结果提示统一。  
**独立测试**: 能独立完成一次“无效输入 -> 校验提示 -> 修正提交 -> 成功反馈”流程。

### 测试任务（先写后改）
- [ ] T017 [P] [US2] 在 `frontend/tests/integration/student-form-validation.test.tsx` 编写字段校验与内联错误提示测试。
- [ ] T018 [P] [US2] 在 `frontend/tests/integration/student-form-submit-feedback.test.tsx` 编写提交成功/失败提示一致性测试。

### 实现任务
- [ ] T019 [US2] 在 `frontend/src/components/StudentFormModal.tsx` 使用 antd `Form`、`Input`、`Select` 改造编辑表单。
- [ ] T020 [US2] 在 `frontend/src/components/StudentFormModal.tsx` 统一字段级错误提示与提交按钮 loading 状态。
- [ ] T021 [US2] 在 `frontend/src/pages/StudentListPage.tsx` 统一提交成功后刷新列表与消息提示行为。
- [ ] T022 [US2] 在 `frontend/src/services/studentApi.ts` 归一化表单提交失败错误信息，避免原生异常直出。
- [ ] T023 [US2] 在 `frontend/tests/integration/student-form-validation.test.tsx` 与 `frontend/tests/integration/student-form-submit-feedback.test.tsx` 完成回归断言并通过。

**检查点**: US2 可独立验证，不依赖 US3。

---

## 阶段 5: 用户故事 3 - 空状态/异常提示一致（P3）

**目标**: 空数据与异常反馈一致、可理解、可重试。  
**独立测试**: 模拟空数据与失败响应时，页面反馈风格一致且主操作可继续。

### 测试任务（先写后改）
- [ ] T024 [P] [US3] 在 `frontend/tests/integration/student-list-empty-state.test.tsx` 编写空列表展示与引导测试。
- [ ] T025 [P] [US3] 在 `frontend/tests/integration/student-list-error-retry.test.tsx` 编写错误提示与重试恢复测试。

### 实现任务
- [ ] T026 [US3] 在 `frontend/src/pages/StudentListPage.tsx` 统一空状态文案与结构，避免空白区域。
- [ ] T027 [US3] 在 `frontend/src/pages/StudentListPage.tsx` 统一失败提示与重试入口交互。
- [ ] T028 [P] [US3] 在 `frontend/src/components/common/` 补齐空态/错误态组件的可复用参数（文案、重试回调）。
- [ ] T029 [US3] 在 `frontend/tests/integration/student-list-empty-state.test.tsx` 与 `frontend/tests/integration/student-list-error-retry.test.tsx` 完成回归验证。

**检查点**: 三个用户故事均可独立通过验收场景。

---

## 阶段 6: 完善与横切关注点

**目的**: 收尾、验收、范围守卫检查

- [ ] T030 [P] [Polish] 在 `frontend/tests/integration/` 运行并修复全量回归失败用例。
- [ ] T031 [Polish] 在 `frontend/src/pages/StudentListPage.tsx` 与 `frontend/src/components/StudentFormModal.tsx` 清理重复逻辑与无用状态。
- [ ] T032 [Polish] 在 `specs/003-switch-antd-components/design.md` 回填实际实现差异与验收结果摘要。
- [ ] T033 [Polish] 执行范围守卫检查：确认未引入新增业务能力、未改动后端契约。

---

## 依赖关系与执行顺序

### 阶段依赖关系
- 阶段 1（设置）可立即开始。
- 阶段 2（基础）依赖阶段 1 完成，阻塞所有用户故事。
- 阶段 3/4/5（US1/US2/US3）均依赖阶段 2；建议按 P1 -> P2 -> P3 交付。
- 阶段 6（完善）依赖所有用户故事完成。

### 用户故事依赖关系
- **US1 (P1)**: 无业务前置故事依赖，是 MVP。
- **US2 (P2)**: 依赖 US1 提供统一主流程控件风格。
- **US3 (P3)**: 可在 US1 后进行，增强边界场景一致性。

### 故事内执行顺序
- 测试任务（TDD） -> 组件改造 -> 服务映射/错误归一 -> 回归验证。

### 并行机会
- 阶段 1 的 `T001/T003` 可并行。
- 阶段 2 的 `T005/T007` 可并行。
- 每个故事的测试任务可并行（如 `T010/T011`、`T017/T018`、`T024/T025`）。
- 各故事中不同文件任务可并行（标记 `[P]`）。

---

## 并行示例: 用户故事 1

```bash
# 并行写测试
T010: frontend/tests/integration/student-list-ui-consistency.test.tsx
T011: frontend/tests/unit/student-list-actions.test.tsx

# 并行改造不同文件
T014: frontend/src/components/StudentFormModal.tsx
T015: frontend/src/services/studentApi.ts
```

## 并行示例: 用户故事 2

```bash
T017: frontend/tests/integration/student-form-validation.test.tsx
T018: frontend/tests/integration/student-form-submit-feedback.test.tsx
```

## 并行示例: 用户故事 3

```bash
T024: frontend/tests/integration/student-list-empty-state.test.tsx
T025: frontend/tests/integration/student-list-error-retry.test.tsx
T028: frontend/src/components/common/
```

---

## 实施策略

### MVP 优先（仅 US1）
1. 完成阶段 1 与阶段 2。
2. 完成 US1（阶段 3）。
3. 进行独立验收后即可先行交付第一版。

### 增量交付
1. US1（主流程一致性）  
2. US2（输入校验与提交反馈一致）  
3. US3（空态与异常一致）  

### 注意事项
- 每个任务必须包含明确文件路径，完成后可直接验证。
- 不实现规范外新增业务能力，避免过度设计。
