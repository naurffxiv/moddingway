from pydantic import BaseModel


class Mod(BaseModel):
    # This class is meant to demonstrate a response model
    # feel free to modify it for actual purposes as necessary
    modID: str
