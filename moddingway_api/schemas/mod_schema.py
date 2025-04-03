from typing import List

from pydantic import BaseModel

from .base_page import BasePage


class Mod(BaseModel):
    # This class is meant to demonstrate a response model
    # feel free to modify it for actual purposes as necessary
    modID: str

class ModPage(BasePage):
    items: List[Mod]
