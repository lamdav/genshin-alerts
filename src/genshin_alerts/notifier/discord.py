import asyncio
import logging
import sys

import discord
from genshin_alerts.model import NotifierInput
from genshin_alerts.notifier.base import Notifier

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


class DiscordNotifier(Notifier):
    def __init__(self, client: discord.Client, token: str, destination: int):
        self.client = client
        self.token = token
        self.destination = destination

    async def start(self):
        asyncio.create_task(self.client.start(self.token, bot=True, reconnect=True))
        logger.info("client started")

    async def shutdown(self):
        await self.client.logout()
        logger.info("client logged out")

    async def ready(self) -> bool:
        return await self.client.is_ready()

    async def notify(self, notifier_input: NotifierInput):
        await self.client.wait_until_ready()

        if notifier_input.method == "channel":
            return await self.notify_by_channel(
                self.destination, notifier_input.message
            )
        raise ValueError(f"unsupported notifier method: {notifier_input.method}")

    async def notify_by_channel(self, channel_id: int, message: str):
        channel = self.client.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"channel not found: {channel_id}")
        await channel.send(message)

    @staticmethod
    def build(**params) -> "DiscordNotifier":
        return DiscordNotifier(**params)
