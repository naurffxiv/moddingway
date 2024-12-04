from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from moddingway.settings import get_settings
from moddingway.enums import StrikeSeverity

settings = get_settings()


class Strike(BaseModel):
    strike_id: Optional[int] = None
    user_id: int
    severity: StrikeSeverity
    reason: str
    created_timestamp: datetime
    created_by: str
    last_edited_timestamp: datetime
    last_edited_by: str
