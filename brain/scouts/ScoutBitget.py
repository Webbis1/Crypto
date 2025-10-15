import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
import json
from types import Assets, Scout

class ScoutBitget(Scout):
    async def watchOrderBook(self, exchange, symbol, limit=10, params={}):
        if exchange.has['watchOrderBookForSymbols']:
            while True:
                try:
                    tickers = await exchange.watch_tickers(['BTC/USDT', 'ETH/USDT'], params)
                    for symbol, data in tickers.items():
                        try:
                            bid = float(data.get('bid') or 0.0)
                            ask = float(data.get('ask') or 0.0)

                            yield Assets(symbol, ask)

                            #print('Coin: ' + str(symbol) + ' ASK: ' + str(ask) + ' BID: ' + str(bid))
                        except Exception:
                            continue
                except Exception as e:
                    print(e)
                    # stop the loop on exception or leave it commented to retry
                    # raise e
