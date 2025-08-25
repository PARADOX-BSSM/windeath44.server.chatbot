from typing import Optional

from pydantic import BaseModel, Field


class CursorQuery(BaseModel):
    cursor_id: Optional[int] = Field(None, alias="cursorId")
    size : Optional[int] = Field(10)