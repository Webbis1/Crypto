from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Set, List, Any
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
        
        print(f"initialize of {self.exchange_name} complite")
    
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
            print(f"✅ Найдено {len(intersection)} общих монет на {self.exchange_name}")
            
            return sorted(list(intersection))
            
        except Exception as e:
            print(f"Ошибка при поиске пересечения монет: {e}")
            return []
    
    def fetch_tickers_once(self, params: dict[str, Any] = {}) -> List[Assets]:
        """
        Получает тикеры один раз (синхронно).
        
        Returns:
            List[Assets]: Список активов
        """
        if not self.exchange:
            raise RuntimeError("Scout not initialized. Call initialize() first.")
        
        if not self._coins:
            raise RuntimeError("No coins available. Check initialization.")
            
        assets_list: List[Assets] = []
        
        try:
            # Create a sync exchange instance for one-time fetching
            sync_exchange = getattr(ccxt, self.exchange_name)()
            symbols = [f"{coin}/USDT" for coin in self._coins]
            
            tickers: dict[str, Any] = sync_exchange.fetch_tickers(symbols, params)
            
            for symbol, data in tickers.items():
                try:
                    # Extract base currency from symbol (e.g., "BTC/USDT" -> "BTC")
                    base_currency = symbol.split('/')[0]
                    bid: float = float(data.get('bid') or 0.0)
                    ask: float = float(data.get('ask') or 0.0)
                    
                    # Use mid price or handle bid/ask as needed
                    price = ask if ask > 0 else bid
                    assets_list.append(Assets(base_currency, price))
                    
                except (ValueError, TypeError) as e:
                    print(f"Invalid data for {symbol}: {e}")
                    continue
                
        except ccxt.NetworkError as e:
            print(f"Network error in fetch_tickers_once: {e}")
        except ccxt.ExchangeError as e:
            print(f"Exchange error in fetch_tickers_once: {e}")
        except Exception as e:
            print(f"Unexpected error in fetch_tickers_once: {e}")
        finally:
            # Close sync exchange if it exists
            if 'sync_exchange' in locals():
                try:
                    # Проверяем есть ли метод close
                    if hasattr(sync_exchange, 'close'):
                        sync_exchange.close()
                    else:
                        # Для бирж без close() просто удаляем объект
                        del sync_exchange
                except Exception as e:
                    print(f"Ошибка при закрытии биржи: {e}")
        
        return assets_list
    
    def is_initialized(self) -> bool:
        """Проверяет, инициализирован ли скаут"""
        return self.exchange is not None and self._coins is not None
    
    @property
    def coins(self) -> List[str]:
        """Геттер для coins с проверкой инициализации"""
        if self._coins is None:
            raise RuntimeError("Scout not initialized. Call initialize() first.")
        return self._coins
    
    async def close(self) -> None:
        """Закрывает соединение с биржей"""
        if self.exchange:
            try:
                if hasattr(self.exchange, 'close'):
                    self.exchange.close()
                elif hasattr(self.exchange, '__del__'):
                    # Вызываем деструктор если нет close()
                    self.exchange.__del__()
            except Exception as e:
                print(f"Ошибка при закрытии биржи: {e}")
    
    async def __aenter__(self):
        print(f"Scout - {self.exchange_name} runing")
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