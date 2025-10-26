import ccxtpro
from .base import BalanceObserver

class GateIOObserver(BalanceObserver):
    def __init__(self, api_key: str = "", secret_key: str = ""):
        super().__init__()
        self.api_key = api_key
        self.secret_key = secret_key
        self.exchange = ccxtpro.gateio({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
        })
        self._running = False
    
    def _extract_coin_from_symbol(self, symbol: str) -> str:
        """Gate.io: BTC_USDT -> BTC"""
        return self._clean_symbol(symbol)
    
    async def _observe(self) -> None:
        self._running = True
        
        symbols = [f"{coin}/USDT" for coin in self._tracking_coins]
        
        while self._running:
            try:
                ticker = await self.exchange.watch_ticker(symbols)
                symbol = ticker['symbol']
                coin_name = self._extract_coin_from_symbol(symbol)
                
                if self._should_track_coin(coin_name) and 'last' in ticker:
                    change = float(ticker['last'])
                    await self._notify(coin_name, change)
                    
            except Exception as e:
                print(f"Gate.io observation error: {e}")
                await asyncio.sleep(5)
    
    async def stop(self) -> None:
        self._running = False
        await self.exchange.close()