from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, AsyncIterator, List
from .Assets import Assets
from .Coin import Coin

class ScoutHead(ABC):
    @abstractmethod
    async def coin_update(self) -> AsyncIterator[Assets]:
        pass

    @abstractmethod
    async def coin_list(self) -> Dict[str, List[Coin]]:
        pass