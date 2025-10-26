import asyncio
from asyncio import Condition, Queue
from dataclasses import dataclass
from collections import defaultdict
from typing import AsyncGenerator, AsyncContextManager
from bidict import bidict
import ccxt
import ccxt.pro as ccxtpro
from typing import Optional, Dict, Any
from pprint import pprint  
import logging

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
    # 
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange: ccxt.Exchange = exchange
        self._closed = False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def close(self):
        """Явное закрытие соединений"""
        if not self._closed and self.exchange:
            try:
                await self.exchange.close()
                self._closed = True
                logger.info("Соединения биржи закрыты")
            except Exception as e:
                logger.error(f"Ошибка при закрытии биржи: {e}")
    
    def __del__(self):
        if not self._closed:
            logger.warning("Courier удален без закрытия!")
    async def trade(self, buing_coin:str, selling_coin:str, quantity:float) -> bool:
        pass
    
    
class Port:
    async def get_deposit_adress(ex_name:str, coin_name, chain_name:str) -> str:
        pass    

class Courier:
    def __init__(self, exchange: ccxt.Exchange, port: Port):
        self.exchange: ccxt.Exchange = exchange
        self.port = port
        self._closed = False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_deposit_address(self, coin: str, network: str = None) -> tuple[bool, dict[str, Any]]:
        try:
            params = {'network': network, 'chain': network} if network else {}
            address_info = await self.exchange.fetchDepositAddress(coin, params)
            return True, address_info
        except ccxt.BadRequest as e:
            logger.error(f"Неверный запрос для {coin} в сети {network}: {e}")
            try:
                currencies = await self.exchange.fetch_currencies()
                if coin in currencies:
                    available_networks = list(currencies[coin])
                    print(available_networks)
                    # logger.info(f"Доступные сети для {coin}: {available_networks}")
                    return False, {'error': f'Сеть {network} не поддерживается. Доступные сети: {available_networks}'}
            except:
                pass
            return False, {'error': f'Сеть {network} не поддерживается для {coin}'}
        except ccxt.BaseError as e:
            logger.error(f"Ошибка ccxt при получении адреса {coin}: {e}")
            return False, {'error': str(e)}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении адреса {coin}: {e}")
            return False, {'error': str(e)}
    
    async def transfer(self, address: str, coin_name: str, chain_name: str, quantity: float) -> bool:
        try:
            result = await self.exchange.withdraw(
                code=coin_name,
                amount=quantity,
                address=address,
                params={'chain': chain_name.lower()}
            )
            return result and 'id' in result
        except Exception as e:
            print(f"Transfer error: {e}")
            return False
        
    
    async def close(self):
        """Явное закрытие соединений"""
        if not self._closed and self.exchange:
            try:
                await self.exchange.close()
                self._closed = True
                logger.info("Соединения биржи закрыты")
            except Exception as e:
                logger.error(f"Ошибка при закрытии биржи: {e}")
    
    def __del__(self):
        if not self._closed:
            logger.warning("Courier удален без закрытия!")

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
    def __init__(self, obs: BalanceObserver, coins: bidict[str, int], chains: dict[int, str], commissions:dict[int, float]):
        self._coins: bidict[str, int] = coins
        self.chains: dict[int, str] = chains
        self.commissions: dict[int, float] = commissions
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



# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ExFactory(ex_name: str, sandbox: bool = False) -> Optional[ccxt.Exchange]:
    try:
        if ex_name not in ccxt.exchanges:
            logger.error(f"Биржа {ex_name} не поддерживается в ccxt")
            return None
        
        if ex_name not in api_keys:
            logger.error(f"API ключи для биржи {ex_name} не найдены в конфиге")
            return None
        
        config = api_keys[ex_name]
        
        if 'api_key' not in config or 'api_secret' not in config:
            logger.error(f"Отсутствуют обязательные API ключи для биржи {ex_name}")
            return None
        
        # Создаем базовую конфигурацию
        exchange_config: Dict[str, Any] = {
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'sandbox': sandbox,
            'enableRateLimit': True,
        }
        
        optional_params = ['password', 'uid', 'privateKey', 'walletAddress']
        for param in optional_params:
            if param in config and config[param]:
                exchange_config[param] = config[param]
        
        exchange_class = getattr(ccxtpro, ex_name)
        ccxt_exchange = exchange_class(exchange_config)
        
        logger.info(f"Успешно создан экземпляр биржи {ex_name} (sandbox: {sandbox})")
        return ccxt_exchange
        
    except AttributeError as e:
        logger.error(f"Биржа {ex_name} не найдена в ccxtpro: {e}")
        return None
    except KeyError as e:
        logger.error(f"Ошибка в конфигурации для биржи {ex_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании биржи {ex_name}: {e}")
        return None
    
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
    # test = TestSubscriber(obs)
    # await obs.start()
    
        # Ждем 30 секунд
    # await asyncio.sleep(30)
    
    # Останавливаем
    # await obs.stop()
    # async with Courier(ExFactory("bitget")) as cura:
    #     adress = await cura.get_deposit_address("USDT", 'BEP20')
    #     pprint(adress)
    async with Courier(ExFactory("kucoin")) as cura:
        adress = await cura.get_deposit_address("USDT", 'optimism')
        # adress = await cura.get_deposit_address("USDT", 'BEP20')
        pprint(adress)
    # async with Courier(ExFactory("gate")) as cura:
    #     adress = await cura.get_deposit_address("USDT", 'BEP20')
    #     pprint(adress)
    
if __name__ == "__main__":
    asyncio.run(main())