from __future__ import annotations

from datetime import datetime
# 从 Python 内置的 enum 模块中，导入 Enum 枚举类
from enum import Enum

from backend.src.compat import dataclass_with_slots

# 定义一个叫 Gender 的枚举类  这个枚举的值是字符串类型
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass_with_slots
class Student:
    id: int
    student_no: str
    name: str
    gender: Gender
    created_at: datetime
    updated_at: datetime
