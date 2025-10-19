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





coin_list: list[Coin] = [
    Coin('USDT'),
    Coin('BTC'),
    Coin('ETH'),
    Coin('BNB'),
    Coin('SOL'),
    Coin('XRP'),
    Coin('ADA'),
    Coin('DOT'),
    Coin('DOGE'),
    Coin('AVAX'),
    Coin('MATIC'),
    Coin('LTC'),
    Coin('LINK'),
    Coin('ATOM'),
    Coin('UNI'),
    Coin('XLM'),
    Coin('ALGO'),
    Coin('NEAR'),
    Coin('FTM'),
    Coin('ETC'),
    Coin('BCH'),
    # Coin('XMR'),
    Coin('EOS'),
    Coin('AAVE'),
    Coin('MKR'),
    Coin('COMP'),
    Coin('YFI'),
    Coin('SUSHI'),
    Coin('CRV'),
    Coin('SNX'),
    Coin('RUNE'),
    Coin('GRT'),
    Coin('BAT'),
    Coin('ENJ'),
    Coin('MANA'),
    Coin('SAND'),
    Coin('AXS'),
    Coin('CHZ'),
    Coin('HBAR'),
    Coin('XTZ'),
    Coin('FIL'),
    Coin('THETA'),
    Coin('VET'),
    Coin('ICP'),
    Coin('FLOW'),
    Coin('EGLD'),
    Coin('KLAY'),
    Coin('ONE'),
    Coin('CELO'),
    Coin('IOTA'),
    Coin('ZIL'),
    Coin('WAVES'),
    Coin('NEO'),
    # Coin('ZEC'),
    # Coin('DASH'),
    Coin('QTUM'),
    Coin('ONT'),
    Coin('SC'),
    Coin('BTT'),
    Coin('WIN'),
    Coin('JST'),
    Coin('SUN'),
    Coin('ANKR'),
    Coin('OCEAN'),
    Coin('BAND'),
    Coin('OMG'),
    Coin('ZRX'),
    Coin('KAVA'),
    Coin('INJ'),
    Coin('ROSE'),
    Coin('IOTX'),
    Coin('AUDIO'),
    Coin('RSR'),
    Coin('COTI'),
    Coin('DODO'),
    Coin('PERP'),
    Coin('TRB'),
    Coin('UMA'),
    Coin('REN'),
    Coin('KNC'),
    Coin('REQ'),
    Coin('ORN'),
    Coin('TOMO'),
    Coin('DGB'),
    Coin('ICX'),
    Coin('AR'),
    Coin('RVN'),
    Coin('CELR'),
    Coin('SKL'),
    Coin('OGN'),
    Coin('CVC'),
    Coin('STORJ'),
    Coin('DATA'),
    Coin('ANT'),
    Coin('MIR'),
    Coin('TRU'),
    Coin('DENT'),
    Coin('HOT'),
    Coin('VTHO'),
    Coin('MTL'),
    Coin('NKN'),
    Coin('RLC'),
    Coin('POLY'),
    Coin('DIA'),
    Coin('BEL'),
    Coin('PSG'),
    Coin('JUV'),
    Coin('CITY'),
    Coin('ATM'),
    Coin('ASR'),
]

# Создаем экземпляры Exchange
# Создаем экземпляры Exchange без coins в конструкторе
exchange_bitget = Exchange('bitget')
exchange_bybit = Exchange('bybit')
exchange_gate = Exchange('gate')
exchange_kucoin = Exchange('kucoin')
exchange_okx = Exchange('okx')

# Устанавливаем coins через сеттер (это вызовет deepcopy)
exchange_bitget.coins = coin_list
exchange_bybit.coins = coin_list
exchange_gate.coins = coin_list
exchange_kucoin.coins = coin_list
exchange_okx.coins = coin_list
# Создаем скауты, передавая exchange в конструктор
scout_bitget: ScoutBitget = ScoutBitget(exchange_bitget)
scout_bybit: ScoutBybit = ScoutBybit(exchange_bybit)
scout_gate: ScoutGate = ScoutGate(exchange_gate)
scout_kucoin: ScoutKucoin = ScoutKucoin(exchange_kucoin)
scout_okx: ScoutOkx = ScoutOkx(exchange_okx)

# Список пар (Exchange, Scout)
scouts_list: list[tuple[Exchange, Scout]] = [
    (exchange_bitget, scout_bitget),
    (exchange_bybit, scout_bybit),
    (exchange_gate, scout_gate),
    (exchange_kucoin, scout_kucoin),
    (exchange_okx, scout_okx)
]


# coin_count: int = len(coin_list)


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
            exchange_to: 1.0 for exchange_to in Exchange.get_all() if exchange_to != exchange_from
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
    # Безопасная версия:
    if hasattr(__builtins__, 'print'):
        original_print = __builtins__.print
    elif 'print' in __builtins__:
        original_print = __builtins__['print']
    else:
        original_print = print 
    
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

async def monitor_worst_coin(analyst: Analyst):
    while True:
        try:
            buy, sell, benefit = analyst.sorted_coin.peekitem(-1)
            print(f"Worst: {buy.name}→{sell.name}, benefit={benefit:.6f}")
        except Exception as e:
            print(f"Monitor error: {e}")
        await asyncio.sleep(0.5)
 
async def main():
    try:
        async with redirect_prints_to_file("server.log") as log_ctx:
            async with ScoutDad(scouts_list) as scout_head:
                print("ScoutDad запущен корректно")
                
                guide = Guide(sell_commission=sell_commission, buy_commission=buy_commission, 
                            transfer_commission=transfer_commission, transfer_time=transfer_time)
                
                try:
                    async with Analyst(scout=scout_head, guide=guide) as analyst:
                        print("Analyst is ready")
                        
                        # Запускаем обновление данных и мониторинг ПАРАЛЛЕЛЬНО
                        update_task = asyncio.create_task(analyst.start_update())
                        monitor_task = asyncio.create_task(monitor_worst_coin(analyst))
                        
                        print("✅ Запущены оба процесса: обновление данных и мониторинг")
                        
                        try:
                            # Ждем любую из задач (или KeyboardInterrupt)
                            await asyncio.wait([update_task, monitor_task], 
                                             return_when=asyncio.FIRST_COMPLETED)
                        except KeyboardInterrupt:
                            print("Interrupted - stopping...")
                        finally:
                            # Корректно останавливаем обе задачи
                            if not update_task.done():
                                update_task.cancel()
                            if not monitor_task.done():
                                monitor_task.cancel()
                            
                            # Ждем завершения обеих задач
                            await asyncio.gather(update_task, monitor_task, 
                                               return_exceptions=True)
                            print("Все задачи остановлены")
                                    
                except ValueError as e:
                    print(f"Analyst failed: {e}")
                    raise
                    
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