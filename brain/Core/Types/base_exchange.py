from __future__ import annotations
from abc import ABC, abstractmethod
import asyncio
from typing import List, Dict, Callable, Any, Awaitable, Tuple
import ccxt.async_support as ccxt_async
from .ticker import TickerData

class BaseExchangeWS(ABC):
    """
    Базовый "poller" для бирж на базе ccxt.async_support.
    Наследники должны реализовать start_websocket (здесь это polling)
    и stop_websocket для остановки.
    """
    def __init__(self, exchange_name: str) -> None:
        self.exchange_name: str = exchange_name
        self.exchange_client: Any = None
        self.callbacks: List[Callable[[TickerData], Awaitable[None]]] = []
        self.top_symbols: List[str] = []
        self._running: bool = False
        self._poll_interval: float = 1.0  # seconds, можно переопределить в наследниках
        
    async def initialize(self, top_n: int = 100) -> List[str]:
        """Инициализация: создаём асинхронный ccxt-клиент, загружаем рынки и выбираем топ символов.
        Если биржа не поддерживается в ccxt.async_support — возвращаем пустой список."""
        # проверяем, поддерживается ли exchange id в ccxt.async_support
        if self.exchange_name not in getattr(ccxt_async, 'exchanges', []):
            print(f"{self.exchange_name}: not available in ccxt.async_support, skipping initialization")
            self.exchange_client = None
            self.top_symbols = []
            return self.top_symbols
        # создаём клиент (ccxt async)
        ExchangeCls = getattr(ccxt_async, self.exchange_name, None)
        if ExchangeCls is None:
            print(f"{self.exchange_name}: exchange class not found in ccxt.async_support, skipping")
            self.exchange_client = None
            self.top_symbols = []
            return self.top_symbols
        try:
            self.exchange_client = ExchangeCls()
        except Exception as e:
            print(f"{self.exchange_name}: failed to create exchange client: {e}")
            self.exchange_client = None
            self.top_symbols = []
            return self.top_symbols
        # попытка загрузить рынки
        try:
            await self.exchange_client.load_markets()
            markets: Dict[str, Any] = getattr(self.exchange_client, 'markets', {}) or {}
        except Exception as e:
            print(f"{self.exchange_name}: error loading markets: {e}")
            # при ошибке загрузки рынков — закрываем клиент и возвращаем пустой список
            try:
                if self.exchange_client:
                    await self.exchange_client.close()
            except Exception:
                pass
            self.exchange_client = None
            self.top_symbols = []
            return self.top_symbols
        
        # собираем пары, заканчивающиеся на /USDT и имеющие объём
        pairs: List[Tuple[str, float]] = []
        for symbol, m in markets.items():
            try:
                if not symbol.endswith('/USDT'):
                    continue
                active = m.get('active', True)
                if not active:
                    continue
                info = m.get('info') or {}
                vol = 0.0
                # пробуем несколько ключей для объёма
                for key in ('quoteVolume', 'baseVolume', 'volume', 'vol'):
                    try:
                        v = info.get(key) if isinstance(info, dict) else None
                        if v is None:
                            v = m.get(key)
                        if v:
                            vol = float(v)
                            break
                    except Exception:
                        continue
                pairs.append((symbol, vol or 0.0))
            except Exception:
                continue
        
        # сортируем по объёму и выбираем top_n
        pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)
        self.top_symbols = [s for s, _ in pairs_sorted[:top_n]]
        print(f"{self.exchange_name}: initialized with {len(self.top_symbols)} symbols (sample: {self.top_symbols[:5]})")
        return self.top_symbols

    def add_callback(self, callback: Callable[[TickerData], Awaitable[None]]) -> None:
        """Добавляем callback для обработки данных"""
        self.callbacks.append(callback)
    
    async def _emit_ticker(self, ticker_data: TickerData) -> None:
        """Отправляем данные всем подписчикам"""
        for callback in list(self.callbacks):
            try:
                await callback(ticker_data)
            except Exception as e:
                print(f"{self.exchange_name} Error in callback: {e}")

    @abstractmethod
    async def start_websocket(self) -> None:
        """Запуск polling цикла (называется start_websocket чтобы совместиться с кодом монитора)"""
        pass

    @abstractmethod
    async def stop_websocket(self) -> None:
        """Остановка polling и закрытие клиента"""
        pass