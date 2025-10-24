import asyncio
from asyncio import Condition, Queue
from dataclasses import dataclass
from collections import defaultdict
from typing import AsyncGenerator, AsyncContextManager
from bidict import bidict

@dataclass
class Coin:
    _id: int
    _names: dict[str, str] = None
    
    def __init__(self, _id: int, default_name: str):
        self._id = _id
        self._names = {'default': default_name}
        
    def name(self, exchange_name: str = 'default') -> str:
        return self._names.get(exchange_name, self._names['default'])
    
    def __str__(self) -> str:
        return self.name()
    
    def set_name(self, exchange_name: str, name: str):
        self._names[exchange_name] = name
    
    def __int__(self) -> int:
        return self._id
    
    def __hash__(self) -> int:
        return self._id
    

class EX:
    def __init__(self):
        self._coins: dict[str, Coin|int] #coin_name: original coin
    
    

@dataclass
class Wallet:
    _coins: dict[Coin | int, float]
    _names: bidict[str, Coin|int]
    
    def __getitem__(self, coin: Coin|int|str):
        if type(coin) is str:
            coin = self._names[coin]
        return self._coins.get(coin, 0.0)
    
    def __setitem__(self, coin: Coin|int, value: float):
        self._coins[coin] = max(value, 0.0)
      
              
class ExWallet:
    def __init__(self, wallet: Wallet):
        self.wallet: Wallet = wallet
        self._names: bidict[str, Coin|int]
    def __getitem__(self, coin: Coin|int|str):
        if type(coin) is str:
            coin = self._names[coin]
        return self._coins.get(coin, 0.0)

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
    class Subscriber:
        async def update_price(self, coin: str, change: float) -> None: ...
        
    def __init__(self):
        self._subscribers: Set['BalanceObserver.Subscriber'] = set()
    
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


class Manager:
    def __init__(self, obs: BalanceObserver, coins: bidict[str, int]):
        self._coins: bidict[str, int] = coins
        self.wallet: dict[int, float] = {}
        self.trader: Trader
        self.courier: Courier
        
        self.reset_wallet()
        obs.subscribe(self)
        pass
    
    def reset_wallet(self):
        self.wallet = {}
        for _, id in self._coins:
            self.wallet[id] = 0.0
    
    async def update_price(self, coin: Coin | int, change: float) -> None:
            self.wallet[coin] += change
    
    
    # async def start(self):
        
    
import asyncio
from typing import Set, Dict, Any
from abc import ABC, abstractmethod
import inspect
from ccxt import kucoin
import ccxt.pro as ccxtpro
    

class KuCoinBalanceObserver(BalanceObserver):
    def __init__(self, api_key: str, secret: str, password: str, sandbox: bool = False):
        super().__init__()
        self.api_key = api_key
        self.secret = secret
        self.password = password
        self.sandbox = sandbox
        
        self.exchange = ccxtpro.kucoin({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'sandbox': sandbox,
        })
        
        self._current_balances: Dict[str, float] = {}
        self._is_running = False
        
    async def _get_initial_balances(self) -> None:
        """Получаем начальные балансы"""
        try:
            balances = await self.exchange.fetch_balance()
            
            self._current_balances = {}
            for currency, balance in balances['total'].items():
                if balance > 0:
                    self._current_balances[currency] = balance
                    self.logging(f"Initial balance - {currency}: {balance}")
                    
        except Exception as e:
            self.logging(f"Error fetching initial balances: {e}")
            raise

    async def _process_balance_update(self, new_balances: Dict[str, Any]) -> None:
        """Обрабатываем обновление баланса"""
        try:
            for currency, new_balance in new_balances['total'].items():
                old_balance = self._current_balances.get(currency, 0)
                
                if old_balance != new_balance:
                    change = new_balance - old_balance
                    
                    self.logging(f"Balance change - {currency}: {old_balance} -> {new_balance} (change: {change})")
                    
                    self._current_balances[currency] = new_balance
                    
                    # Уведомляем подписчиков
                    coin = currency  # Просто используем строку как coin для теста
                    await self._notify(coin, change)
                        
        except Exception as e:
            self.logging(f"Error processing balance update: {e}")

    async def _observe(self) -> None:
        """Основной метод наблюдения"""
        self._is_running = True
        
        try:
            await self._get_initial_balances()
            self.logging("Starting WebSocket monitoring...")
            
            while self._is_running:
                try:
                    balance_update = await self.exchange.watch_balance()
                    await self._process_balance_update(balance_update)
                    
                except Exception as e:
                    self.logging(f"Error in observation: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            self.logging(f"Fatal error: {e}")
        finally:
            self._is_running = False

    async def start(self) -> None:
        """Запускаем наблюдение"""
        if not self._is_running:
            asyncio.create_task(self._observe())
        else:
            self.logging("Already running")

    async def stop(self) -> None:
        """Останавливаем наблюдение"""
        self._is_running = False
        await self.exchange.close()
        self.logging("Stopped")
        
        

api_keys = {
    'binance': {
        'api_key': 'wMWuRuUvlORTAuRZAbqlmd7r8KIyL2UY2kd0gnNhyPUAxxOOUzXapYRsRZLZ9Auf',
        'api_secret': 'tJatzCwiGPWeulEwR48pkMqf8F5Exfj3FMV6QJFYC1xH9KL0xQU7AO2zScyPWDuT',
    },
    'okx': {
        'api_key': '7a9e7e40-0bc1-458f-b098-a7c8dae5f8c6',
        'api_secret': '74B2A62DE20C5F6415A7E917A3F9B220',
        'password': '@Arr1ess'
    },
    'bitget': {
        'api_key': 'bg_d2f35784890895eb13f84b393f211be5',
        'api_secret': '9be28baff7bde3464c84a3f52330ab123276877c46557a4b311950b6dfc2c0bf',
        'password': 'Ar1essTest'
    },
    'gate': {
        'api_key': '3c161daae69c4add254f58a221b3df3a',
        'api_secret': 'ac93d7767b2e652da91ee959bfce0e1a34873e632c17e1858986ba75e9d55b09',
    },
    'kucoin': {
        'api_key': '68eba1be03ad1c00011b0a37',  
        'api_secret': 'e3d6c2ad-6ac3-4ae7-a605-28b59d937453',
        'password': 'rABSQCS5XR5ubqh'
    },
}

        
obs = KuCoinBalanceObserver(api_keys['kucoin']['api_key'], api_keys['kucoin']['api_secret'], api_keys['kucoin']['password'])


class TestSubscriber:
    def __init__(self, obs: BalanceObserver):
        # self.obs: BalanceObserver = obs
        obs.subscribe(self)
    
    async def update_price(self, coin: Coin | int, change: float) -> None:
            print(f'TestClass: data is update\n Coin - {coin}; Change - {change}')
            




async def main():
    test = TestSubscriber(obs)
    await obs.start()
    
        # Ждем 30 секунд
    await asyncio.sleep(30)
    
    # Останавливаем
    await obs.stop()
    
if __name__ == "__main__":
    asyncio.run(main())