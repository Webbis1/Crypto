from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, AsyncIterator, List
from .Assets import Assets
from .Coin import Coin
from .Exchange import Exchange

class Scout(ABC):
    @abstractmethod
    async def watch_tickers(self) -> AsyncIterator[Assets]:
        pass
