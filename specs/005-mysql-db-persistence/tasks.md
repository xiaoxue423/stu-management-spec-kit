---
description: "005 MySQL 持久化 — 实现任务"
---

# 任务: 005 学生与成绩数据持久化（MySQL）

**输入**: `/Users/1998hx/Desktop/python-study/specs/005-mysql-db-persistence/design.md`、`spec.md`  
**前置条件**: design.md（必需）、spec.md（用户故事 P1–P3）

**测试**: `spec.md` **NFR-002** 要求关键路径「写入—重启—查询」可脚本化/自动化复现；本列表在 **US1** 阶段包含 **一次轻量可执行验收脚本** 任务，**不**强制先行 TDD 全量单测套件（章程范围内最小增量）。

**组织结构**: 按用户故事分组；路径为仓库内**绝对路径**。

## 格式: `[ID] [P?] [Story] 描述`

- **[P]**: 可并行（不同文件、无未完成的前置依赖）
- **[Story]**: `US1` / `US2` / `US3` 映射至 `spec.md` 中 P1/P2/P3 用户故事
- 描述中含目标文件路径

## 路径约定

- 后端: `/Users/1998hx/Desktop/python-study/backend/src/`
- 规范与运维说明: `/Users/1998hx/Desktop/python-study/specs/005-mysql-db-persistence/`

---

## 阶段 1: 设置（共享基础设施）

**目的**: 依赖与 Alembic 骨架就位，便于后续迁移与 ORM 绑定。

- [ ] **T001** 在 `/Users/1998hx/Desktop/python-study/backend/requirements.txt` 中增加 `SQLAlchemy`、`pymysql`、`alembic`（建议写明确版本约束，与 Python 版本兼容）。
- [ ] **T002** **[P]** 在 `/Users/1998hx/Desktop/python-study/backend/alembic.ini` 中配置 `script_location` 指向 `alembic` 目录、`sqlalchemy.url` 由环境变量覆盖方式与官方惯例一致（不在仓库写死密码）。
- [ ] **T003** **[P]** 创建 `/Users/1998hx/Desktop/python-study/backend/alembic/env.py`：`target_metadata` 预留为项目 `Base.metadata`；支持 offline/online 迁移。

---

## 阶段 2: 基础（阻塞前置条件）

**目的**: ORM 表模型、会话、首版 DDL 与迁移可执行——**完成前禁止声称任何用户故事已交付**。

**⚠️ 关键**: 阶段 3 起依赖此处产出的表结构与 `Session` 工厂。

- [ ] **T004** 创建 `/Users/1998hx/Desktop/python-study/backend/src/db/base.py`：导出 SQLAlchemy 2.x `DeclarativeBase`（或等价）作为全局 `Base`。
- [ ] **T005** **[P]** 创建 `/Users/1998hx/Desktop/python-study/backend/src/db/session.py`：从环境变量 **`DATABASE_URL`**（`mysql+pymysql://...`）创建 `engine` 与 `sessionmaker`，暴露 `SessionLocal` 或同类工厂（符合 `design.md` §6.1）。
- [ ] **T006** **[P]** 创建 `/Users/1998hx/Desktop/python-study/backend/src/db/deps.py`：实现 FastAPI 依赖 `get_db()`，`yield` 会话并在请求结束时 **close**；异常时不吞掉导致“假成功提交”（对齐 **FR-003**）。
- [ ] **T007** 创建 ORM 映射模块（推荐单文件 `/Users/1998hx/Desktop/python-study/backend/src/models/orm/tables.py`，或按类拆分至 `backend/src/models/orm/`）：  
  - 表 **`students`**：`id` PK AI、`student_no` CHAR(4) UNIQUE、`name`、`gender`、`created_at`/`updated_at` DATETIME(6)；charset **utf8mb4**。  
  - 表 **`exam_scores`**：与 `design.md` §5 一致；`UNIQUE(student_id, month, subject)`；FK 指向 `students.id`，**ON DELETE RESTRICT**（或等价禁止级联删除）。  
  - 表 **`student_no_seq`**：单行序列表（`design.md` §5.1 辅助实体），用于原子递增学号。
