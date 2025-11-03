from Core.Types import *
from Core.Analyst import Analyst
from Core.Guide import Guide
import asyncio
from Core.ResponseServer import AsyncResponseServer
from Core.scouts import *
import logging
from log_manager import AsyncLogManager
from setup import *
from sortedcollections import ValueSortedDict
import csv
from datetime import datetime
import os

async def writeCoinListInCSV (coins: ValueSortedDict[Coin, tuple[Exchange, Exchange, float]], sleepSeconds: int, parseSecondsDuring: int = -1, parseTimeInfinity: bool = False):
    CSV_FILENAME = 'coins.csv'
    line: list = list()
    
    while (parseSecondsDuring > 0 or parseTimeInfinity):
        csv_data: list = list()
        timestamp = datetime.now().strftime('%H:%M:%S')

        for key, value in coins.items():
            line = [
                key.name,
                value[0].name,
                value[1].name,
                round(value[2] * 100, 3),
                timestamp
            ]

            csv_data.append(line)

        with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            if not os.path.exists(CSV_FILENAME) or os.path.getsize(CSV_FILENAME) == 0:
                csvwriter.writerow(['Монета','место где купить','место куда продать','прибыль','время'])

            csvwriter.writerows(csv_data)

        # print('Coins CSV was updated')
        
        parseSecondsDuring -= sleepSeconds
        await asyncio.sleep(sleepSeconds)


async def main():
    logger = logging.getLogger('main')
    try:
        with AsyncLogManager("crypto_logs"):
            logger.info("Starting application with async logging")
            logging.getLogger('ccxt').setLevel(logging.WARNING)
            logging.getLogger('ccxt.base.exchange').setLevel(logging.WARNING)
            
            async with ScoutDad(scouts_list) as scout_head:
                logger.info("ScoutDad initialized successfully")
                
                try:
                    async with Analyst(scout=scout_head, guide=guide) as analyst:
                        logger.info("Analyst is ready and starting data processing")
                        
                        update_task = asyncio.create_task(analyst.start_update())
                        logger.info("Data update task started")

                        print_dict_task = asyncio.create_task(writeCoinListInCSV(analyst.sorted_coin, 2, 10, True))
                        print('Print coins task started')
                        
                        async with AsyncResponseServer(analyst) as server:
                            logger.info("AsyncResponseServer is ready")
                            server_task = asyncio.create_task(server.start_async_server())
                            logger.info("AsyncResponseServer is started")
                            
                            try:
                                # Просто ждем, пока пользователь не прервет выполнение
                                while True:
                                    await asyncio.sleep(1)
                                    
                            except KeyboardInterrupt:
                                logger.info("Received interrupt signal - stopping services")
                            finally:
                                # Отменяем задачи
                                if not update_task.done():
                                    update_task.cancel()
                                if not server_task.done():
                                    server_task.cancel()
                                
                                # Ждем завершения с обработкой исключений
                                try:
                                    await asyncio.gather(update_task, server_task, print_dict_task, return_exceptions=True)
                                except Exception as e:
                                    logger.error(f"Error during shutdown: {e}")
                                
                                logger.info("All tasks stopped successfully")
                except ValueError as e:
                    logger.error(f"Analyst initialization failed: {e}")
                    raise
                    
    except Exception as e:
        logger.critical(f"Critical error in main application: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        logger = logging.getLogger('main')
        logger.info("Starting crypto scanner application")
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Application finished by user request")
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)