import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
import json
from ..Types import Assets, Scout

class ScoutBybit(Scout):
    async def watch_tickers(self, exchange, symbol, limit=10, params={}):
        if exchange.has['watchTickers']:
            while (True):
                try:
                    tickers = await exchange.watch_tickers([symbol], params)
                    for symbol, data in tickers.items():
                        try:
                            bid = float(data.get('bid') or 0.0)
                            ask = float(data.get('ask') or 0.0)
                            last_price = float(data.get('lastPrice') or 0.0)

                            if (bid != 0.0 and ask != 0.0):
                                yield Assets(symbol, ask)
                            else:
                                yield Assets(symbol, last_price)

                        except Exception:
                            continue
                except Exception as e:
                    print(e)
                    # stop the loop on exception or leave it commented to retry
                    # raise e
