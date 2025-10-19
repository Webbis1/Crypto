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
        print("🚀 ScoutDad: coin_update started")
        try:
            while True:
                print("⏳ ScoutDad: waiting for queue data...")
                answer = await self.queue.get()
                print(f"📥 ScoutDad: received from queue - {answer[0].name}: {answer[1].currency.name} = {answer[1].amount:.6f}")
                yield answer
                self.queue.task_done()
                print("✅ ScoutDad: queue task done")
        except Exception as e:
            print(f"❌ ScoutDad: coin_update error - {e}")
            raise

    async def start_monitoring(self):
        print(f"🎯 ScoutDad: starting monitoring for {len(self.scouts)} scouts")
        tasks = []
        for exchange, scout in self.scouts:
            print(f"🔧 ScoutDad: creating monitor task for {exchange.name}")
            task = asyncio.create_task(self._monitor_scout(exchange, scout))
            tasks.append(task)
        
        print(f"✅ ScoutDad: all {len(tasks)} monitor tasks created")
        return tasks
        
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _monitor_scout(self, exchange: 'Exchange', scout: 'Scout'):
        print(f"🚀 Starting monitor for {exchange.name} with scout {scout.__class__.__name__}")
        
        try:
            async for assets in scout.watch_tickers():
                print(f"📨 {exchange.name}: Received assets - {assets.currency.name} = {assets.amount:.6f}")
                await self.queue.put((exchange, assets))
                print(f"✅ {exchange.name}: Assets queued successfully")
                
        except asyncio.CancelledError:
            print(f"⏹️  Monitor for {exchange.name} was cancelled")
            raise
            
        except Exception as e:
            print(f"❌ {exchange.name}: Monitor crashed with error: {e}")
            
        finally:
            print(f"🏁 Monitor for {exchange.name} has stopped")

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