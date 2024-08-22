import json
from dataclasses import dataclass


class BaseResponse:
    def __init__(self, code, data, message):
        self.code = code
        self.data = data
        self.message = message

    def __str__(self):
        return json.JSONEncoder(self)
