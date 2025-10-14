from __future__ import annotations
import asyncio
from kucoin_ws import KuCoinWS
from bitget_ws import BitGetWS
from generic_ws import GenericExchangeWS
from Types.ticker import TickerData
from collections import defaultdict
from Types.base_exchange import BaseExchangeWS
import time
from typing import Dict, List, Any, Set
import shutil

class CryptoMonitor:
    def __init__(self) -> None:
        # Добавлены новые биржи: Pionex, Gate, MEXC, Bybit, OKX
        self.exchanges: Dict[str, BaseExchangeWS] = {
            'kucoin': KuCoinWS(),
            'bitget': BitGetWS(),
            'pionex': GenericExchangeWS('pionex'),
            'gate': GenericExchangeWS('gate'),
            'mexc': GenericExchangeWS('mexc'),
            'bybit': GenericExchangeWS('bybit'),
            'okx': GenericExchangeWS('okx'),
        }
        self.last_updates: Dict[str, Dict[str, TickerData]] = defaultdict(dict)
        self.stats: Dict[str, int] = defaultdict(int)
        self._lock: asyncio.Lock = asyncio.Lock()
        
    async def start_monitoring(self, top_n: int = 100) -> None:
        print(f"Starting monitoring for top {top_n} pairs...")
        # Инициализируем все биржи (получаем их собственные top_symbols)
        for exchange in self.exchanges.values():
            await exchange.initialize(top_n)
            exchange.add_callback(self.handle_ticker)

        # NOTE: не выполняем фильтр по пересечению символов — будем показывать всё, что приходит с бирж.

        # Теперь запускаем polling для каждой биржи
        tasks: List[asyncio.Task] = []
        # Запускаем только те poller'ы, у которых есть exchange_client (инициализация прошла успешно)
        started_exchanges = []
        for name, exchange in self.exchanges.items():
            if getattr(exchange, 'exchange_client', None) is not None and exchange.top_symbols:
                tasks.append(asyncio.create_task(exchange.start_websocket()))
                started_exchanges.append(name)
            else:
                print(f"{exchange.exchange_name}: not started (no client or no symbols)")
        
        display_task = asyncio.create_task(self._display_loop(refresh_interval=1.0))
        tasks.append(display_task)

        # Собираем в gather и ждём, пока не будет отмены (Ctrl-C) или исключения.
        main_gather = asyncio.gather(*tasks)
        try:
            await main_gather
        except asyncio.CancelledError:
            print("Monitoring cancelled (CancelledError). Cancelling child tasks...")
            # отменяем все таски
            for t in tasks:
                t.cancel()
            # ждём их завершения (глубоко)
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        except KeyboardInterrupt:
            print("Monitoring interrupted by user (KeyboardInterrupt). Cancelling child tasks...")
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            # лог ошибки и попытка корректно завершить
            print(f"Monitoring error: {e}. Cancelling tasks...")
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            # при выходе попытаться аккуратно остановить клиентов и закрыть low-level clients
            for exchange in self.exchanges.values():
                try:
                    try:
                        await exchange.stop_websocket()
                    except Exception:
                        pass
                    client = getattr(exchange, 'exchange_client', None)
                    if client is not None:
                        try:
                            await client.close()
                        except Exception:
                            pass
                except Exception:
                    pass
    
    async def handle_ticker(self, ticker: TickerData) -> None:
        async with self._lock:
            self.last_updates[ticker.exchange][ticker.symbol] = ticker
            self.stats[ticker.exchange] += 1
        
        # if sum(self.stats.values()) % 10 == 0:
        #     self.print_stats()

    def print_stats(self) -> None:
        print(f"\n=== Stats at {time.strftime('%H:%M:%S')} ===")
        for exchange, count in self.stats.items():
            print(f"{exchange}: {count} ticks")
        print("=" * 40)
    
    def get_current_prices(self, symbol: str) -> Dict[str, TickerData]:
        prices: Dict[str, TickerData] = {}
        for exchange_name, exchange_data in self.last_updates.items():
            if symbol in exchange_data:
                prices[exchange_name] = exchange_data[symbol]
        return prices
    
    def find_arbitrage_opportunities(self, min_spread_percent: float = 0.5) -> List[Dict[str, Any]]:
        opportunities: List[Dict[str, Any]] = []
        all_symbols = set()
        for exchange_data in self.last_updates.values():
            all_symbols.update(exchange_data.keys())
        
        for symbol in all_symbols:
            prices = self.get_current_prices(symbol)
            if len(prices) >= 2:
                exchanges = list(prices.keys())
                for i in range(len(exchanges)):
                    for j in range(i + 1, len(exchanges)):
                        exch1, exch2 = exchanges[i], exchanges[j]
                        price1 = prices[exch1].ask
                        price2 = prices[exch2].bid
                        if (price1 is not None) and (price2 is not None) and price2 > price1:
                            spread_percent = ((price2 - price1) / price1) * 100 if price1 != 0 else 0.0
                            if spread_percent >= min_spread_percent:
                                opportunities.append({
                                    'symbol': symbol,
                                    'buy_at': exch1,
                                    'sell_at': exch2,
                                    'buy_price': price1,
                                    'sell_price': price2,
                                    'spread_percent': spread_percent
                                })
        return sorted(opportunities, key=lambda x: x['spread_percent'], reverse=True)

    async def _display_loop(self, refresh_interval: float = 1.0) -> None:
        # Показываем все подключённые биржи
        exchanges_to_show: List[str] = list(self.exchanges.keys())

        # Входим в alternate buffer и скрываем курсор, чтобы основной вывод не "убегал" вниз.
        print("\x1b[?1049h\x1b[?25l", end="", flush=True)
        try:
            while True:
                try:
                    async with self._lock:
                        snapshot: Dict[str, Dict[str, TickerData]] = {
                            ex: dict(self.last_updates.get(ex, {})) for ex in exchanges_to_show
                        }

                    # Собираем объединение символов, которые есть в snapshot на любых биржах
                    symbol_sets = [set(snapshot.get(ex, {}).keys()) for ex in exchanges_to_show]
                    common_symbols = set().union(*symbol_sets) if symbol_sets else set()

                    cols, rows = shutil.get_terminal_size((120, 20))
                    # Оставляем место для заголовка/футера — резервируем 6 строк
                    max_rows = max(1, rows - 6)

                    # Фильтруем символы: оставляем только те, у которых max_arb > 0.1%
                    threshold = 0.1
                    symbols_with_arb: List[str] = []
                    arb_map: Dict[str, float] = {}
                    last_map: Dict[str, Dict[str, Any]] = {}

                    for sym in common_symbols:
                        bids = {}
                        asks = {}
                        lasts = {}
                        for ex in exchanges_to_show:
                            t = snapshot.get(ex, {}).get(sym)
                            if t:
                                if t.bid is not None:
                                    bids[ex] = t.bid
                                if t.ask is not None:
                                    asks[ex] = t.ask
                                if t.last is not None:
                                    lasts[ex] = t.last
                        # вычисляем max arb между любыми парами
                        max_arb = 0.0
                        for buy_ex, buy_ask in asks.items():
                            for sell_ex, sell_bid in bids.items():
                                if buy_ex == sell_ex:
                                    continue
                                if buy_ask != 0:
                                    arb = ((sell_bid - buy_ask) / buy_ask) * 100
                                    if arb > max_arb:
                                        max_arb = arb
                        if max_arb > threshold:
                            symbols_with_arb.append(sym)
                            arb_map[sym] = max_arb
                            last_map[sym] = lasts

                    displayed = sorted(symbols_with_arb)[:max_rows]

                    # Перемещаем курсор в начало экрана и очищаем до конца экрана
                    print("\x1b[H\x1b[0J", end="", flush=True)

                    # Заголовок (показываем только last для каждой биржи)
                    header = f"{'Symbol':<15}"
                    for ex in exchanges_to_show:
                        header += f"{ex.capitalize() + ' (last)':^20}"
                    header += f"{'Max Arb %':>12}"
                    print(header)
                    print("-" * min(cols, 110))

                    # Строки (ограниченные по количеству)
                    for sym in displayed:
                        row = f"{sym:<15}"
                        lasts = last_map.get(sym, {})
                        for ex in exchanges_to_show:
                            if ex in lasts:
                                # форматируем last с 8 знаками, можно изменить формат при желании
                                val = lasts[ex]
                                try:
                                    cell = f"{float(val):>20.8f}"
                                except Exception:
                                    cell = f"{str(val):>20}"
                            else:
                                cell = f"{'-':>20}"
                            row += cell
                        row += f"{arb_map.get(sym, 0.0):12.4f}"
                        print(row)

                    # Если символов больше, чем поместилось — покажем подсказку
                    remaining = max(0, len(symbols_with_arb) - len(displayed))
                    if remaining > 0:
                        print(f"... and {remaining} more (terminal height limited)")

                    # Нижняя статистика
                    print("\n" + "-" * min(cols, 110))
                    total_ticks = sum(self.stats.values())
                    print(f"Total ticks: {total_ticks} | " + " | ".join(f"{ex}: {self.stats.get(ex,0)}" for ex in exchanges_to_show))

                    await asyncio.sleep(refresh_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"Display loop error: {e}", flush=True)
                    await asyncio.sleep(refresh_interval)
        finally:
            # Восстанавливаем основной буфер и показываем курсор
            print("\x1b[?25h\x1b[?1049l", end="", flush=True)

# пример запуска
async def main():
    monitor = CryptoMonitor()
    await monitor.start_monitoring(top_n=1000)

if __name__ == "__main__":
    asyncio.run(main())