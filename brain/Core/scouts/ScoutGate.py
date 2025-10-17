from typing import List, Dict, Any, AsyncIterator
import ccxt
from ..Types import Assets, Scout

class ScoutGate(Scout):
    def __init__(self):
        super().__init__('gateio') 

    async def watch_tickers(self, limit: int = 10, params: Dict[str, Any] = {}) -> AsyncIterator[Assets]:
        if self.exchange.has['watchTickers']:
            while True:
                try:
                    tickers = await self.exchange.watch_tickers(self.coins, params)
                    for symbol, data in tickers.items():
                        try:
                            bid = float(data.get('bid') or 0.0)
                            ask = float(data.get('ask') or 0.0)
                            yield Assets(symbol, ask)
                        except (ValueError, TypeError) as e:
                            continue
                except Exception as e:
                    print(f"Watch tickers error: {e}")