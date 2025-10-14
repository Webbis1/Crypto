from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, AsyncIterator, List
from .Assets import Assets

class BalanceMonitor(ABC):
    @abstractmethod
    async def curent_balance(self) -> List[Assets]:
        pass
    
    @abstractmethod
    async def receive_all(self) -> AsyncIterator[Assets]:
        pass