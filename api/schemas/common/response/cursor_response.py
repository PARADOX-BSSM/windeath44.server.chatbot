from typing import Any

from pydantic import BaseModel

class CursorResponse(BaseModel):
    values : Any
    hasNext : bool