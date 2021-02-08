import asyncio
from typing import Iterable, Optional

import structlog
from genshin_alerts.fetcher import Fetcher
from genshin_alerts.model import NotifierInput
from genshin_alerts.notifier import Notifier

logger = structlog.get_logger()


class Driver(object):
    def __init__(
        self,
        fetcher: Fetcher,
        notifiers: Optional[Iterable[Notifier]] = None,
        delay: int = 10,
    ):
        self.fetcher = fetcher
        self.notifiers = notifiers if notifiers is not None else []
        self.delay = delay

    async def shutdown(self):
        for notifier in self.notifiers:
            await notifier.shutdown()

    def add_notifier(self, notifier: Notifier):
        self.notifiers.append(notifier)

    async def run(self):
        if len(self.notifiers) == 0:
            raise ValueError("no notifiers provided")

        for notifier in self.notifiers:
            await notifier.start()

        logger.info("waiting for notifiers to be ready")
        ready = False
        while ready:
            ready = True
            for notifier in self.notifiers:
                ready = ready and await notifier.ready()

        logger.info("driver initialized")
        while True:
            gift_entries = await self.fetcher.fetch()
            gift_entries = [
                gift_entry for gift_entry in gift_entries if not gift_entry.expired
            ]
            if len(gift_entries) == 0:
                logger.info("no gift codes available")
                return

            line_details = [
                f"{gift_entry.rewards}: NA: **{gift_entry.na}** EU: **{gift_entry.eu}** SEA: **{gift_entry.sea}**"
                for gift_entry in gift_entries
            ]
            line_details = "\n- ".join(line_details)
            message = f"Redeem Gift Code here: https://genshin.mihoyo.com/en/gift\n- {line_details}"

            logger.info("sending message to notifiers")
            tasks = []
            for notifier in self.notifiers:
                task = asyncio.create_task(
                    notifier.notify(NotifierInput(method="channel", message=message))
                )
                tasks.append(task)
            await asyncio.gather(*tasks)
            logger.info("sent messages to all notifiers")

            logger.info(f"sleeping", duration=self.delay)
            await asyncio.sleep(self.delay)
