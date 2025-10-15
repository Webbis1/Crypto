from ..Types import ScoutHead, Scout, Coin
from ScoutBitget import ScoutBitget
from ScoutBybit import ScoutBybit
from ScoutGate import ScoutGate
from ScoutKucoin import ScoutKucoin
from ScoutOkx import ScoutOkx
from asyncio import Queue

'''
Список Scouts'ов
Цикл по списку с async for
Добавление результата в асинхронную очередь
'''

class ScoutDad(ScoutHead):
    def __init__(self, scouts: list[Scout]):
        self.scouts: Scout = scouts
        self.queue = Queue()

    async def coin_update(self):
        



scout_data = ScoutDad()
scout_data.test()