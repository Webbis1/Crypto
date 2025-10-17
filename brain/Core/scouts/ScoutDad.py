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
        print("start monitoring")
        tasks = []
        for exchange, scout in self.scouts:
            task = asyncio.create_task(self._monitor_scout(exchange, scout))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _monitor_scout(self, exchange: 'Exchange', scout: 'Scout'):
        async for assets in scout.watch_tickers():
            await self.queue.put((exchange, assets))

    async def coin_list(self) -> dict[Coin, dict[Exchange, float]]:
        result_dict: dict[Coin, dict[Exchange, float]] = {}
        
        for exchange, scout in self.scouts:                
            tickers: list[Assets] = scout.fetch_tickers_once()
            for asset in tickers:
                if asset.currency not in result_dict:
                    result_dict[asset.currency] = {}
                result_dict[asset.currency][exchange] = asset.amount

        return result_dict


    async def __aenter__(self):
        print("Start ScoutDad")
        # Все скауты инициализируются ПАРАЛЛЕЛЬНО
        await asyncio.gather(*[scout.__aenter__() for _, scout in self.scouts])
        return self
        

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Все скауты завершаются ПАРАЛЛЕЛЬНО
        print("rip ded")
        await asyncio.gather(*[
            scout.__aexit__(exc_type, exc_val, exc_tb) 
            for _, scout in self.scouts
        ], return_exceptions=True)  # Игнорируем ошибки при завершении
        # await super().__aexit__(exc_type, exc_val, exc_tb)