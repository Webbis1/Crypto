from Exchange2.Types import BalanceObserver
import asyncio


class RegularObserver(BalanceObserver):    
    async def _process_balance_update(self, new_balances: dict[str, any]) -> None:
        try:
            for currency, new_balance in new_balances['total'].items():
                await self._notify(currency, new_balance)
                        
        except Exception as e:
            self.logging(f"Error processing balance update: {e}")
    
    
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

    async def start(self) -> None:
        if not self._is_running:
            await self._observe() 
        else:
            self.logging("Already running")

    async def stop(self) -> None:
        self._is_running = False
        self.logging("Stopped")