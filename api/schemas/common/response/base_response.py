from typing import Any

from pydantic import BaseModel

class BaseResponse(BaseModel):
    message : str = "undefined response message"
    data : Any = None