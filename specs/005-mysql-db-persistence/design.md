---
description: "005 学生与成绩 MySQL 持久化 — 技术方案"
---
# 方案设计

**功能分支**：`feature/SPEC-202604031050/005-mysql-db-persistence`  
**创建日期**：2026-04-03  
**规范**：`/Users/1998hx/Desktop/python-study/specs/005-mysql-db-persistence/spec.md`  
**研究**：阶段 0 结论已内化至 §2 / §5 / §6（原 `temp/research.md` 在计划收尾时由脚本清理）

## 1 概览

本方案将后端当前 **`StudentScoreService` 内存字典实现**替换为 **MySQL 持久化**，保持 **HTTP 路径、请求/响应 JSON、业务规则（学号 0001–9999、乐观锁、成绩 upsert）与 001/002 规范一致**。前端无强制改动。交付物包括：DDL/迁移策略、仓储层或等价抽象、连接配置与 **可复现的本地 Quickstart**（见实施阶段文档化），满足 P1「重启不丢数」、P2「多实例共享同一库」、P3「环境可搭建」。

## 2 技术背景

| 项 | 内容 |
|----|------|
| **语言/版本** | Python 3.11+（与仓库一致） |
| **主要依赖** | FastAPI、Pydantic、**SQLAlchemy 2.0**、**PyMySQL**（经 `mysql+pymysql`）、**Alembic**（迁移） |
| **存储** | MySQL 8.x，`utf8mb4` |
| **测试** | pytest（核心路径：仓储 CRUD、学号分配并发、乐观锁冲突、重启前后集成测试可选） |
| **目标平台** | Linux/macOS 开发机；Docker MySQL 本地联调 |
| **项目类型** | Web：现有 `backend/` + `frontend/` |
| **性能目标** | 与 `001`/`002` 既有 NFR 对齐：迁库后 **95%** 列表/只读查询在同等数据量下不明显变慢；具体 p95 以抽样对比或文档记录（NFR-004） |
| **约束条件** | 章程 **禁止**引入缓存、消息队列、通用重试/熔断、独立监控平台；错误须显式返回，禁止「假成功」 |
| **规模/范围** | 单库单 schema；不实现分库分表、读副本 |

## 3 项目结构

### 文档（本功能）

```
specs/005-mysql-db-persistence/
├── spec.md
├── design.md              # 本文件 — 技术方案
├── checklists/
│   └── requirements.md
└── tasks.md               # 由 /speckit.tasks 生成（非本命令）
```

### 源代码（计划中的后端增量 — 实施时落地）

```
backend/
├── main.py                          # 可选： lifespan 中 engine dispose
├── requirements.txt                 # 增加 sqlalchemy、pymysql、alembic
├── alembic/                         # 版本化 DDL（推荐）
│   ├── env.py
│   └── versions/
└── src/
    ├── db/
    │   ├── session.py               # Engine、SessionLocal、get_session
    │   └── base.py                  # SQLAlchemy Declarative Base
    ├── models/                      # 现有 domain dataclass 可保留；新增 ORM 映射模块或表类
    │   └── orm/                     # 建议：StudentRow、ExamScoreRow（命名示例）
    ├── repositories/                # 建议：StudentRepository、ScoreRepository（封装 SQL）
    └── services/
        └── student_score_service.py # 委托仓储，去除内存 dict
```

## 4 项目架构

### 4.1 系统上下文

```mermaid
graph TB
    subgraph clients [Clients]
        FE[React 前端 localhost:5173]
    end
    subgraph backend [FastAPI backend]
        API[HTTP routes\nstudent_scores / student_query]
        SVC[StudentScoreService]
        REPO[Repositories]
    end
    DB[(MySQL 8)]
    FE --> API --> SVC --> REPO --> DB
```

### 4.2 分层架构

```mermaid
graph LR
    R[API Router] --> Svc[StudentScoreService]
    Svc --> Repo[MySQL Repositories]
    Repo --> ORM[SQLAlchemy ORM / Core]
    ORM --> MySQL[(MySQL)]
```

**要点**：路由层与 DTO 不变；服务层保留校验与 `DomainError` 语义；**唯一替换**为「数据访问从内存 dict 改为 MySQL」。

## 5 核心实体

### 5.1 服务内部实体（逻辑 / 表）

#### 实体：`Student`（持久化学生档案）

**位置**：`students` 表 ↔ 现有 `backend.src.models.student.Student`

**职责**：承载学号、姓名、性别与时间戳；支撑列表、编辑回显、乐观更新。

**字段定义**：

