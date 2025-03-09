from pydantic import BaseModel


class User(BaseModel):
    # This class is meant to demonstrate a response model
    # feel free to modify it for actual purposes as necessary
    userID: str
    isMod: bool
    strikePoints: int
