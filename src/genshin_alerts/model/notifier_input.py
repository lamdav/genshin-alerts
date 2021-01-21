from pydantic import BaseModel


class NotifierInput(BaseModel):
    method: str
    message: str
