# ScoutOkx.py
import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
import json
from typing import AsyncIterator
from ..Types import Assets, Scout, Coin
# ScoutOkx.py
class ScoutOkx(Scout):        
    async def watch_tickers(self, limit=10, params={}) -> AsyncIterator[Assets]:
        print(f"OKX: starting with {len(self._coins)} coins")
        if self.ccxt_exchange.has['watchTickers']:
            while True:
                try:
                    symbols = [f"{coin.name}/USDT" for coin in self._coins]
                    tickers = await self.ccxt_exchange.watch_tickers(symbols, params)
                    print(f"OKX: received {len(tickers)} tickers")
                    
                    for symbol, data in tickers.items():
                        try:
                            base_currency = symbol.split('/')[0]
                            coin: Coin = self.exchange.get_coin_by_name(base_currency)
                            ask = float(data.get('ask') or data.get('lastPrice') or 0.0)
                            
                            yield Assets(coin, ask)
                            print(f"OKX: yielded {coin.name} = {ask:.6f}")
                            
                        except Exception:
                            continue
                except Exception as e:
                    print(f"OKX: {e}")