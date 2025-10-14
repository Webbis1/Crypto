from abc import ABC, abstractmethod
from .Assets import Assets
from typing import Optional, Dict, Any


class Trader(ABC):
    @abstractmethod
    async def trade(self, selling: Assets, buying: str) -> Optional[Dict[str, Any]]:
        pass