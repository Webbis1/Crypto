import asyncio
from ..Types import Assets, Scout
import logging

class ScoutBybit(Scout):
    async def watch_tickers(self, limit=10, params={}):
        logger = logging.getLogger('scout.bybit')
        
        if self.ccxt_exchange.has['watchTickers']:
            logger.info(f"Starting ticker monitoring for {len(self._coins)} coins")
            
            while True:
                try:
                    symbols = [f"{coin.name}/USDT" for coin in self._coins]
                    
                    chunks = [symbols[i:i+10] for i in range(0, len(symbols), 10)]
                    # if len(chunks) > 1:
                    #     logger.info(f"Split into {len(chunks)} chunks")
                    
                    for chunk in chunks:
                        try:
                            tickers = await self.ccxt_exchange.watch_tickers(chunk, params)
                            
                            for symbol, data in tickers.items():
                                try:
                                    base_currency = symbol.split('/')[0]
                                    coin = self.exchange.get_coin_by_name(base_currency)
                                    ask = float(data.get('ask') or data.get('lastPrice') or 0.0)
                                    
                                    yield Assets(coin, ask)
                                    
                                except Exception as e:
                                    logger.warning(f"Error processing symbol {symbol}: {e}")
                                    continue
                        except Exception as e:
                            logger.error(f"Chunk processing error: {e}")
                            continue
                            
                except asyncio.CancelledError:
                    logger.info("Ticker monitoring cancelled")
                    raise
                except Exception as e:
                    logger.error(f"Ticker monitoring error: {e}")
                    await asyncio.sleep(1)