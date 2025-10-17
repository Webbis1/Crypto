from Core.Types import *
from Core.Analyst import Analyst
from Core.Guide import Guide
from tabulate import tabulate
from asyncio import run
import asyncio
from Core.ResponseServer import AsyncResponseServer
from Core.scouts import *


# Добавьте в начало вашего скрипта
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('roi_debug.log'),
        # logging.StreamHandler()
    ]
)

scout_bitget: ScoutBitget = ScoutBitget()
scout_bybit: ScoutBybit = ScoutBybit()
scout_gate: ScoutGate = ScoutGate()
scout_kucoin: ScoutKucoin = ScoutKucoin()
scout_okx: ScoutOkx = ScoutOkx()

scouts_list: list[tuple['Exchange', 'Scout']]= {
    (Exchange('bitget'), scout_bitget),
    (Exchange('bybit'), scout_bybit),
    (Exchange('gate'), scout_gate),
    (Exchange('kucoin'), scout_kucoin),
    (Exchange('okx'), scout_okx)
}

coin_list: list[Coin] = [
    Coin('USDT', 'bep20'),
    Coin('BTC', 'bep20'),
    Coin('BTC', 'erc20'),
    Coin('BTC', 'trc20'),
    Coin('BTC', 'native'),
    
    Coin('ETH', 'erc20'),
    Coin('ETH', 'bep20'),
    Coin('ETH', 'native'),
    
    Coin('BNB', 'bep20'),
    Coin('BNB', 'erc20'),
    Coin('BNB', 'native'),
    
    Coin('SOL', 'native'),
    Coin('SOL', 'bep20'),
    Coin('SOL', 'erc20'),
    
    Coin('XRP', 'native'),
    Coin('XRP', 'bep20'),
    Coin('XRP', 'erc20'),
    
    Coin('ADA', 'native'),
    Coin('ADA', 'bep20'),
    
    Coin('DOT', 'native'),
    Coin('DOT', 'bep20'),
    Coin('DOT', 'erc20'),
    
    Coin('DOGE', 'native'),
    Coin('DOGE', 'bep20'),
    Coin('DOGE', 'erc20'),
    
    Coin('AVAX', 'native'),
    Coin('AVAX', 'bep20'),
    Coin('AVAX', 'erc20'),
    
    Coin('MATIC', 'native'),
    Coin('MATIC', 'erc20'),
    Coin('MATIC', 'bep20'),
    
    Coin('LTC', 'native'),
    Coin('LTC', 'bep20'),
    Coin('LTC', 'erc20'),
    
    Coin('LINK', 'erc20'),
    Coin('LINK', 'bep20'),
    Coin('LINK', 'native'),
    
    Coin('ATOM', 'native'),
    Coin('ATOM', 'bep20'),
    Coin('ATOM', 'erc20'),
    
    Coin('UNI', 'erc20'),
    Coin('UNI', 'bep20'),
    
    Coin('XLM', 'native'),
    Coin('XLM', 'bep20'),
    
    Coin('ALGO', 'native'),
    Coin('ALGO', 'bep20'),
    
    Coin('NEAR', 'native'),
    Coin('NEAR', 'bep20'),
    
    Coin('FTM', 'native'),
    Coin('FTM', 'bep20'),
    
    Coin('ETC', 'native'),
    Coin('ETC', 'bep20'),
    
    Coin('BCH', 'native'),
    Coin('BCH', 'bep20'),
    
    Coin('XMR', 'native'),
    Coin('XMR', 'bep20'),
    
    Coin('EOS', 'native'),
    Coin('EOS', 'bep20'),
    
    Coin('AAVE', 'erc20'),
    Coin('AAVE', 'bep20'),
    
    Coin('MKR', 'erc20'),
    Coin('MKR', 'bep20'),
    
    Coin('COMP', 'erc20'),
    Coin('COMP', 'bep20'),
    
    Coin('YFI', 'erc20'),
    Coin('YFI', 'bep20'),
    
    Coin('SUSHI', 'erc20'),
    Coin('SUSHI', 'bep20'),
    
    Coin('CRV', 'erc20'),
    Coin('CRV', 'bep20'),
    
    Coin('SNX', 'erc20'),
    Coin('SNX', 'bep20'),
    
    Coin('RUNE', 'native'),
    Coin('RUNE', 'bep20'),
    
    Coin('GRT', 'erc20'),
    Coin('GRT', 'bep20'),
    
    Coin('BAT', 'erc20'),
    Coin('BAT', 'bep20'),
    
    Coin('ENJ', 'erc20'),
    Coin('ENJ', 'bep20'),
    
    Coin('MANA', 'erc20'),
    Coin('MANA', 'bep20'),
    
    Coin('SAND', 'erc20'),
    Coin('SAND', 'bep20'),
    
    Coin('AXS', 'erc20'),
    Coin('AXS', 'bep20'),
    
    Coin('CHZ', 'erc20'),
    Coin('CHZ', 'bep20'),
    
    Coin('HBAR', 'native'),
    Coin('HBAR', 'bep20'),
    
    Coin('XTZ', 'native'),
    Coin('XTZ', 'bep20'),
    
    Coin('FIL', 'native'),
    Coin('FIL', 'bep20'),
    
    Coin('THETA', 'native'),
    Coin('THETA', 'bep20'),
    
    Coin('VET', 'native'),
    Coin('VET', 'bep20'),
    
    Coin('ICP', 'native'),
    Coin('ICP', 'bep20'),
    
    Coin('FLOW', 'native'),
    Coin('FLOW', 'bep20'),
    
    Coin('EGLD', 'native'),
    Coin('EGLD', 'bep20'),
    
    Coin('KLAY', 'native'),
    Coin('KLAY', 'bep20'),
    
    Coin('ONE', 'native'),
    Coin('ONE', 'bep20'),
    
    Coin('CELO', 'native'),
    Coin('CELO', 'bep20'),
    
    Coin('IOTA', 'native'),
    Coin('IOTA', 'bep20'),
    
    Coin('ZIL', 'native'),
    Coin('ZIL', 'bep20'),
    
    Coin('WAVES', 'native'),
    Coin('WAVES', 'bep20'),
    
    Coin('NEO', 'native'),
    Coin('NEO', 'bep20'),
    
    Coin('ZEC', 'native'),
    Coin('ZEC', 'bep20'),
    
    Coin('DASH', 'native'),
    Coin('DASH', 'bep20'),
    
    Coin('QTUM', 'native'),
    Coin('QTUM', 'bep20'),
    
    Coin('ONT', 'native'),
    Coin('ONT', 'bep20'),
    
    Coin('SC', 'native'),
    Coin('SC', 'bep20'),
    
    Coin('BTT', 'bep20'),
    Coin('BTT', 'trc20'),
    
    Coin('WIN', 'bep20'),
    Coin('WIN', 'trc20'),
    
    Coin('JST', 'bep20'),
    Coin('JST', 'trc20'),
    
    Coin('SUN', 'trc20'),
    Coin('SUN', 'bep20'),
    
    Coin('ANKR', 'erc20'),
    Coin('ANKR', 'bep20'),
    
    Coin('OCEAN', 'erc20'),
    Coin('OCEAN', 'bep20'),
    
    Coin('BAND', 'erc20'),
    Coin('BAND', 'bep20'),
    
    Coin('OMG', 'erc20'),
    Coin('OMG', 'bep20'),
    
    Coin('ZRX', 'erc20'),
    Coin('ZRX', 'bep20'),
    
    Coin('KAVA', 'native'),
    Coin('KAVA', 'bep20'),
    
    Coin('INJ', 'native'),
    Coin('INJ', 'bep20'),
    
    Coin('ROSE', 'native'),
    Coin('ROSE', 'bep20'),
    
    Coin('IOTX', 'native'),
    Coin('IOTX', 'bep20'),
    
    Coin('AUDIO', 'erc20'),
    Coin('AUDIO', 'bep20'),
    
    Coin('RSR', 'erc20'),
    Coin('RSR', 'bep20'),
    
    Coin('COTI', 'native'),
    Coin('COTI', 'bep20'),
    
    Coin('STMX', 'erc20'),
    Coin('STMX', 'bep20'),
    
    Coin('DODO', 'erc20'),
    Coin('DODO', 'bep20'),
    
    Coin('PERP', 'erc20'),
    Coin('PERP', 'bep20'),
    
    Coin('TRB', 'erc20'),
    Coin('TRB', 'bep20'),
    
    Coin('UMA', 'erc20'),
    Coin('UMA', 'bep20'),
    
    Coin('REN', 'erc20'),
    Coin('REN', 'bep20'),
    
    Coin('KNC', 'erc20'),
    Coin('KNC', 'bep20'),
    
    Coin('REQ', 'erc20'),
    Coin('REQ', 'bep20'),
    
    Coin('ORN', 'erc20'),
    Coin('ORN', 'bep20'),
    
    Coin('TOMO', 'native'),
    Coin('TOMO', 'bep20'),
    
    Coin('DGB', 'native'),
    Coin('DGB', 'bep20'),
    
    Coin('ICX', 'native'),
    Coin('ICX', 'bep20'),
    
    Coin('AR', 'native'),
    Coin('AR', 'bep20'),
    
    Coin('RVN', 'native'),
    Coin('RVN', 'bep20'),
    
    Coin('CELR', 'erc20'),
    Coin('CELR', 'bep20'),
    
    Coin('SKL', 'erc20'),
    Coin('SKL', 'bep20'),
    
    Coin('OGN', 'erc20'),
    Coin('OGN', 'bep20'),
    
    Coin('CVC', 'erc20'),
    Coin('CVC', 'bep20'),
    
    Coin('STORJ', 'erc20'),
    Coin('STORJ', 'bep20'),
    
    Coin('DATA', 'erc20'),
    Coin('DATA', 'bep20'),
    
    Coin('ANT', 'erc20'),
    Coin('ANT', 'bep20'),
    
    Coin('MIR', 'erc20'),
    Coin('MIR', 'bep20'),
    
    Coin('TRU', 'erc20'),
    Coin('TRU', 'bep20'),
    
    Coin('DENT', 'erc20'),
    Coin('DENT', 'bep20'),
    
    Coin('HOT', 'erc20'),
    Coin('HOT', 'bep20'),
    
    Coin('VTHO', 'erc20'),
    Coin('VTHO', 'bep20'),
    
    Coin('MTL', 'erc20'),
    Coin('MTL', 'bep20'),
    
    Coin('KEY', 'erc20'),
    Coin('KEY', 'bep20'),
    
    Coin('NKN', 'erc20'),
    Coin('NKN', 'bep20'),
    
    Coin('RLC', 'erc20'),
    Coin('RLC', 'bep20'),
    
    Coin('POLY', 'erc20'),
    Coin('POLY', 'bep20'),
    
    Coin('DIA', 'erc20'),
    Coin('DIA', 'bep20'),
    
    Coin('BEL', 'bep20'),
    Coin('BEL', 'erc20'),
    
    Coin('PSG', 'bep20'),
    Coin('PSG', 'erc20'),
    
    Coin('JUV', 'bep20'),
    Coin('JUV', 'erc20'),
    
    Coin('CITY', 'bep20'),
    Coin('CITY', 'erc20'),
    
    Coin('BAR', 'bep20'),
    Coin('BAR', 'erc20'),
    
    Coin('ATM', 'bep20'),
    Coin('ATM', 'erc20'),
    
    Coin('ASR', 'bep20'),
    Coin('ASR', 'erc20'),
]

