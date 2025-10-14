from abc import ABC, abstractmethod
from .Assets import Assets
from .Destination import Destination


class Courier(ABC):
    @abstractmethod
    async def transfer(self, departure:str, celling: Assets, destination: Destination):
        pass