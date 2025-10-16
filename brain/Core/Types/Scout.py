from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Set, List
from .Assets import Assets
from .Coin import Coin
from ccxt.base.exchange import Exchange
import ccxt
import ccxt.pro as ccxtpro

class Scout(ABC):
    def __init__(self, exchange_name: str):
        super().__init__()
        self.exchange_name = exchange_name
        self.exchange: Optional[ccxtpro.Exchange] = None
        self._coins: Optional[List[str]] = None
        
    async def initialize(self) -> None:
        """Асинхронная инициализация биржи"""
        self.exchange = getattr(ccxtpro, self.exchange_name)()
        await self.exchange.load_markets()
        self._coins = await self.get_intersection_coins()
    
    def get_usdt_pairs(self, include_inactive: bool = False) -> List[str]:
        """
        Получает список монет с USDT-парами.
        
        Returns:
            List[str]: Список базовых монет из USDT-пар
        """
        if not self.exchange:
            raise RuntimeError("Exchange not initialized. Call initialize() first.")
            
        try:
            markets = self.exchange.markets
            coins: Set[str] = set()
            
            for symbol, market_info in markets.items():
                # Фильтруем USDT-пары
                if not symbol.endswith('/USDT'):
                    continue
                
                # Проверяем активность если нужно
                if not include_inactive and not market_info.get('active', True):
                    continue
                
                base_coin = symbol.split('/')[0]
                coins.add(base_coin)
            
            return sorted(list(coins))
            
        except Exception as e:
            print(f"Ошибка при получении USDT-пар: {e}")
            return []
    
    async def get_intersection_coins(self) -> List[str]:
        """
        Получает пересечение монет из базы данных и доступных на бирже.
        
        Returns:
            List[str]: Список общих монет
        """
        try:
            coin_names = set(Coin.get_all_coin_names())
            exchange_coins = set(self.get_usdt_pairs())
            
            intersection = coin_names.intersection(exchange_coins)
            print(f"✅ Найдено {len(intersection)} общих монет")
            
            return sorted(list(intersection))
            
        except Exception as e:
            print(f"Ошибка при поиске пересечения монет: {e}")
            return []
    
    @property
    def coins(self) -> List[str]:
        """Геттер для coins с проверкой инициализации"""
        if self._coins is None:
            raise RuntimeError("Scout not initialized. Call initialize() first.")
        return self._coins
    
    async def close(self) -> None:
        """Закрывает соединение с биржей"""
        if self.exchange:
            await self.exchange.close()
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @abstractmethod
    async def watch_tickers(self, limit: int = 10, params: dict = None) -> AsyncIterator[Assets]:
        """
        Абстрактный метод для отслеживания тикеров.
        
        Args:
            limit: Лимит монет для отслеживания
            params: Дополнительные параметры
            
        Yields:
            Assets: Данные об активах
        """
        pass