import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
import json
from ..Types import Assets, Scout

class ScoutGate(Scout):
    def __init__(self):
        self.exchange = ccxtpro.gate()
        self.coins = self.get_intersection_coins()

    async def watch_tickers(self, limit=10, params={}):
        if self.exchange.has['watchTickers']:
            while True:
                try:
                    tickers = await self.exchange.watch_tickers(self.coins, params)
                    for symbol, data in tickers.items():
                        try:
                            bid = float(data.get('bid') or 0.0)
                            ask = float(data.get('ask') or 0.0)

                            yield Assets(symbol, ask)
                        except Exception:
                            continue
                except Exception as e:
                    print(e)
                    # stop the loop on exception or leave it commented to retry
                    # raise e
