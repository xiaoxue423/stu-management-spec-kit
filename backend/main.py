"""
main.py 是 FastAPI 的入口文件，负责启动整个 API 服务。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
# 导入 参数校验失败异常，方便你自己捕获并自定义错误返回
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
# 从 FastAPI 的响应模块里，导入一个叫 JSONResponse 的工具，它专门用来返回标准的 JSON 格式数据给前端
from fastapi.responses import JSONResponse

from backend.src.api.student_query import router as student_query_router
from backend.src.api.student_scores import router as student_router
from backend.src.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    dispose_engine()


app = FastAPI(title="Student Score API", version="0.1.0", lifespan=lifespan)

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 注册路由
app.include_router(student_router)
app.include_router(student_query_router)

# 全局参数校验异常处理
@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": "invalid request parameters",
                "errors": exc.errors(),
            }
        },
    )

# 健康检查接口
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
