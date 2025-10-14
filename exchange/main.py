from core import KuCoinMonitor, KuCoinTrader, BitgetBalanceWatcher, BitgetTrader
from config import api_keys
import asyncio
import datetime

async def balancerKuCoin():
    start_time = None
    first_operation_done = False
    
    try:
        async with KuCoinMonitor.KuCoinBalanceWatcher(
            api_key=api_keys['kucoin']['api_key'],
            secret=api_keys['kucoin']['api_secret'],
            password=api_keys['kucoin']['password']
        ) as monitor:
            trader = KuCoinTrader.KuCoinTrader(
                api_key=api_keys['kucoin']['api_key'],
                secret=api_keys['kucoin']['api_secret'],
                password=api_keys['kucoin']['password']
            )
            
            async for asset in monitor.receive_all():
                current_time = datetime.datetime.now()
                timestamp = current_time.strftime("%H:%M:%S.%f")[:-3]  # Формат: ЧЧ:ММ:СС.ммм
                
                # Проверяем, не прошло ли 30 секунд после первой операции
                if first_operation_done and start_time:
                    if asyncio.get_event_loop().time() - start_time >= 30:
                        print(f"[{timestamp}] ⏰ 30 seconds passed after first operation. Stopping.")
                        break
                
                # print(f"[{timestamp}] Updated asset: {asset.currency} = {asset.amount}")
                
                if asset.currency == 'USDT' and asset.amount > 2:
                    selling = asset
                    asset.amount -= 1
                    buying = 'CELR'
                    print(f"[{timestamp}] Attempting to trade {selling.amount} {selling.currency} for {buying}")
                    order = await trader.trade(selling, buying)
                    if order:
                        print(f"[{timestamp}] Trade successful:")
                        # Засекаем время после первой успешной операции
                        if not first_operation_done:
                            start_time = asyncio.get_event_loop().time()
                            first_operation_done = True
                            current_op_time = datetime.datetime.now()
                            op_timestamp = current_op_time.strftime("%H:%M:%S.%f")[:-3]
                            print(f"[{op_timestamp}] ⏱️ First operation completed. Running for 30 seconds.")
                    else:
                        print(f"[{timestamp}] Trade failed or no order returned.")
                
                # Продаем все другие валюты в USDT
                elif asset.currency != 'USDT' and asset.amount > 0:
                    selling = asset
                    buying = 'USDT'
                    print(f"[{timestamp}] 🔄 Selling all {asset.amount} {asset.currency} for USDT")
                    order = await trader.trade(selling, buying)
                    if order:
                        print(f"[{timestamp}] ✅ Sold {asset.currency} successfully: ")
                        # Засекаем время после первой успешной операции
                        if not first_operation_done:
                            start_time = asyncio.get_event_loop().time()
                            first_operation_done = True
                            current_op_time = datetime.datetime.now()
                            op_timestamp = current_op_time.strftime("%H:%M:%S.%f")[:-3]
                            print(f"[{op_timestamp}] ⏱️ First operation completed. Running for 30 seconds.")
                    else:
                        print(f"[{timestamp}] ❌ Failed to sell {asset.currency}")
                
                # Добавляем небольшую задержку между итерациями
                await asyncio.sleep(0.1)
                            
    except asyncio.CancelledError:
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Program terminated gracefully.")
        
async def balancerBitGet():

    try:
        async with BitgetBalanceWatcher.BitgetBalanceWatcher(
            api_key=api_keys['bitget']['api_key'],
            secret=api_keys['bitget']['api_secret'],
            password=api_keys['bitget']['password']
        ) as monitor:
            trader = BitgetTrader.BitgetTrader(
                api_key=api_keys['bitget']['api_key'],
                secret=api_keys['bitget']['api_secret'],
                password=api_keys['bitget']['password']
            )
            
            async for asset in monitor.receive_all():
                current_time = datetime.datetime.now()
                timestamp = current_time.strftime("%H:%M:%S.%f")[:-3]
                
                if asset.currency == 'USDT' and asset.amount > 2:
                    selling = asset
                    asset.amount -= 1
                    buying = 'CELR'
                    print(f"[{timestamp}] Attempting to trade {selling.amount} {selling.currency} for {buying}")
                    
                    # Запускаем торговлю в фоне, не блокируя получение следующих ассетов
                    asyncio.create_task(_execute_trade(trader, selling, buying, timestamp))
                
                elif asset.currency != 'USDT' and asset.amount > 200:
                    selling = asset
                    buying = 'USDT'
                    print(f"[{timestamp}] 🔄 Selling all {asset.amount} {asset.currency} for USDT")
                    
                    # Запускаем в фоне
                    asyncio.create_task(_execute_trade(trader, selling, buying, timestamp))
                    

                                
    except asyncio.CancelledError:
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Program terminated gracefully.")

async def _execute_trade(trader, selling, buying, timestamp):
    """Выполняет торговую операцию в фоне"""
    order = await trader.trade(selling, buying)
    if order:
        print(f"[{timestamp}] ✅ Trade successful for {selling.currency} -> {buying}")
    else:
        print(f"[{timestamp}] ❌ Trade failed for {selling.currency} -> {buying}")


if __name__ == "__main__":
    try:
        asyncio.run(balancerBitGet())
        pass
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")