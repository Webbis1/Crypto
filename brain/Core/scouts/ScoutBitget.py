import asyncio
from ..Types import Assets, Scout, Coin
import logging

class ScoutBitget(Scout):        
    async def watch_tickers(self, limit=10, params={}):
        logger = logging.getLogger('scout.bitget')
        
        if self.ccxt_exchange.has['watchTickers']:
            logger.info(f"Starting ticker monitoring for {len(self._coins)} coins")
            
            try:
                while True:
                    try:
                        symbols = [f"{coin.name}/USDT" for coin in self._coins]
                        tickers = await self.ccxt_exchange.watch_tickers(symbols, params)
                        
                        for symbol, data in tickers.items():
                            try:
                                base_currency = symbol.split('/')[0]
                                coin: Coin = self.exchange.get_coin_by_name(base_currency)
                                ask = float(data.get('ask') or data.get('lastPrice') or 0.0)
                                
                                yield Assets(coin, ask)
                                
                            except Exception as e:
                                logger.warning(f"Error processing symbol {symbol}: {e}")
                                continue
                    except Exception as e:
                        logger.error(f"Ticker monitoring error: {e}")
                        
            except asyncio.CancelledError:
                logger.info("Ticker monitoring cancelled")
                raise