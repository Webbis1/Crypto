from typing import Dict, List
from .base import BalanceObserver
from .binance import BinanceObserver
from .bybit import BybitObserver
from .okx import OKXObserver
from .gateio import GateIOObserver
from .mexc import MEXCObserver
from .bingx import BingXObserver
from .bitget import BitgetObserver
from .htx import HTXObserver
from .kucoin import KuCoinObserver
from .phemex import PhemexObserver
from .bitfinex import BitfinexObserver

class ExchangeFactory:
    """Фабрика для создания наблюдателей за биржами"""
    
    _observers: Dict[str, type] = {
        'binance': BinanceObserver,
        'bybit': BybitObserver,
        'okx': OKXObserver,
        'gateio': GateIOObserver,
        'mexc': MEXCObserver,
        'bingx': BingXObserver,
        'bitget': BitgetObserver,
        'htx': HTXObserver,
        'kucoin': KuCoinObserver,
        'phemex': PhemexObserver,
        'bitfinex': BitfinexObserver,
    }
    
    @classmethod
    def create_observer(cls, exchange_name: str, api_key: str = "", 
                       secret_key: str = "", passphrase: str = "") -> BalanceObserver:
        """
        Создать наблюдатель для биржи
        """
        exchange_name = exchange_name.lower()
        
        if exchange_name not in cls._observers:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
        
        observer_class = cls._observers[exchange_name]
        
        if exchange_name in ['okx', 'bitget', 'kucoin']:
            return observer_class(api_key, secret_key, passphrase)
        else:
            return observer_class(api_key, secret_key)
    
    @classmethod
    def get_supported_exchanges(cls) -> List[str]:
        return list(cls._observers.keys())

__all__ = [
    'BalanceObserver',
    'ExchangeFactory',
    'BinanceObserver',
    'BybitObserver',
    'OKXObserver',
    'GateIOObserver',
    'MEXCObserver', 
    'BingXObserver',
    'BitgetObserver',
    'HTXObserver',
    'KuCoinObserver',
    'PhemexObserver',
    'BitfinexObserver',
]