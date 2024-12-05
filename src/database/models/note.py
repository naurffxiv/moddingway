from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from settings import get_settings

settings = get_settings()


class Note(BaseModel):
    note_id: Optional[int] = None
    user_id: int
    note: str
    created_timestamp: datetime
    created_by: str
    last_edited_timestamp: datetime
    last_edited_by: str
