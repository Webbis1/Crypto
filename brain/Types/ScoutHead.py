from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, AsyncIterator, List
from .Assets import Assets


class ScoutHead(ABC):
    @abstractmethod
    async def coin_update(self) -> AsyncIterator[Assets]:
        pass
