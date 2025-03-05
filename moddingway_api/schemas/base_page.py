from pydantic import BaseModel


class BasePage(BaseModel):
    total: int
    page: int
    size: int
    pages: int
