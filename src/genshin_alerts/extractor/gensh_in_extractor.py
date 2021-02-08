import itertools
from typing import Iterable, Any, Generator, List

import structlog
import validators
from bs4 import BeautifulSoup
from genshin_alerts.extractor.base import Extractor
from genshin_alerts.model import GiftEntry


logger = structlog.get_logger()


class GenshiINExtractor(Extractor):
    def __init__(self, url: str = "https://www.gensh.in/events/promotion-codes"):
        validators.url(url)
        self.url = url

    async def extract(self, data: Any) -> Iterable[GiftEntry]:
        if not isinstance(data, str):
            raise ValueError(
                f"Gensh.in Extractor does not support extracting from non-string sources: {type(data)}"
            )

        data: str
        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table")
        headers = [header.text.strip().lower() for header in table.find_all("th")]
        columns = [column.text.strip() for column in table.find_all("td")]

        gift_entries = []
        for chunk in self.n_chunks(
            zip(itertools.cycle(headers), columns), len(headers)
        ):
            chunk_dict = dict(chunk)
            try:
                expired = chunk_dict.get("expired", None)
                if expired is not None:
                    expired = "yes" in expired.lower()
                else:
                    expired = False
                chunk_dict["expired"] = expired
                gift_entry = GiftEntry(**chunk_dict)
                gift_entries.append(gift_entry)
            except Exception as e:
                logger.exception("failed to parse entry", **chunk_dict)

        return gift_entries

    def source(self) -> str:
        return self.url

    @staticmethod
    def n_chunks(
        iterator: Iterable[Any], chunk_size
    ) -> Generator[List[Any], None, None]:
        buffer = [None] * chunk_size
        for i, data in enumerate(iterator):
            index = i % chunk_size
            if i > 0 and index == 0:
                yield buffer
            buffer[index] = data
