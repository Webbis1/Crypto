from typing import Any, Dict, Optional, AsyncIterator, List
import asyncio
import ccxt
import ccxt.pro as ccxtpro
import pprint
from .Types import BalanceMonitor, Assets
import traceback

class KuCoinBalanceWatcher(BalanceMonitor):
    def __init__(self, api_key: str, secret: str, password: str):
        self.exchange = ccxtpro.kucoin({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'sandbox': False,
        })
        
        self.previous_balance = {}
        # self._lock = asyncio.Lock()
        
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
                        total_balance = balance_update['total']
                        for currency, amount in total_balance.items():
                            if amount > 0:  # Только ненулевые балансы
                                print(f"🔔 Balance update received: {currency} = {amount}")
                                yield Assets(currency=currency, amount=amount)
                    else:
                        print(f"⚠️ Unexpected balance update format: {balance_update}")
                            
                    
                except Exception as e:
                    print(f"❌ Error in balance watch loop: {e}")
                    print(f"Error type: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    await asyncio.sleep(5)
                    
        except Exception as e:
            print(f"❌ Failed to start balance watcher: {e}")
            import traceback
            traceback.print_exc()

    async def __aenter__(self):
        print("Connecting to KuCoin exchange...")
        await self.exchange.load_markets()
        print("Connected to KuCoin exchange.")
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()