coin_count: int = len(coin_list)


sell_commission: dict[Coin, dict[Exchange, float]] = {
    coin: {
        exchange: 0.001 for exchange in Exchange.get_all()
    } for coin in coin_list
}

buy_commission:  dict[Coin, dict[Exchange, float]] = {
    coin: {
        exchange: 0.001 for exchange in Exchange.get_all()
    } for coin in coin_list
}

transfer_commission: dict[Coin, dict[Exchange, dict[Exchange, float]]] = {
    coin: {
        exchange_from: {
            exchange_to: 1.0 for exchange_to in Exchange.get_all() if exchange_to != exchange_from
        } for exchange_from in Exchange.get_all()
    } for coin in coin_list
}

transfer_time: dict[Coin, dict[Exchange, dict[Exchange, float]]] = {
    coin: {
        exchange_from: {
            exchange_to: 5.0 for exchange_to in Exchange.get_all() if exchange_to != exchange_from
        } for exchange_from in Exchange.get_all()
    } for coin in coin_list
}

def print_sell_commission_table(sell_commission: dict[Coin, dict[Exchange, float]]):
    # Собираем все уникальные биржи
    all_exchanges = set()
    for exchanges in sell_commission.values():
        all_exchanges.update(exchanges.keys())
    
    all_exchanges = sorted(all_exchanges, key=lambda x: x.name)
    
    # Создаем таблицу
    table_data = []
    headers = ["Coin"] + [ex.name for ex in all_exchanges]
    
    for coin, exchanges in sell_commission.items():
        row = [coin]
        for exchange in all_exchanges:
            commission = exchanges.get(exchange, "N/A")
            if commission != "N/A":
                commission = f"{commission}$"
            row.append(commission)
        table_data.append(row)
    
    print("\n📊 SELL COMMISSIONS MATRIX")
    print("=" * 100)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


