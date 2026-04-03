# 多实例验证（US2）

**目的**：确认多个后端进程共用同一 `DATABASE_URL` 时，写入对全部实例可见，且数据库故障时不出现「200 假成功」。

## 前提

- MySQL 已按 `backend/docs/mysql-setup.md` 就绪，`alembic upgrade head` 已执行。
- 两个 shell（或两个终端标签）。

## 步骤

1. **实例 A**（端口 8000）：

   ```bash
   export DATABASE_URL='mysql+pymysql://student:studentpass@127.0.0.1:3306/student_score?charset=utf8mb4'
   export PYTHONPATH=.
   uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```

2. **实例 B**（端口 8001），**相同的** `DATABASE_URL`：

   ```bash
   export DATABASE_URL='mysql+pymysql://student:studentpass@127.0.0.1:3306/student_score?charset=utf8mb4'
   export PYTHONPATH=.
   uvicorn backend.main:app --host 127.0.0.1 --port 8001
   ```

3. 向 **A** 创建学生：

   ```bash
   curl -sS -X POST http://127.0.0.1:8000/api/v1/students \
     -H 'Content-Type: application/json' \
     -d '{"name":"双实例","gender":"male"}'
   ```

4. 在 **B** 上拉列表，应能看到同一学生：

   ```bash
   curl -sS http://127.0.0.1:8001/api/v1/students
   ```

5. **故障语义**（任选）：停止 MySQL 或对实例 A 使用错误 `DATABASE_URL`，对写入接口应返回 **5xx** 且响应体不应声称已成功持久化。

## 说明

- 本仓库未引入读副本、缓存或消息队列；一致性依赖单一 MySQL 实例。