| 字段名 | 类型 | 必填 | 是否新增 | 说明 |
|--------|------|------|----------|------|
| id | BIGINT | ✅ | 库内自增 | 对应 API `student_id` |
| student_no | CHAR(4) | ✅ | 否 | UNIQUE，0001–9999 |
| name | VARCHAR(255) | ✅ | 否 | |
| gender | VARCHAR(16) | ✅ | 否 | `male` / `female` |
| created_at | DATETIME(6) | ✅ | 否 | UTC |
| updated_at | DATETIME(6) | ✅ | 否 | 乐观锁 |

**关键说明**：学号分配逻辑见 §6.1；与内存实现一致地递增用尽时返回 **409**。

#### 实体：`ExamScore`（持久化月考成绩）

**位置**：`exam_scores` 表 ↔ 现有 `backend.src.models.exam_score.ExamScore`

**职责**：`(student_id, month, subject)` 唯一；upsert 更新分数与 `updated_at`。

**字段定义**：

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | BIGINT | ✅ | 自增主键 |
| student_id | BIGINT | ✅ | FK → students.id |
| month | TINYINT | ✅ | 1–12 |
| subject | VARCHAR(32) | ✅ | math/chinese/english |
| score | DECIMAL(5,2) | ✅ | |
| created_at / updated_at | DATETIME(6) | ✅ | |

#### 辅助：`student_no_seq`

**职责**：原子递增学号序列，避免 `MAX+1` 竞态；单行表 `id=1`（详见 `temp/data-model.md` 已并入本设计的 DDL 思考）。

### 5.2 外部依赖

| 名称 | 来源 | 用途 |
|------|------|------|
| MySQL Server | 运维/本地 Docker | 唯一权威持久化 |

## 6 关键功能

### 6.1 关键组件与接口

#### 组件：数据库会话与迁移

**位置**：`backend/src/db/session.py`、 `backend/alembic/`

**职责**：管理连接池生命周期；提供请求级或事务级 `Session`；版本化建表。

**核心逻辑**：

1. 应用读取 `DATABASE_URL`，创建 `engine` 与 `sessionmaker`。
2. 部署/本地首次：`alembic upgrade head` 创建 `students`、`exam_scores`、`student_no_seq`。
3. 禁止在未成功提交事务时向前端返回成功（FR-003）。

**异常处理**：连接失败、超时 → **500** + 既有 `UNKNOWN_ERROR` 或细化 `DATABASE_ERROR`（可选）；**不**做自动重试循环（章程）。

#### 组件：`StudentScoreService`（改造后）

**位置**：`backend/src/services/student_score_service.py`

**职责**：保留公共方法签名：`create_student`、`update_student`、`upsert_score`、`get_edit_form`、`list_students`；内部调用 Repository。

**核心逻辑**：

1. **create_student**：事务内从 `student_no_seq` 取下一值 → 格式化 → 插入 `students`；`next_val>9999` → `ConflictError`。
2. **update_student**：`UPDATE students SET ... WHERE id=:id AND updated_at=:expected`；`rowcount==0` → `ConflictError`（版本冲突）或 `NotFoundError`。
3. **upsert_score**：`INSERT ... ON DUPLICATE KEY UPDATE` 或 先查后插/事务内 select-for-update，二选一以 ORM 表达清晰为准。
4. **list_students / get_edit_form**：SQL 查询 + 排序（id / month, subject）与现行为一致。

**单元测试**：

- 用例1：创建学生后 `student_no` 为 `0001`，第二次为 `0002`。
- 用例2：`updated_at` 不匹配时更新失败 409。

**边界场景**：

- 学号用尽 → 409，`student_no range exhausted` 同类消息。
- 外键：`student_id` 不存在 → 404。

### 6.2 组件依赖关系

`student_scores.py` / `student_query.py` → `StudentScoreService` → `StudentRepository` + `ScoreRepository` → SQLAlchemy `Session` → MySQL。

### 6.3 数据流（创建学生）

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as POST /students
    participant SVC as StudentScoreService
    participant REPO as Repository
    participant DB as MySQL
    FE->>API: name, gender
    REPO->>DB: BEGIN; bump student_no_seq
    REPO->>DB: INSERT students
    REPO->>DB: COMMIT
    API-->>FE: 200 data StudentResponse
