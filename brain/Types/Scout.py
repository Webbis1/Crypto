from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, AsyncIterator, List
from .Assets import Assets
from .Coin import Coin
from .Exchange import Exchange

class Scout(ABC):
    def get_intersection_coins (self) -> list:
        self.exchange.load_markets()

        return list(set(Coin.get_all_coin_names_by_excange()).intersection(set(self.exchange.markets)))

    @abstractmethod
    async def watch_tickers(self, limit=10, params={}) -> AsyncIterator[Assets]:
        pass
