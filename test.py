from typing import List, Optional, Set
import ccxt
from pprint import pprint

def get_usdt_pairs_advanced(
    exchange_name: str,
    include_inactive: bool = False
) -> Optional[List[str]]:
    """
    Расширенная версия для получения USDT-пар.
    
    Args:
        exchange_name: Название биржи
        include_inactive: Включать неактивные пары
        
    Returns:
        Список базовых монет из USDT-пар
    """
    try:
        exchange = getattr(ccxt, exchange_name)()
        markets = exchange.load_markets()
        
        coins: Set[str] = set()
        
        for symbol, market_info in markets.items():
            # Фильтруем только USDT-пары
            if not symbol.endswith('/USDT'):
                continue
            
            # Фильтруем по активности если нужно
            if not include_inactive and not market_info.get('active', True):
                continue
            
            base_coin = symbol.split('/')[0]
            coins.add(base_coin)
        
        return sorted(list(coins))
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Использование
coins: Optional[List[str]] = get_usdt_pairs_advanced('binance')

pprint(coins)