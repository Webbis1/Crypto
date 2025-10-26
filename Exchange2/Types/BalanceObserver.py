from abc import ABC, abstractmethod
import inspect
import ccxt.pro as ccxtpro


class BalanceObserver(ABC):
    
    class Subscriber:
        async def update_price(self, coin: str, change: float) -> None: ...
        
    def __init__(self, ex: ccxtpro.Exchange):
        self._subscribers: set['BalanceObserver.Subscriber'] = set()
        self.ex: ccxtpro.Exchange = ex
        self._is_running = False
    
    def logging(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")
    
    def subscribe(self, subscriber: Subscriber) -> None:
        method = getattr(subscriber, 'update_price', None)
        if not method or not callable(method):
            raise TypeError("Subscriber must have callable 'update_price'")
        
        if not inspect.iscoroutinefunction(method):
            raise TypeError("'update_price' must be async function")
        
        self._subscribers.add(subscriber)
        self.logging(f"Subscriber added: {subscriber.__class__.__name__}")

    def unsubscribe(self, subscriber: Subscriber) -> None:
        self._subscribers.discard(subscriber)
        self.logging(f"Subscriber removed: {subscriber.__class__.__name__}")

    async def _notify(self, coin: str, change: float) -> None:
        for subscriber in self._subscribers.copy():
            try:
                await subscriber.update_price(coin, change)
            except Exception as e:
                self.logging(f"Error notifying subscriber: {e}")

    @abstractmethod
    async def _observe(self): ...
    
    @abstractmethod
    async def start(self) -> None: ...
    
    @abstractmethod
    async def stop(self) -> None: ...
    
    
    