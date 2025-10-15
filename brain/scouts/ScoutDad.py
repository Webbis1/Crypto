from ..Types import ScoutHead, Scout, Assets, Exchange
from asyncio import Queue

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
                exchange.name = exchange_name

                yield (exchange, assets)


scout_data = ScoutDad()
scout_data.test()