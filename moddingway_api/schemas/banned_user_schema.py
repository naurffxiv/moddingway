from pydantic import BaseModel
from typing import Optional


class Banned(BaseModel):
    userID: str
