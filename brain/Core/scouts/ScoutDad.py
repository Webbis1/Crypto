from ..Types import ScoutHead, Scout, Assets, Exchange, Coin
from asyncio import Queue
import asyncio
import ccxt.pro as ccxtpro
from typing import AsyncIterator


class ScoutDad(ScoutHead):
    def __init__(self, scouts: list[tuple['Exchange', 'Scout']]):
        self.scouts: list[tuple['Exchange', 'Scout']] = scouts
        self.queue: Queue[tuple['Exchange', 'Assets']] = Queue()

    async def coin_update(self) -> AsyncIterator[tuple['Exchange', 'Assets']]:
        while True:
            answer = await self.queue.get()
            yield answer
            self.queue.task_done()

    async def start_monitoring(self):
        tasks = []
        for exchange, scout in self.scouts:
            task = asyncio.create_task(self._monitor_scout(exchange, scout))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _monitor_scout(self, exchange: 'Exchange', scout: 'Scout'):
        async with scout:
            async for assets in scout.watch_tickers():
                await self.queue.put((exchange, assets))

    def coin_list(self):
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

                tickers = scout.watch_tickers([coin])
                for symbol, data in tickers.items():
                    try:
                        ask = float(data.get('ask') or 0.0)

                        if (ask != 0.0):
                            result_dict[coin_obj][exchange_obj] = ask

                    except Exception:
                        continue

        return result_dict


    async def __aenter__(self):
        print("Start ScoutDad")
        await self.start_monitoring()
        print("start monitoring")