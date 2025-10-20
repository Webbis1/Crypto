from exchange.core.Types import Assets
from exchange.core.Types.Destination import Destination
from .Wallet import Wallet
from ...exchange.core.Types.Courier import Courier as cor
import asyncio


class Courier(cor):
    def __init__(self, wallet: Wallet):
        self.wallet: Wallet
        
    async def transfer(self, departure:int, celling: Assets, destination: int):
        if self.wallet[departure][celling.currency] < celling.amount:
            return False
        if self.wallet[destination][1] < 1:
            return False
        
        #вот здесь еще должна быть проверка на мин сумму
        
        
        #вот здесь должна быть проверка на возможность переведа между биржей а и биржей б
        
         
        self.wallet[departure][celling.currency] -= celling.amount
        asyncio.sleep(7)
        self.wallet[destination][celling.currency] += celling.amount #TODO: поправить определение комиссии 
        self.wallet[destination][1] -= 1 #вычли комисссию из usdt