import asyncio
from ExFactory import ExFactory, ExchangeConnectionError
from config import api_keys
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():    
    try:
        async with ExFactory(api_keys) as factory:
            logger.info("ExFactory successfully initialized, exchanges connected, and balances checked.")

            try:
                binance_ex = factory["binance"]
                logger.info(f"Accessed Binance exchange object (ID: {binance_ex.id}).")
            except KeyError as e:
                logger.warning(e)

            try:
                bybit_ex = factory["bybit"]
                logger.info(f"Accessed Bybit exchange object (ID: {bybit_ex.id}).")
            except KeyError as e:
                logger.warning(e)
            
            try:
                unknown_ex = factory["unknown"]
                logger.info(f"Accessed unknown exchange object (ID: {unknown_ex.id}).")
            except KeyError as e:
                logger.info(f"Attempted to get 'unknown' exchange: {e}")
            
    except ExchangeConnectionError as e:
        print(f"Ошибка подключения к биржам: {e}")
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем (Ctrl+C)")
    except Exception as e:
        print(f"Другая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())