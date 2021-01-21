from pydantic import BaseModel


class GiftEntry(BaseModel):
    rewards: str
    expired: bool
    eu: str
    na: str
    sea: str
