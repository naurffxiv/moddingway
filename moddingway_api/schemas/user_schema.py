from typing import List

from pydantic import BaseModel

from .base_page import BasePage


class User(BaseModel):
    # This class is meant to demonstrate a response model
    # feel free to modify it for actual purposes as necessary
    userID: str
    isMod: bool
    strikePoints: int


class UserPage(BasePage):
    items: List[User]
