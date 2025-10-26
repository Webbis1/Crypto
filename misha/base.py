from abc import ABC, abstractmethod
from typing import Set, List, Protocol
import inspect
import asyncio

class BalanceObserver(ABC):
    class Subscriber(Protocol):
        async def update_price(self, coin: str, change: float) -> None: ...
        
    def __init__(self):
        self._subscribers: Set['BalanceObserver.Subscriber'] = set()
        self._tracking_coins: List[str] = []
    
    def subscribe(self, subscriber: Subscriber) -> None:
        method = getattr(subscriber, 'update_price', None)
        if not method or not callable(method):
            raise TypeError("Subscriber must have callable 'update_price'")
        
        if not inspect.iscoroutinefunction(method):
            raise TypeError("'update_price' must be async function")
        
        self._subscribers.add(subscriber)

    async def _notify(self, coin: str, change: float) -> None:
        for subscriber in self._subscribers:
            await subscriber.update_price(coin, change)
    
    def set_tracking_coins(self, coins: List[str]) -> None:
        """Установить список монет для отслеживания (просто строки)"""
        self._tracking_coins = coins
    
    def _should_track_coin(self, coin_symbol: str) -> bool:
        """Проверить, нужно ли отслеживать эту монету"""
        # Базовая реализация - проверяем по точному совпадению
        clean_symbol = self._clean_symbol(coin_symbol)
        return clean_symbol in self._tracking_coins
    
    def _clean_symbol(self, symbol: str) -> str:
        """Очистить символ от пар и суффиксов биржи"""
        # Базовая реализация - убираем USDT и разделители
        symbol = symbol.upper()
        for pair in ['USDT', '/USDT', '_USDT', '-USDT']:
            symbol = symbol.replace(pair, '')
        symbol = symbol.replace('/', '').replace('_', '').replace('-', '')
        return symbol
    
    @abstractmethod
    def _extract_coin_from_symbol(self, symbol: str) -> str:
        """Извлечь чистый символ монеты из символа биржи"""
        pass
    
    @abstractmethod
    async def _observe(self) -> None:
        """Основной метод наблюдения за биржей"""
        pass
    
    async def start(self) -> None:
        """Запуск наблюдения"""
        await self._observe()
    
    async def stop(self) -> None:
        """Остановка наблюдения"""
        pass