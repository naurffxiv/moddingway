from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from moddingway.settings import get_settings

settings = get_settings()


class BanForm(BaseModel):
    form_id: Optional[int] = None
    user_id: int
    reason: str
    approval: Optional[bool] = None
    approved_by: Optional[int] = None
    submission_timestamp: datetime
