'''
student_scores.py 是 FastAPI 的路由文件，负责实现学生成绩相关的 API 接口。
“学生模块的 HTTP 路由层（Controller）”，主要负责把前端请求转成后端服务调用，再把结果包装成前端可用的 JSON。
'''
# 允许在类型标注中使用尚未定义的类型名（前向引用），减少类型循环依赖问题。
from __future__ import annotations

# 用于接收前端传入的更新时间字段（ISO 时间字符串 -> datetime）。
from datetime import datetime
# 用于处理分数字段，避免 float 精度误差（例如 89.9）。
from decimal import Decimal

# APIRouter 用于注册路由；HTTPException 用于抛出标准 HTTP 错误响应。
from fastapi import APIRouter, HTTPException
# BaseModel 用于定义请求体模型并自动做参数校验。
from pydantic import BaseModel

# 科目枚举（如语文/数学/英语），用于约束成绩接口的 subject 字段。
from backend.src.models.exam_score import Subject
# 性别枚举，用于约束学生创建/更新接口的 gender 字段。
from backend.src.models.student import Gender
# ScoreResponse：成绩响应 DTO；UpsertScoreRequest：写入成绩的服务层入参 DTO。
from backend.src.schemas.score import ScoreResponse, UpsertScoreRequest
# 学生相关 DTO：创建请求、更新请求、学生响应。
from backend.src.schemas.student import CreateStudentRequest, StudentResponse, UpdateStudentRequest
# DomainError：业务错误；StudentScoreService：封装学生与成绩业务逻辑。
from backend.src.services.student_score_service import DomainError, StudentScoreService

# 定义该模块路由前缀与 Swagger 分组名。
router = APIRouter(prefix="/api/v1/students", tags=["students"])
# 路由层持有一个 service 实例，所有业务动作都委托给它执行。
service = StudentScoreService()
# 查询职责已拆分到 student_query.py 的 GET /api/v1/students，并在该文件处理只读参数校验。


# 创建学生接口的请求体模型：只接收 name 与 gender。
class CreateStudentBody(BaseModel):
    # 学生姓名。
    name: str
    # 学生性别（受 Gender 枚举约束）。
    gender: Gender


# 更新学生接口的请求体模型：除 name/gender 外还要求 updatedAt。
class UpdateStudentBody(BaseModel):
    # 更新后的学生姓名。
    name: str
    # 更新后的学生性别。
    gender: Gender
    # 前端提交的更新时间戳，常用于并发更新校验（乐观锁语义）。
    updatedAt: datetime


# 录入/更新成绩接口的请求体模型。
class UpsertScoreBody(BaseModel):
    # 月份（通常是 1-12，具体范围由服务层校验）。
    month: int
    # 科目（受 Subject 枚举约束）。
    subject: Subject
    # 分数（Decimal 避免精度问题）。
    score: Decimal


# 把业务异常转换为 HTTPException，让前端得到统一错误结构。
def _raise_http(exc: DomainError) -> None:
    # detail 中统一放 code/message，便于前端做错误码分流。
    raise HTTPException(status_code=exc.status_code, detail={"code": exc.error_code, "message": exc.message})


# 把未知异常统一映射为 500，避免暴露内部实现细节。
def _raise_unknown() -> None:
    raise HTTPException(status_code=500, detail={"code": "UNKNOWN_ERROR", "message": "internal server error"})


# POST /api/v1/students：创建学生基础信息。
@router.post("")
def create_student(body: CreateStudentBody) -> dict:
    # 写接口职责：仅负责创建学生基础信息，不承载列表查询逻辑。
    try:
        # 将 API 层请求体映射为服务层 DTO，再交给 service 执行业务。
        student = service.create_student(CreateStudentRequest(name=body.name, gender=body.gender))
        # 返回统一 data 包裹结构，并把领域模型转成响应 DTO。
        return {"data": StudentResponse.from_model(student)}
    # 可预期业务错误：按业务定义的状态码和错误码返回。
    except DomainError as exc:
        _raise_http(exc)
    # 未知错误：统一 500。
    except Exception:
        _raise_unknown()


# PUT /api/v1/students/{student_id}：更新学生基础信息。
@router.put("/{student_id}")
def update_student(student_id: int, body: UpdateStudentBody) -> dict:
    try:
        # 传入路径参数 student_id 与更新 DTO，执行更新。
        student = service.update_student(
            student_id,
            UpdateStudentRequest(
                # name/gender 直接来自请求体。
                name=body.name,
                gender=body.gender,
                # API 字段 updatedAt 映射到服务层字段 updated_at（蛇形命名）。
                updated_at=body.updatedAt,
            ),
        )
        # 返回更新后的学生信息。
        return {"data": StudentResponse.from_model(student)}
    # 业务可预期错误（如学生不存在、并发冲突等）。
    except DomainError as exc:
        _raise_http(exc)
    # 兜底未知错误。
    except Exception:
        _raise_unknown()


# POST /api/v1/students/{student_id}/scores：录入或更新某学生某月某科成绩。
@router.post("/{student_id}/scores")
def upsert_score(student_id: int, body: UpsertScoreBody) -> dict:
    try:
        # upsert 语义：存在则更新，不存在则新增（具体规则在 service）。
        score = service.upsert_score(
            student_id, UpsertScoreRequest(month=body.month, subject=body.subject, score=body.score)
        )
        # 返回成绩响应 DTO。
        return {"data": ScoreResponse.from_model(score)}
    # 业务错误统一映射。
    except DomainError as exc:
        _raise_http(exc)
    # 未知错误统一 500。
    except Exception:
        _raise_unknown()


# GET /api/v1/students/{student_id}/edit-form：一次性返回编辑页所需数据。
@router.get("/{student_id}/edit-form")
def get_edit_form(student_id: int) -> dict:
    try:
        # service 返回编辑表单聚合对象（学生信息 + 成绩列表）。
        edit_form = service.get_edit_form(student_id)
        return {
            "data": {
                # 学生基础信息。
                "student": StudentResponse.from_model(edit_form.student),
                # 成绩列表：逐条映射为响应 DTO。
                "scores": [ScoreResponse.from_model(s) for s in edit_form.scores],
            }
        }
    # 业务错误（如学生不存在）。
    except DomainError as exc:
        _raise_http(exc)
    # 未知错误兜底。
    except Exception:
        _raise_unknown()
