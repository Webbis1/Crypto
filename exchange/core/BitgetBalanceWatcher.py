from typing import Any, Dict, Optional, AsyncIterator, List
import asyncio
import ccxt
import ccxt.pro as ccxtpro
import pprint
from .Types import BalanceMonitor, Assets
import traceback

class BitgetBalanceWatcher(BalanceMonitor):
    def __init__(self, api_key: str, secret: str, password: str):
        self.exchange = ccxtpro.bitget({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'sandbox': False,
        })
        
        self.previous_balance = {}
        self._initialized = False
        
    async def close(self):
        await self.exchange.close()

    async def curent_balance(self) -> List[Assets]:
        return [Assets(currency=currency, amount=info if info else 0.0) for currency, info in (await self.exchange.fetch_balance())['total'].items()]
    
    async def receive_all(self) -> AsyncIterator[Assets]:
        try:            
            while True:
                try:
                    balance_update = await self.exchange.watch_balance()

                    if balance_update is None:
                        print("⚠️ Received empty balance update")
                        continue
                    
                    # Обрабатываем полный баланс
                    if 'total' in balance_update:
                        current_balance = balance_update['total']
                        
                        # Если это первый запуск, просто сохраняем баланс
                        if not self._initialized:
                            self.previous_balance = current_balance.copy()
                            self._initialized = True
                            print("✅ Initial balance snapshot saved")
                            continue
                        
                        # Сравниваем с предыдущим балансом и находим изменения
                        for currency, current_amount in current_balance.items():
                            previous_amount = self.previous_balance.get(currency, 0)
                            
                            # Вычисляем изменение
                            change = current_amount - previous_amount
                            
                            # Отправляем только положительные изменения (пополнения)
                            if change > 0:
                                print(f"🔔 Balance increased: {currency} +{change} (was {previous_amount}, now {current_amount})")
                                yield Assets(currency=currency, amount=change)
                        
                        # Обновляем предыдущий баланс
                        self.previous_balance = current_balance.copy()
                            
                    else:
                        print(f"⚠️ Unexpected balance update format: {balance_update}")
                            
                    
                except Exception as e:
                    print(f"❌ Error in balance watch loop: {e}")
                    print(f"Error type: {type(e)}")
                    traceback.print_exc()
                    await asyncio.sleep(5)
                    
        except Exception as e:
            print(f"❌ Failed to start balance watcher: {e}")
            traceback.print_exc()

    async def __aenter__(self):
        print("Connecting to Bitget exchange...")
        await self.exchange.load_markets()
        
        # Инициализируем начальный баланс
        initial_balance = await self.exchange.fetch_balance()
        if 'total' in initial_balance:
            self.previous_balance = initial_balance['total'].copy()
            self._initialized = True
            print("✅ Initial balance snapshot loaded")
        
        print("Connected to Bitget exchange.")
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()