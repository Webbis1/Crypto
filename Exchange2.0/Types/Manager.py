import asyncio
from asyncio import Condition, Queue
from dataclasses import dataclass
from typing import AsyncGenerator, AsyncContextManager

@dataclass
class Coin:
    _id: int
    name: str
    
    def __int__(self) -> int:
        return self._id
    
    def __hash__(self) -> int:
        return self._id

@dataclass
class Wallet:
    coins: dict[Coin | int, float]

class Trader:
    async def trade(self) -> bool:
        pass
    
class Courier:
    async def  transfer(self) -> bool:
        pass

class Brain:
    async def consultation(self):
        pass

from typing import Callable, Set, Protocol
from collections.abc import Awaitable
import inspect
from abc import ABC, abstractmethod

class BalanceObserver(ABC):
    class Subscriber(Protocol):
        async def update_price(self, coin: Coin | int, change: float) -> None: ...
        
    def __init__(self):
        self._subscribers: Set['BalanceObserver.Subscriber'] = set()
    
    def subscribe(self, subscriber: Subscriber) -> None:
        method = getattr(subscriber, 'update_price', None)
        if not method or not callable(method):
            raise TypeError("Subscriber must have callable 'update_price'")
        
        if not inspect.iscoroutinefunction(method):
            raise TypeError("'update_price' must be async function")
        
        self._subscribers.add(subscriber)

    async def _notify(self, coin: Coin | int, change: float) -> None:
        for subscriber in self._subscribers:
            await subscriber.update_price(coin, change)
    
    @abstractmethod
    async def _observe(self): ...


class Manager:
    def __init__(self, obs: BalanceObserver):
        self.wallet: Wallet
        self.trader: Trader
        self.courier: Courier
        obs.subscribe(self)
        pass
    
    async def update_price(self, coin: Coin | int, change: float) -> None:
            self.wallet[coin] += change
    
    
    # async def start(self):
        