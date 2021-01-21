import enum
import pathlib
from typing import List, Any, Dict

import yaml
from pydantic import BaseModel


class NotifierEnum(str, enum.Enum):
    discord = "discord"


class NotifierConfig(BaseModel):
    name: NotifierEnum
    params: Dict[str, Any]


class Config(BaseModel):
    notifiers: List[NotifierConfig]
    delay: int

    @staticmethod
    def load(path: pathlib.Path) -> "Config":
        with path.open("rb") as f:
            args = yaml.safe_load(f)
        return Config(**args)
