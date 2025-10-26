from Exchange2.Types import BalanceObserver
import asyncio
from collections import defaultdict


class OkxObserver(BalanceObserver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_balances = {}  # Храним текущие балансы
        self._locks = defaultdict(asyncio.Lock)  # Асинхронные блокировки для каждой монеты
    
    async def _process_balance_update(self, new_balances: dict[str, any]) -> None:
        try:
            if 'total' not in new_balances:
                return
                
            current_total = new_balances['total']
            
            # Создаем задачи для обновления каждой монеты
            tasks = []
            for currency in current_total.keys():
                task = self._update_single_currency(currency, current_total)
                tasks.append(task)
            
            # Выполняем все задачи конкурентно
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logging(f"Error processing balance update: {e}")
    
    async def _update_single_currency(self, currency: str, current_total: dict[str, any]) -> None:
        # Получаем блокировку для конкретной монеты
        lock = self._locks[currency]
        async with lock:
            new_balance = current_total[currency]
            old_balance = self._current_balances.get(currency, 0.0)
            
            if old_balance != new_balance:
                await self._notify(currency, new_balance)
                self.logging(f"Coin - {currency}; Change - {new_balance}")
            
            self._current_balances[currency] = new_balance
    
    
    async def _observe(self) -> None:
        self._is_running = True
        try:
            # Добавляем информацию о бирже
            exchange_info = f"{self.ex.id}"  # базовое имя биржи
            if hasattr(self.ex, 'name'):
                exchange_info = f"{self.ex.name}"
            if hasattr(self.ex, 'urls'):
                exchange_info += f" ({self.ex.urls.get('www', '')})"
                
            self.logging(f"Starting WebSocket monitoring for {exchange_info}...")
            
            while self._is_running:
                try:
                    balance_update = await self.ex.watch_balance()
                    await self._process_balance_update(balance_update)
                    
                except asyncio.CancelledError:
                    # Нормально при завершении
                    self.logging(f"Observation cancelled for {self.ex.id}")
                    break
                except Exception as e:
                    self.logging(f"[{self.ex.id}] Error: {e}")
                    await asyncio.sleep(1)
                        
        except Exception as e:
            self.logging(f"Fatal error: {e}")
        finally:
            self._is_running = False
            self._current_balances = {}  # Очищаем при остановке

    async def start(self) -> None:
        if not self._is_running:
            await self._observe() 
        else:
            self.logging("Already running")

    async def stop(self) -> None:
        self._is_running = False
        self._current_balances = {}  # Очищаем при остановке
        self.logging("Stopped")