```

## 7 API 设计

**本次无不新增路由**；行为补充如下。

### 7.1 列表查询 `student_query.list_students`

**位置**：`backend/src/api/student_query.py`  
**是否新增接口**：否  
**变更**：数据源改为 DB；只读语义与查询参数校验不变。

### 7.2 创建学生 `student_scores.create_student`

**位置**：`backend/src/api/student_scores.py`  
**是否新增接口**：否  
**变更**：写库成功后才返回 200；DB 错误不伪装成功。

### 7.3 其余端点

`PUT /students/{id}`、`POST /scores`、`GET /edit-form` 同上，仅存储后端替换。

**契约引用**：HTTP 细节与错误码模式保持与现实现一致；详见同期生成的契约说明（已内化 FR）。

## 8 宪章合规性检查

| 原则 | 如何满足 |
|------|----------|
| **代码质量** | 仓储层隔离 SQL；Service 保持单一职责；命名与现有模块一致。 |
| **测试标准** | 覆盖学号递增、乐观锁 409、成绩 upsert 唯一键；修复内存实现缺陷时补回归；可选「重启前后」集成测试脚本化。 |
| **用户体验一致性** | 成功/校验错误响应结构不变；仅 DB 挂时用户看到明确失败（501/500 视映射而定），非静默。 |
| **性能预算** | 沿用 001/002 叙述；迁库后做同等数据量抽样对比并记录。 |
| **范围控制 / 禁止过度设计** | 不引入 Redis、MQ、缓存、熔断、重试框架、独立日志表/监控平台；单 MySQL 实例；不修改前端契约。 |

## 9 方案设计 checkList

### 架构

- [x] 高维架构描述清晰
- [x] 组件职责定义清晰
- [x] 组件之间的依赖关系已明确
- [x] 技术选型有合理的论证（见 §2 与阶段 0 研究结论）

### 需求符合度

- [x] 设计满足 FR-001 — FR-005
- [x] 已考虑 NFR-001 — NFR-005
- [x] 可满足 SC-001 — SC-004（依赖实施与测试落地）
- [x] 假设：无内存生产数据迁移；多实例共享同一库

### 技术质量

- [x] 设计遵循分层与既有 FastAPI 模式
- [x] 安全性：连接凭据环境变量；最小权限 DB 账号；不在日志打印密码
- [x] 性能：单库索引合理；无过早优化
- [x] 错误处理：显式 HTTP + DomainError；无假成功
- [x] 未引入章程禁止的复杂机制

### 实施准备度

- [x] 设计细节足以支撑实现（表结构、事务边界、序列表）
- [x] 数据实体完整（§5）
- [x] API 无变更；契约说明已覆盖
- [x] 测试策略覆盖核心路径与边界

### 可维护性

- [x] 可通过 Alembic 演进 schema
- [x] 仓储抽象便于未来换库（非本需求）
- [x] 配置外部化（`DATABASE_URL`）
- [x] **监控/可观测性**：不新增独立监控栈；沿用 `/health` 与应用错误响应（符合禁止过度设计）
- [x] 用户可见行为与现 API 一致

---

**下一步**：执行 `/speckit.tasks` 生成 `tasks.md` 并按切片实施。

## 10 本地联调 Quickstart（FR-004 / P3）

### 前置

- Docker（推荐）或本机 MySQL 8.x；Python 与仓库一致。

### 启动 MySQL（Docker 示例）

```bash
docker run -d --name student-mysql \
  -e MYSQL_ROOT_PASSWORD=devroot \
  -e MYSQL_DATABASE=student_score \
  -e MYSQL_USER=student \
  -e MYSQL_PASSWORD=studentpass \
  -p 3306:3306 \
  mysql:8 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

### 环境变量

```bash
export DATABASE_URL='mysql+pymysql://student:studentpass@127.0.0.1:3306/student_score?charset=utf8mb4'
```

### 依赖与迁移（实施完成后对齐 tasks）

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 最小验收（SC-001）

1. `POST /api/v1/students` 创建学生；可选 `POST .../scores` 录入成绩。  
2. 停止并重启 uvicorn。  
3. `GET /api/v1/students` 与 `GET /api/v1/students/{id}/edit-form` 与重启前一致。

### §10 附录（运维文档索引）

- 逐步排查与常见问题（推荐主文档）：`backend/docs/mysql-setup.md`
- 双进程同库验证（US2）：`MULTI_INSTANCE_VERIFICATION.md`

## 11 性能与迁移说明（NFR-004）

迁库后接口路径与前端契约未变；列表与只读查询在单机联调数据量下与内存实现相比**未引入额外线性扫描以外的架构**。若后续在万级行数下感知变慢，再单独开需求优化索引或查询（当前单库单表，无读副本）。

---

**实施记录**：`tasks.md` 中 T001–T025 已由 `/speckit.implement` 对应落地（依赖代码与文档路径以仓库为准）。