# print_sell_commission_table(sell_commission)


import sys
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

@asynccontextmanager
async def redirect_prints_to_file(filename="app.log", also_to_console=False):
    original_stdout = sys.stdout
    original_print = __builtins__.print
    
    class AsyncLogger:
        def __init__(self):
            self.filename = filename
            self.also_to_console = also_to_console
            self.queue = asyncio.Queue()
            self.worker_task = None
            self.running = False
            self.pending_writes = set()
        
        async def start(self):
            self.running = True
            self.worker_task = asyncio.create_task(self._worker())
        
        async def stop(self):
            """Безопасная остановка с ожиданием завершения всех задач"""
            self.running = False
            
            # Ждем завершения всех pending write задач
            if self.pending_writes:
                print(f"Waiting for {len(self.pending_writes)} pending writes...")
                await asyncio.gather(*self.pending_writes, return_exceptions=True)
            
            # Останавливаем worker
            if self.worker_task:
                await self.queue.put(None)
                await asyncio.wait_for(self.worker_task, timeout=5.0)
        
        async def _worker(self):
            with open(self.filename, 'a', encoding='utf-8') as file:
                while self.running:
                    try:
                        text = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                        if text is None:
                            break
                            
                        if text.strip():
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            file.write(f"[{timestamp}] {text}")
                            file.flush()
                        
                        if self.also_to_console:
                            original_stdout.write(text)
                            original_stdout.flush()
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        original_stdout.write(f"Logger error: {e}\n")
                        original_stdout.flush()
        
        async def write(self, text):
            """Асинхронная запись с отслеживанием задачи"""
            if self.running:
                task = asyncio.create_task(self._safe_write(text))
                self.pending_writes.add(task)
                task.add_done_callback(self.pending_writes.discard)
        
        async def _safe_write(self, text):
            """Безопасная запись в очередь"""
            try:
                await self.queue.put(text)
            except Exception as e:
                if self.also_to_console:
                    original_stdout.write(f"Queue error: {e}\n")
    
    logger = AsyncLogger()
    await logger.start()
    
    # Перехватываем print
    def new_print(*args, **kwargs):
        text = ' '.join(str(arg) for arg in args) + '\n'
        # Создаем задачу для асинхронной записи
        asyncio.create_task(logger.write(text))
        if also_to_console:
            original_stdout.write(text)
            original_stdout.flush()
    
    __builtins__.print = new_print
    
    try:
        yield
    finally:
        # Дожидаемся завершения логгера
        await logger.stop()
        sys.stdout = original_stdout
        __builtins__.print = original_print

