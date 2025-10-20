from ..Types import ScoutHead, Scout, Assets, Exchange, Coin
from asyncio import Queue
import asyncio
from typing import AsyncIterator
import logging


class ScoutDad(ScoutHead):
    def __init__(self, scouts: list[tuple['Exchange', 'Scout']]):
        self.scouts: list[tuple['Exchange', 'Scout']] = scouts
        self.queue: Queue[tuple['Exchange', 'Assets']] = Queue()
        self.logger = logging.getLogger('scout_dad')

    async def coin_update(self) -> AsyncIterator[tuple['Exchange', 'Assets']]:
        self.logger.info("Starting coin updates stream")
        try:
            while True:
                answer = await self.queue.get()
                yield answer
                self.queue.task_done()
        except Exception as e:
            self.logger.error(f"Coin update error: {e}")
            raise

    async def start_monitoring(self):
        self.logger.info(f"Starting monitoring for {len(self.scouts)} scouts")
        tasks = []
        for exchange, scout in self.scouts:
            task = asyncio.create_task(self._monitor_scout(exchange, scout))
            tasks.append(task)
        
        self.logger.info(f"Created {len(tasks)} monitor tasks")
        return tasks

    async def _monitor_scout(self, exchange: 'Exchange', scout: 'Scout'):
        self.logger.info(f"Starting monitor for {exchange.name}")
        
        try:
            async for assets in scout.watch_tickers():
                await self.queue.put((exchange, assets))
                
        except asyncio.CancelledError:
            self.logger.info(f"Monitor for {exchange.name} cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Monitor for {exchange.name} crashed: {e}")
        finally:
            self.logger.info(f"Monitor for {exchange.name} stopped")

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
        self.logger.info("Starting ScoutDad")
        await asyncio.gather(*[scout.__aenter__() for _, scout in self.scouts])
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"ScoutDad context error: {exc_val}")
        self.logger.info("Stopping ScoutDad")
        await asyncio.gather(*[
            scout.__aexit__(exc_type, exc_val, exc_tb) 
            for _, scout in self.scouts
        ], return_exceptions=True)