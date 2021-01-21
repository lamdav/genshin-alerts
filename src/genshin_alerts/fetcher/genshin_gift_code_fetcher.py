from typing import Iterable

import httpx
from genshin_alerts.extractor import Extractor
from genshin_alerts.fetcher import Fetcher
from genshin_alerts.model import GiftEntry


class GenshinGiftCodeFetcher(Fetcher):
    def __init__(self, extractor: Extractor):
        self.extractor = extractor

    async def fetch(self) -> Iterable[GiftEntry]:
        async with httpx.AsyncClient() as client:
            client: httpx.AsyncClient
            response = await client.get(self.extractor.source())

        return await self.extractor.extract(response.text)

