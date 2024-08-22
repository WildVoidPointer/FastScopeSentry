from .response import BaseTaskResp, TaskStatusResp, BaseResponse
from typing import Any


class TaskStatusRespController:
    @staticmethod
    def success(task_id, task_name) -> TaskStatusResp:
        return TaskStatusResp(code=0, data=BaseTaskResp(task_id=task_id, task_name=task_name), message="successfully")

    @staticmethod
    def failed() -> TaskStatusResp:
        return TaskStatusResp()


class BaseRespController:
    @staticmethod
    def success(data: Any) -> BaseResponse:
        return BaseResponse(code=0, data=data, message="successfully")

    @staticmethod
    def failed() -> BaseResponse:
        return BaseResponse()
