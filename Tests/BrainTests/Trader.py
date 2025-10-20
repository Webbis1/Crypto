import ccxt
from Tests.BrainTests.Wallet import Wallet
from exchange.core.Types import Assets
from exchange.core.Types.Trader import Trader
from typing import Optional, Any
# from Wallet import Wallet

class TraderTester(Trader):
    def __init__(self, wallet: Wallet, exchange_name: str):
        self.wallet = wallet
        self.exchange = getattr(ccxt, exchange_name)()

    
    async def trade(self, selling: Assets, buying: str) -> Optional[dict[str, Any]]:
        pass
    
    
    async def get_exchange_rate(self, coin_a: str, coin_b: str) -> float:
        ticker = await self.exchange.fetch_ticker(f'{coin_a}/{coin_b}')
        return ticker['last']
    
    
tr = TraderTester(Wallet({}), "okx")



print(tr.get_exchange_rate("USDT", "BTC"))
    