- [ ] **T008** 在 `/Users/1998hx/Desktop/python-study/backend/alembic/versions/` 下添加首条迁移 revision：创建上述三张表、必要索引与约束；**插入** `student_no_seq` 初始行（与 `design.md` 序列表逻辑一致）。
- [ ] **T009** 将 `/Users/1998hx/Desktop/python-study/backend/alembic/env.py` 的 `target_metadata` 绑定到 T007 的 `Base.metadata`；本地执行 `alembic upgrade head` 验证无错误。

**检查点**: 空库可迁移成功；`Session` 可获取；**可进入用户故事阶段**。

---

## 阶段 3: 用户故事 1 — 重启后仍能查看历史数据（优先级: P1）🎯 MVP

**目标**: `StudentScoreService` 全链路读写走 MySQL；**重启 uvicorn 后**列表与编辑回显数据与重启前一致（`spec.md` **SC-001**、`design.md` §10）。

**独立测试**: 按 `design.md` §10「最小验收」：创建学生（及可选成绩）→ 停止并重启后端 → `GET /api/v1/students` 与 `GET /api/v1/students/{id}/edit-form` 与重启前一致；无成绩学生状态一致。

### US1 的验证（NFR-002，轻量脚本）

- [ ] **T010** **[US1]** 新增 `/Users/1998hx/Desktop/python-study/backend/scripts/verify_persistence_smoke.sh`（或同等可执行脚本）：对 `BASE_URL` 调用创建与查询接口并打印关键字段；文档中说明**人工**执行「重启服务」后再跑查询步骤以覆盖 **SC-001**（章程不要求引入复杂自动化框架）。

### US1 的实施

- [ ] **T011** **[P] [US1]** 创建 `/Users/1998hx/Desktop/python-study/backend/src/repositories/student_repository.py`：在**同一事务**内完成学号序列递增（`student_no_seq` + `LAST_INSERT_ID` 或等价原子操作）、格式化 4 位学号、`INSERT` 学生；实现按 `id` 查询、按 `id` 排序列表、`UPDATE ... WHERE id AND updated_at` 乐观锁、`rowcount` 判断；将行映射为现有领域对象 `/Users/1998hx/Desktop/python-study/backend/src/models/student.py` 的 `Student`；学号 **>9999** 时抛出现有 `ConflictError` 语义（与内存实现一致）。
- [ ] **T012** **[P] [US1]** 创建 `/Users/1998hx/Desktop/python-study/backend/src/repositories/score_repository.py`：按 `(student_id, month, subject)` **upsert**（`INSERT ... ON DUPLICATE KEY UPDATE` 或等价）；列表查询按学生、排序与当前 `StudentScoreService.get_edit_form` 行为一致；映射为 `/Users/1998hx/Desktop/python-study/backend/src/models/exam_score.py` 的 `ExamScore`。
- [ ] **T013** **[US1]** 重写 `/Users/1998hx/Desktop/python-study/backend/src/services/student_score_service.py`：**删除**内存 dict/`_student_auto_id` 等；构造函数接收 `Session`（或接收两个 repository 实例，由调用方用当前 `Session` 构造）；保留 **`create_student` / `update_student` / `upsert_score` / `get_edit_form` / `list_students`** 的**对外行为与异常类型**（`DomainError`/`ValidationError`/`NotFoundError`/`ConflictError`）；所有写操作在失败时 **rollback** 且不向前端返回成功（**FR-003**）。
- [ ] **T014** **[US1]** 新增 **`/Users/1998hx/Desktop/python-study/backend/src/services/student_score_service_factory.py`**（或紧邻 service 的工厂函数）：`def get_student_score_service(session: Session) -> StudentScoreService`，集中创建带 repository 的 service，避免路由层重复拼装。
- [ ] **T015** **[US1]** 修改 `/Users/1998hx/Desktop/python-study/backend/src/api/student_scores.py`：移除模块级单例 `service = StudentScoreService()`；每个处理函数使用 `Depends(get_db)` 取得 `session`，通过工厂得到 `StudentScoreService` 再调用；**不得**改变 URL、请求体、成功 JSON 形状。
- [ ] **T016** **[US1]** 修改 `/Users/1998hx/Desktop/python-study/backend/src/api/student_query.py`：列表接口改为通过 `Depends(get_db)` + 同一工厂获取 service 调用 `list_students`；**不得**再依赖 `student_scores.service` 模块级全局变量。
- [ ] **T017** **[US1]** 修改 `/Users/1998hx/Desktop/python-study/backend/main.py`：使用 FastAPI **`lifespan`**（或等价）在应用关闭时 **`engine.dispose()`**（见 `design.md` §3）；**不**在此阶段引入连接重试/熔断。

