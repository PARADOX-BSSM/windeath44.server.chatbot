from typing import Any

from pydantic import BaseModel, Field


class CursorResponse(BaseModel):
    values : Any
    hasNext : bool
