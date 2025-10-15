import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
import json
from ..Types import Assets, Scout, Coin

class ScoutKucoin(Scout):
    def __init__(self):
        self.exchange = ccxtpro.kucoin()
        self.coins = list(set(Coin.get_all_coin_names_by_excange()).intersection(set(self.get_exhange_coins_list())))

    def get_exhange_coins_list (self):
        self.exchange.load_markets()

        return self.exchange.markets

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