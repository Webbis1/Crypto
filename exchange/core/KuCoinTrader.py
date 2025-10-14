from .Types import Trader, Assets, Destination
import ccxt
import asyncio
import socket
import json
from typing import Optional, Dict, Any


class KuCoinTrader(Trader):
    def __init__(self, api_key: str, secret: str, password: str):
        self.exchange = ccxt.kucoin({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'sandbox': False,
        })

    async def trade(self, selling: Assets, buying: str) -> Optional[Dict[str, Any]]:
        if not selling or not selling.currency or selling.amount <= 0:
            print(f"❌ Invalid selling asset: {selling}")
            return None
        if not buying or not isinstance(buying, str):
            print(f"❌ Invalid buying currency: {buying}")
            return None

        loop = asyncio.get_running_loop()

        try:
            await loop.run_in_executor(None, self.exchange.load_markets)
            print(f"✅ Markets loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load markets: {e}")
            return None

        # Определяем направление торговли
        if buying.upper() == 'USDT':
            symbol = f"{selling.currency.upper()}/USDT"
            side = 'sell'
            amount = selling.amount  # Количество продаваемой валюты
            print(f"🔄 Selling {amount} {selling.currency} for USDT")
        elif selling.currency.upper() == 'USDT':
            symbol = f"{buying.upper()}/USDT" 
            side = 'buy'
            # Для покупки нужно рассчитать количество на основе суммы USDT
            # Это сложно для market ордера, используем упрощенный подход
            ticker = await loop.run_in_executor(None, lambda: self.exchange.fetch_ticker(symbol))
            current_price = ticker['last']
            amount = selling.amount / current_price  # Примерное количество
            print(f"🔄 Buying {buying} with {selling.amount} USDT (~{amount:.6f} {buying})")
        else:
            symbol = f"{selling.currency.upper()}/{buying.upper()}"
            side = 'sell'
            amount = selling.amount
            print(f"🔄 Trading {amount} {selling.currency} for {buying}")

        if symbol not in self.exchange.symbols:
            print(f"❌ Trading pair not found: {symbol}")
            return None

        print(f"🎯 Creating market {side} order: {amount} {symbol}")

        try:
            order = await loop.run_in_executor(
                None,
                lambda: self.exchange.create_order(symbol, 'market', side, amount)
            )
            print(f"✅ Order created successfully: {order['id']}")
            return order
        except Exception as e:
            print(f"❌ Failed to create order: {e}")
            return None