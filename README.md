# Student Score 项目

本项目是一个前后端分离的学生成绩管理系统：

- 前端位于 `frontend`，负责页面展示与交互。
- 后端位于 `backend`，提供学生与成绩相关 API。

## 技术栈与版本

### 前端（`frontend`）

- Node.js：建议使用 LTS 版本（>= 18）
- React：`^18.3.1`
- React DOM：`^18.3.1`
- Ant Design：`^5.27.6`
- TypeScript：`^5.6.2`
- Vite：`^5.4.8`
- Vitest：`^2.1.9`

### 后端（`backend`）

- Python：建议使用 `3.10+`
- FastAPI：`requirements.txt`（未锁定具体版本）
- Uvicorn：`requirements.txt`（未锁定具体版本）
- SQLAlchemy：`>=2.0,<3`
- PyMySQL：`>=1.1.0`
- Alembic：`>=1.13.0`
- MySQL：`8`（开发文档使用 Docker 镜像 `mysql:8`）

## 启动前准备

在项目根目录执行以下操作：

```bash
cd /Users/1998hx/Desktop/python-study
```

建议先准备 Python 虚拟环境（可选但推荐）：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 后端启动

### 1) 安装依赖

```bash
pip install -r backend/requirements.txt
```

### 2) 启动 MySQL（Docker）

```bash
docker run -d --name student-mysql \
  -e MYSQL_ROOT_PASSWORD=devroot \
  -e MYSQL_DATABASE=student_score \
  -e MYSQL_USER=student \
  -e MYSQL_PASSWORD=studentpass \
  -p 3306:3306 \
  mysql:8 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

### 3) 配置环境变量并执行迁移

```bash
export DATABASE_URL='mysql+pymysql://student:studentpass@127.0.0.1:3306/student_score?charset=utf8mb4'
export PYTHONPATH=.
cd backend && alembic upgrade head && cd ..
```

### 4) 启动后端服务

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

后端启动后可访问健康检查接口：

- `http://127.0.0.1:8000/health`

## 前端启动

另开一个终端，在项目根目录执行：

### 1) 安装依赖

```bash
cd frontend
npm install
```

### 2) 启动开发服务器

```bash
npm run dev
```

默认访问地址：

- `http://127.0.0.1:5173`

前端开发服务器已配置代理，将 `/api` 请求转发到 `http://127.0.0.1:8000`。

## 常用命令

### 前端

```bash
cd frontend
npm run build
npm run test
```

### 后端

```bash
# 在项目根目录
export PYTHONPATH=.
cd backend
alembic upgrade head
```
