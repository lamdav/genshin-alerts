import abc
from typing import Iterable

from genshin_alerts.model import GiftEntry


class Fetcher(abc.ABC):
    @abc.abstractmethod
    async def fetch(self) -> Iterable[GiftEntry]:
        pass
