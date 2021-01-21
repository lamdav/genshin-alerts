import abc
from typing import Any, Iterable

from genshin_alerts.model import GiftEntry


class Extractor(abc.ABC):
    @abc.abstractmethod
    async def extract(self, data: Any) -> Iterable[GiftEntry]:
        pass

    @abc.abstractmethod
    def source(self) -> str:
        pass
