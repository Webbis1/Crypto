from __future__ import annotations
import asyncio
import time
from typing import Optional, Dict, Any
from Types.base_exchange import BaseExchangeWS
from Types.ticker import TickerData

class KuCoinWS(BaseExchangeWS):
    def __init__(self, poll_interval: float = 1.0) -> None:
        super().__init__('kucoin')
        self._poll_interval = poll_interval

    async def start_websocket(self) -> None:
        """Polling через ccxt.async_support.fetch_tickers / fetch_ticker"""
        if not self.top_symbols:
            await self.initialize()
        self._running = True

        client = self.exchange_client
        if client is None:
            print("KuCoin: exchange client not available, skipping poller")
            self._running = False
            return

        while self._running:
            try:
                tickers: Dict[str, Any] = {}
                try:
                    if hasattr(client, 'fetch_tickers'):
                        tickers = await client.fetch_tickers(self.top_symbols)
                    else:
                        tickers = {}
                except Exception:
                    tickers = {}

                if tickers:
                    for symbol, data in tickers.items():
                        try:
                            bid = float(data.get('bid') or 0.0)
                            ask = float(data.get('ask') or 0.0)
                            last = float(data.get('last') or data.get('close') or 0.0)
                            vol = float(data.get('quoteVolume') or data.get('baseVolume') or data.get('volume') or 0.0)
                            ts = float(data.get('timestamp') or 0.0) / 1000.0 if data.get('timestamp') else 0.0
                        except Exception:
                            continue

                        ticker = TickerData(
                            symbol=symbol.replace('-', '/'),
                            exchange='kucoin',
                            bid=bid,
                            ask=ask,
                            last=last,
                            volume=vol,
                            timestamp=ts
                        )
                        await self._emit_ticker(ticker)
                else:
                    for symbol in list(self.top_symbols):
                        try:
                            data = await client.fetch_ticker(symbol)
                            bid = float(data.get('bid') or 0.0)
                            ask = float(data.get('ask') or 0.0)
                            last = float(data.get('last') or data.get('close') or 0.0)
                            vol = float(data.get('quoteVolume') or data.get('baseVolume') or data.get('volume') or 0.0)
                            ts = float(data.get('timestamp') or 0.0) / 1000.0 if data.get('timestamp') else 0.0

                            ticker = TickerData(
                                symbol=symbol.replace('-', '/'),
                                exchange='kucoin',
                                bid=bid,
                                ask=ask,
                                last=last,
                                volume=vol,
                                timestamp=ts
                            )
                            await self._emit_ticker(ticker)
                        except Exception:
                            continue

                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"KuCoin poll error: {e}")
                await asyncio.sleep(2.0)

    async def stop_websocket(self) -> None:
        """Остановка polling и закрытие ccxt клиента"""
        self._running = False
        try:
            if self.exchange_client:
                await self.exchange_client.close()
        except Exception as e:
            print(f"KuCoin stop error: {e}")