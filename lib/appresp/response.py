from pydantic import BaseModel
from typing import Any


class BaseResponse(BaseModel):
    code: int = 1
    data: Any | None = None
    message: str = "failed"


class BaseTaskResp(BaseModel):
    task_id: int
    task_name: str


class TaskStatusResp(BaseModel):
    code: int = 1
    data: BaseTaskResp | None = None
    message: str = "failed"

