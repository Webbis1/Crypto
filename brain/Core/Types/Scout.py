from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Set, List, Any
from .Assets import Assets
from .Exchange import Exchange
from .Coin import Coin
from ccxt.base.exchange import Exchange as ccxt_ex
import ccxt
import ccxt.pro as ccxtpro
import logging

class Scout(ABC):
    def __init__(self, exchange: Exchange):
        super().__init__()
        self.exchange: Exchange = exchange
        self.ccxt_exchange: Optional[ccxtpro.Exchange] = None
        self._coins: Optional[List[Coin]] = None
        self.logger = logging.getLogger(f'scout.{exchange.name}')
        
    async def initialize(self) -> None:
        self.ccxt_exchange = getattr(ccxtpro, self.exchange.name)()
        await self.ccxt_exchange.load_markets()
        self._coins = await self.get_intersection_coins()
        
        self.logger.info(f"Initialized with {len(self._coins)} coins")
    
    def get_usdt_pairs(self, include_inactive: bool = False) -> List[str]:
        if not self.ccxt_exchange:
            raise RuntimeError("Exchange not initialized. Call initialize() first.")
            
        try:
            markets = self.ccxt_exchange.markets
            coins: Set[str] = set()
            
            for symbol, market_info in markets.items():
                if not symbol.endswith('/USDT'):
                    continue
                
                if not include_inactive and not market_info.get('active', True):
                    continue
                
                base_coin = symbol.split('/')[0]
                coins.add(base_coin)
            
            return sorted(list(coins))
            
        except Exception as e:
            self.logger.error(f"Error getting USDT pairs: {e}")
            return []
    
    async def get_intersection_coins(self) -> List[Coin]:
        try:
            exchange_coins = set(self.get_usdt_pairs())
            intersection: List[Coin] = [coin for coin in self.exchange.coins if coin.name in exchange_coins]
            
            self.logger.info(f"Found {len(intersection)} common coins")
            return intersection
            
        except Exception as e:
            self.logger.error(f"Error finding coin intersection: {e}")
            return []
    
    def fetch_tickers_once(self, params: dict[str, Any] = {}) -> List[Assets]:
        if not self.exchange:
            raise RuntimeError("Scout not initialized. Call initialize() first.")
        
        if not self._coins:
            raise RuntimeError("No coins available. Check initialization.")
            
        assets_list: List[Assets] = []
        
        try:
            sync_exchange = getattr(ccxt, self.exchange.name)()
            symbols = [f"{coin.name}/USDT" for coin in self._coins]
            
            tickers: dict[str, Any] = sync_exchange.fetch_tickers(symbols, params)
            
            for symbol, data in tickers.items():
                try:
                    base_currency = symbol.split('/')[0]
                    coin: Coin = self.exchange.get_coin_by_name(base_currency)
                    bid: float = float(data.get('bid') or 0.0)
                    ask: float = float(data.get('ask') or 0.0)
                    
                    price = ask if ask > 0 else bid
                    assets_list.append(Assets(coin, price))
                    
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid data for {symbol}: {e}")
                    continue
                
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error in fetch_tickers_once: {e}")
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error in fetch_tickers_once: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in fetch_tickers_once: {e}")
        finally:
            if 'sync_exchange' in locals():
                try:
                    if hasattr(sync_exchange, 'close'):
                        sync_exchange.close()
                    else:
                        del sync_exchange
                except Exception as e:
                    self.logger.warning(f"Error closing exchange: {e}")
        
        return assets_list
    
    def is_initialized(self) -> bool:
        return self.exchange is not None and self._coins is not None
    
    @property
    def coins(self) -> List[Coin]:
        if self._coins is None:
            raise RuntimeError("Scout not initialized. Call initialize() first.")
        return self._coins
    
    async def close(self) -> None:
        if self.exchange:
            try:
                if hasattr(self.exchange, 'close'):
                    self.exchange.close()
                elif hasattr(self.exchange, '__del__'):
                    self.exchange.__del__()
            except Exception as e:
                self.logger.warning(f"Error closing exchange: {e}")
    
    async def __aenter__(self):
        self.logger.info("Starting scout")
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"Scout context error: {exc_val}")
        await self.close()
        self.logger.info("Scout stopped")

    @abstractmethod
    async def watch_tickers(self, limit: int = 10, params: dict = None) -> AsyncIterator[Assets]:
        pass