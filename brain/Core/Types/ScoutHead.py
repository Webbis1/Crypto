from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, AsyncIterator, List
from .Assets import Assets
from .Coin import Coin
from .Exchange import Exchange

class ScoutHead(ABC):
    @abstractmethod
    async def coin_update(self) -> AsyncIterator[tuple[Exchange, Assets]]:
        pass

    @abstractmethod
    def coin_list(self) -> Dict[Coin, Dict[Exchange, float]]:
        pass