import resource

def set_memory_limit(limit_mb=1024):
    """Установка лимита памяти в MB"""
    try:
        # Конвертируем в байты
        limit_bytes = limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
        print(f"Memory limit set to {limit_mb} MB")
    except (ValueError, resource.error) as e:
        print(f"Could not set memory limit: {e}")

 
 
async def main():
    try:
        async with redirect_prints_to_file("server.log") as log_ctx:
            print("Before ScoutDad context")
            async with ScoutDad(scouts_list) as scout_head:
                print(f"Inside ScoutDad context, scout_head: {scout_head}")
                print(f"ScoutDad type: {type(scout_head)}")
                
                guide = Guide(sell_commission=sell_commission, buy_commission=buy_commission, 
                            transfer_commission=transfer_commission, transfer_time=transfer_time)
                # print(f"Guide created: {guide}")
                
                print("Before Analyst context")
                try:
                    async with Analyst(scout=scout_head, guide=guide) as analyst:
                        print("Analyst is ready")
                        # ... остальной код
                except ValueError as e:
                    print(f"Analyst failed: {e}")
                    print(f"At time of failure, scout_head: {scout_head}")
                    raise
                    server = AsyncResponseServer(analyst)
                    await server.start_async_server()
    except KeyboardInterrupt:
        print("Received interrupt, shutting down...")
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program finished")