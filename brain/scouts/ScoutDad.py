from ..Types import ScoutHead, Scout, Assets, Exchange, Coin
from asyncio import Queue
import asyncio
import ccxt.pro as ccxtpro

'''
Список Scouts'ов
Цикл по списку с async for
Добавление результата в асинхронную очередь
'''

class ScoutDad(ScoutHead):
    def __init__(self, scouts: tuple[str, Scout]):
        '''scouts: (имяБиржы, объект Scout)'''

        self.scouts: Scout = scouts
        self.queue: Queue = Queue()

    async def coin_update(self):
        for exchange_name, scout in self.scouts:
            async with scout:
                assets: Assets = await scout.watch_tickers()
                exchange: Exchange = Exchange()
                exchange.set_name(exchange_name)

                yield (exchange, assets)

    async def coin_list(self):
        if (len(Coin.get_all_coin_names()) == 0):
            print('All coin names is empty')

        result_dict = {}

        for coin in Coin.get_all_coin_names():
            coin_obj: Coin = Coin()
            coin_obj.set_name(coin)

            result_dict[coin_obj] = {}

            for exchange_name, scout in self.scouts:
                exchange_obj: Exchange = Exchange()
                exchange_obj.set_name(exchange_name)

                tickers = await scout.watch_tickers([coin])
                for symbol, data in tickers.items():
                    try:
                        ask = float(data.get('ask') or 0.0)

                        if (ask != 0.0):
                            result_dict[coin_obj][exchange_obj] = ask

                    except Exception:
                        continue

        return result_dict
