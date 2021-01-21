import abc

from genshin_alerts.model import NotifierInput


class Notifier(abc.ABC):
    @abc.abstractmethod
    async def notify(self, notifier_input: NotifierInput):
        pass

    @abc.abstractmethod
    async def start(self):
        pass

    @abc.abstractmethod
    async def shutdown(self):
        pass

    @abc.abstractmethod
    async def ready(self) -> bool:
        pass
