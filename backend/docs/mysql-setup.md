# MySQL 本地与迁移（005 持久化）

与 `specs/005-mysql-db-persistence/design.md` §10 对齐；按本文从零搭建即可跑通读写与 `alembic upgrade head`。

## 1. 启动 MySQL（Docker）

```bash
docker run -d --name student-mysql \
  -e MYSQL_ROOT_PASSWORD=devroot \
  -e MYSQL_DATABASE=student_score \
  -e MYSQL_USER=student \
  -e MYSQL_PASSWORD=studentpass \
  -p 3306:3306 \
  mysql:8 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

## 2. 环境变量

```bash
export DATABASE_URL='mysql+pymysql://student:studentpass@127.0.0.1:3306/student_score?charset=utf8mb4'
```

勿将真实密码提交到 git。

## 3. 安装依赖与迁移

在仓库根目录（`python-study`）：

```bash
pip install -r backend/requirements.txt
export PYTHONPATH=.
cd backend && alembic upgrade head && cd ..
```

## 4. 启动 API

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## 5. SC-001 最小验收

1. `POST /api/v1/students` 创建一名学生（仅姓名+性别）。
2. 可选：`POST /api/v1/students/{id}/scores` 录入成绩。
3. **停止并重启** uvicorn。
4. `GET /api/v1/students` 与 `GET /api/v1/students/{id}/edit-form` 应与重启前一致。

辅助脚本（需服务已启动）：

```bash
BASE_URL=http://127.0.0.1:8000 bash backend/scripts/verify_persistence_smoke.sh
```

## 常见问题

| 现象 | 处理 |
|------|------|
| `DATABASE_URL is not set` | 未 export 环境变量；API 在首次使用数据库时会抛错。 |
| Access denied / 1045 | 检查用户、密码、库名是否与 Docker `-e` 一致。 |
| Can't connect to MySQL | 3306 是否映射、容器是否 `docker ps` 可见。 |
| 部署前未执行 `alembic upgrade head` | 建表失败或接口 500；先完成迁移再启动应用。 |

多实例验证见：`../specs/005-mysql-db-persistence/MULTI_INSTANCE_VERIFICATION.md`。