**检查点**: 完成 **T010–T017** 后，US1 应单独达标：**重启后不丢数**。

---

## 阶段 4: 用户故事 2 — 多实例部署下数据一致（优先级: P2）

**目标**: 多进程共享同一 `DATABASE_URL` 时，任一实例写入后其他实例读到的列表/详情一致；数据库不可用时返回明确错误、**不伪造成功**（`spec.md` US2、`FR-003`）。

**独立测试**: 本地起两个 uvicorn 进程（不同端口）、相同 `DATABASE_URL`；经实例 A `POST` 创建后，实例 B `GET` 列表可见；将 MySQL 停写或断连一次，对写入接口期望 **5xx** 或既有错误结构，响应体不应暗示已保存。

- [ ] **T018** **[US2]** 审查 `/Users/1998hx/Desktop/python-study/backend/src/repositories/*.py` 与 `student_score_service.py`：所有 `commit` 路径仅在成功时返回业务结果；捕获 DBAPI 错误后 **rollback** 并向上抛出，由路由层落入现有 `_raise_unknown` 或映射为 **500** + `UNKNOWN_ERROR`/`DATABASE_ERROR`（择一，保持 JSON `detail.code`/`detail.message` 模式）；**禁止**空 `except` 吞异常。
- [ ] **T019** **[US2]** 在 `/Users/1998hx/Desktop/python-study/specs/005-mysql-db-persistence/design.md` **§10 附录**或单独文件 `MULTI_INSTANCE_VERIFICATION.md`（同目录下）写明：双进程启动命令示例、`DATABASE_URL` 一致性要求、US2 手工验收步骤（满足 **独立测试** 段落）。

**检查点**: US1 行为不退化；US2 错误语义与文档可复现。

---

## 阶段 5: 用户故事 3 — 可追溯的交付与配置（优先级: P3）

**目标**: 新成员可按文档完成建库、迁移、环境变量与最小读写（`spec.md` **FR-004**、**SC-003**）。

**独立测试**: 另一台机器或干净 shell：仅照文档执行至 `alembic upgrade head` 并启动应用，完成一次创建+查询。

- [ ] **T020** **[US3]** 创建 `/Users/1998hx/Desktop/python-study/backend/docs/mysql-setup.md`：从 **Docker 启动 MySQL**、`DATABASE_URL` 样例、`pip install`、`alembic upgrade head`、`uvicorn` 命令到 **SC-001** 核对清单；与 `design.md` §10 保持同步（可一方引用另一方，避免长期漂移）。
- [ ] **T021** **[US3]** 在 **错误场景**下验证可诊断性：错误 `DATABASE_URL` 或 MySQL 未启动时，首次访问写接口或启动阶段的行为与 `mysql-setup.md` **「常见问题」**一致（不出现“200 但无数据”）；按需仅在 `session.py` 或启动日志中增加**一条**不含密码的连接失败说明（**禁止**引入独立日志系统，遵循章程）。

**检查点**: 文档可单独执行通；US3 不依赖 US2 文档外的额外工具。

---

## 阶段 6: 完善与横切关注点

**目的**: 去残留、性能备注、范围守卫。

- [ ] **T022** 全仓库检索并删除 `/Users/1998hx/Desktop/python-study/backend/src/services/student_score_service.py` 及 API 层对内存存储的残留引用；确认无第二套“mock 存储”并行存在。
- [ ] **T023** **[P]** **NFR-004**：在 PR 描述或 `/Users/1998hx/Desktop/python-study/specs/005-mysql-db-persistence/design.md` 末尾增加**简短**迁移前后说明（例如同机器、同数据量下列表接口粗略耗时或定性“无明显劣化”）；**禁止**不要求精确 APM。
- [ ] **T024** **[P]** 核对 `/Users/1998hx/Desktop/python-study/frontend/src/docs/student-api-flow.md`：若后端仅换存储、契约未变，必要时仅追加一句“数据来自 MySQL”；**不**改前端业务代码除非契约变化。
- [ ] **T025** 执行 `/Users/1998hx/Desktop/python-study/specs/005-mysql-db-persistence/spec.md` **范围守卫**自检：无读副本、无分库分表、无审计日志表、无消息队列、无通用重试/熔断/缓存组件。

