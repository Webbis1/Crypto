import asyncio
import inspect
import logging

from .config import api_keys as API
from .Types import Port, ExFactory, ExchangeConnectionError, BalanceObserver
from .Observers.RegularObserver import RegularObserver
from .Observers.OkxObserver import OkxObserver


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROUTES: dict[str, dict[int, dict[str, str]]] = {}

async def run_observers_with_graceful_shutdown(observers):
    """Запускает обсерверы с graceful shutdown"""
    observer_tasks = [asyncio.create_task(obs.start()) for obs in observers]
    
    try:
        await asyncio.gather(*observer_tasks)
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received, initiating graceful shutdown...")
    except asyncio.CancelledError:
        logger.debug("Tasks cancelled during shutdown")
    finally:
        # Останавливаем обсерверы
        for obs in observers:
            obs._is_running = False
        
        # Ждем завершения с таймаутом
        logger.info("⏳ Waiting for observers to finish...")
        done, pending = await asyncio.wait(observer_tasks, timeout=2.0)
        
        if pending:
            logger.info(f"⚠️  Cancelling {len(pending)} pending tasks...")
            for task in pending:
                task.cancel()
            
            # Ждем отмены
            await asyncio.wait(pending, timeout=1.0)
        
        logger.info("✅ All observers stopped")

def log_caller_info(func):
    async def wrapper(self, coin: str, change: float):
        # Здесь можно добавить логику для определения источника
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back  # два уровня назад
        caller_self = caller_frame.f_locals.get('self')
        
        source = "Unknown"
        if caller_self and hasattr(caller_self, 'ex'):
            source = getattr(caller_self.ex, 'id', 'Unknown')
        
        logger.info(f'Data from: {source}')
        return await func(self, coin, change)
    return wrapper

class TestSubscriber:
    def __init__(self, observers: list[BalanceObserver]):
        for obs in observers:
            obs.subscribe(self) 
        logger.info("TestSubscriber initialized")
    
    @log_caller_info
    async def update_price(self, coin: str, change: float) -> None:
        logger.info(f'TestClass: data is update\n Coin - {coin}; Quantity - {change}')

async def main():    
    try:
        async with ExFactory(API) as factory:
            logger.info("ExFactory successfully initialized, exchanges connected, and balances checked.")
            port: Port = Port(factory, ROUTES)
            
            observers = []
            for ex in factory:
                if ex.id == 'okx':
                    observers.append(OkxObserver(ex))
                else:
                    observers.append(RegularObserver(ex)) 
            
            pr = TestSubscriber(observers)
            
            await run_observers_with_graceful_shutdown(observers)
            
    except ExchangeConnectionError as e:
        logger.error(f"Ошибка подключения к биржам: {e}")
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Другая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())