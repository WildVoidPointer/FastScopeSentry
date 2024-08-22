from .response.BaseResponse import BaseResponse


class ResultUtils:
    @staticmethod
    def success(data):
        return BaseResponse(0, data, "ok")

    @staticmethod
    def fail(code=1, message="fail"):
        return BaseResponse(code, None, message)