---

## 依赖关系与执行顺序

### 阶段依赖

- **阶段 1** → 无前置。
- **阶段 2** → 依赖阶段 1；**阻塞**阶段 3–5。
- **阶段 3（US1）** → 依赖阶段 2；为 **MVP**。
- **阶段 4（US2）** → 依赖阶段 3（在稳定读写链路上加固错误与文档）。
- **阶段 5（US3）** → 可与阶段 4 **部分并行**（T020–T021 主要改文档），但建议在 T017 后补齐以避免文档与实现不一致。
- **阶段 6** → 依赖阶段 3 完成；建议在 US2/US3 收尾后做。

### 用户故事依赖

| 故事 | 依赖 |
|------|------|
| **US1 (P1)** | 阶段 2 完成后即可开做 |
| **US2 (P2)** | US1 核心链路可用 |
| **US3 (P3)** | US1 行为稳定后编写文档最省事 |

### 阶段 3 内部顺序

1. **T011、T012** 可并行；完成后 **T013**；再 **T014**；再 **T015、T016**（不同文件，但需同一套工厂/依赖语义，建议同一提交或先 T014 再 T015/T016）；**T017** 可紧随；**T010** 可与实现晚期并行，但须在发布前可运行。

---

## 并行示例

### 阶段 1

```bash
# 可并行：T001 与 T002、T003（不同文件，T003 可与 T002 对齐目录后并行）
```

### 阶段 2

```bash
# 可并行：T004 完成后，T005 与 T006 并行；T007 建议在 T004 后单独做或紧随
```

### 阶段 3（US1）

```bash
# 可并行：T011 student_repository.py 与 T012 score_repository.py
# 随后顺序：T013 → T014 → T015 → T016 → T017；T010 与最后几步可并行开发
```

### 阶段 6

```bash
# 可并行：T023 与 T024
```

---

## 实施策略

### 仅 MVP（仅 US1）

1. 完成阶段 1、2。  
2. 完成阶段 3（**T010–T017**），跑通 **design.md §10** 与 **T010** 脚本中的验收说明。  
3. **停止并演示**：重启后数据仍在。

### 增量交付（推荐）

1. 阶段 1 + 2 → 迁移与 ORM 就绪。  
2. 阶段 3 → **MVP（US1）** 上线标准：**SC-001**。  
3. 阶段 4 → **US2** 生产信心与运维双实例说明。  
4. 阶段 5 → **US3** **SC-003** 文档成功率。  
5. 阶段 6 → 去债与 NFR 收口。

### 多人并行

- 开发者 A：T007、T008、T009  
- 开发者 B（待 T004 后）：T011  
- 开发者 C（待 T004 后）：T012  
- 汇合后单人串 T013–T017 减少冲突。

---

## 任务统计摘要

| 项 | 数量 |
|----|------|
| **总任务数** | 25（T001–T025） |
| **US1** | 8 实施 + 1 验证脚本 ≈ 9 |
| **US2** | 2 |
| **US3** | 2 |
| **设置** | 3 |
| **基础** | 6 |
| **完善** | 4 |
| **[P] 可并行机会** | 阶段 1–2 多处；T011∥T012；T023∥T024 |

### 各故事独立测试标准（摘自 spec）

- **US1**: 录入 → **重启后端** → 列表与详情与重启前一致（含无成绩学生）。  
- **US2**: 双实例同库写入后互读一致；DB 故障不误报成功。  
- **US3**: 按 `mysql-setup.md` 从零跑通迁移与最小读写。

---

## 注意事项

- 同一文件上的修改**不要**标 **[P]** 与并行冲突（例如 T015 与 T016 可并行，因不同文件）。  
- **禁止**：Redis、MQ、连接池级自动重试循环、熔断、缓存层、独立监控平台、内存存储 fallback。  
- **DATABASE_URL** 与凭据不入 git；示例用占位符。  
