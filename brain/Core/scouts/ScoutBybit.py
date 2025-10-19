# ScoutBybit.py
import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
import json
from ..Types import Assets, Scout, Coin

class ScoutBybit(Scout):
    async def watch_tickers(self, limit=10, params={}):
        print(f"Bybit: starting with {len(self._coins)} coins")
        
        if self.ccxt_exchange.has['watchTickers']:
            while True:
                try:
                    symbols = [f"{coin.name}/USDT" for coin in self._coins]
                    
                    # Bybit ограничение - разбиваем на chunks по 10
                    chunks = [symbols[i:i+10] for i in range(0, len(symbols), 10)]
                    if len(chunks) > 1:
                        print(f"Bybit: split into {len(chunks)} chunks")
                    
                    for chunk in chunks:
                        try:
                            tickers = await self.ccxt_exchange.watch_tickers(chunk, params)
                            print(f"Bybit: received {len(tickers)} tickers")
                            
                            for symbol, data in tickers.items():
                                try:
                                    base_currency = symbol.split('/')[0]
                                    coin = self.exchange.get_coin_by_name(base_currency)
                                    ask = float(data.get('ask') or data.get('lastPrice') or 0.0)
                                    
                                    yield Assets(coin, ask)
                                    print(f"Bybit: yielded {coin.name} = {ask:.6f}")
                                    
                                except Exception as e:
                                    print(f"Bybit: error processing {symbol}: {e}")
                                    continue
                        except Exception as e:
                            print(f"Bybit: chunk error: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Bybit: {e}")
                    await asyncio.sleep(1)