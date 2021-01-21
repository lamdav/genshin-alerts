import asyncio
import pathlib

import click
import discord
import structlog
from genshin_alerts.config import Config, NotifierEnum
from genshin_alerts.driver import Driver
from genshin_alerts.extractor import GenshiINExtractor
from genshin_alerts.fetcher import GenshinGiftCodeFetcher
from genshin_alerts.notifier import DiscordNotifier

logger = structlog.get_logger()


@click.group()
def cli():
    pass


@click.option("--config", help="path to config", type=click.Path(exists=True, file_okay=True, dir_okay=False), default="./config.yaml")
@cli.command()
def start(config: str):
    config_path = pathlib.Path(config)
    config = Config.load(config_path)

    extractor = GenshiINExtractor()
    fetcher = GenshinGiftCodeFetcher(extractor)
    driver = Driver(fetcher, delay=config.delay)

    for notifier_config in config.notifiers:
        if notifier_config.name is NotifierEnum.discord:
            client = discord.Client()

            @client.event
            async def on_ready():
                logger.info("client is ready", user=client.user)

            @client.event
            async def on_message(message: discord.Message):
                if message.author == client.user:
                    return
                elif not message.content.startswith("!! "):
                    return

                content = message.content.lstrip("!! ")
                if content == "run":
                    if driver is not None:
                        await driver.run()

            driver.add_notifier(DiscordNotifier(client, **notifier_config.params))
        else:
            raise ValueError(f"unsupported notifier {notifier_config.name}")

    loop = asyncio.get_event_loop()
    driver_task = loop.create_task(driver.run(), name="driver")
    try:
        loop.run_forever()
    finally:
        logger.info("shutting down driver")
        loop.run_until_complete(driver.shutdown())
        logger.info("shutdown driver")

        logger.info("stopping loop")
        loop.stop()
        logger.info("stopped loop")


if __name__ == "__main__":
    cli()
