import asyncio
import ccxt
import ccxt.pro as ccxtpro
import pprint
from typing import Dict, Any

class KuCoinBalanceWatcher:
    def __init__(self, api_key: str, secret: str, password: str):
        self.exchange = ccxtpro.kucoin({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'sandbox': False,
        })
        
        self.previous_balance = {}
        
    async def on_usdt_increase(self, currency: str, old_amount: float, new_amount: float, difference: float):
        """
        Вызывается при увеличении баланса USDT
        """
        print(f"🎯 USDT BALANCE INCREASED!")
        print(f"   Currency: {currency}")
        print(f"   Previous: {old_amount:.6f}")
        print(f"   Current:  {new_amount:.6f}")
        print(f"   Added:    {difference:.6f} USDT")
        print("-" * 50)
        
    async def on_other_currency_increase(self, currency: str, old_amount: float, new_amount: float, difference: float):
        """
        Вызывается при увеличении баланса любой другой валюты (кроме USDT)
        """
        print(f"💰 OTHER CURRENCY BALANCE INCREASED!")
        print(f"   Currency: {currency}")
        print(f"   Previous: {old_amount:.6f}")
        print(f"   Current:  {new_amount:.6f}")
        print(f"   Added:    {difference:.6f} {currency}")
        print("-" * 50)
        
    def _parse_balance_update(self, balance_data):
        """
        Правильно парсим обновление баланса из WebSocket
        """
        if isinstance(balance_data, dict):
            # Стандартный формат ccxt
            if 'total' in balance_data:
                return balance_data['total']
            elif 'info' in balance_data:
                # Прямой формат от биржи
                info = balance_data['info']
                if 'data' in info:
                    return self._parse_kucoin_balance_data(info['data'])
        return balance_data
    
    def _parse_kucoin_balance_data(self, data):
        """
        Парсим специфичный формат KuCoin
        """
        balance = {}
        if isinstance(data, dict):
            for currency, amount in data.items():
                if isinstance(amount, (int, float)):
                    balance[currency] = amount
                elif isinstance(amount, dict):
                    balance[currency] = amount.get('available', 0) + amount.get('hold', 0)
        return balance
    
    def _calculate_balance_changes(self, new_balance_raw):
        """
        Вычисляет изменения баланса между текущим и предыдущим состоянием
        """
        new_balance = self._parse_balance_update(new_balance_raw)
        changes = {}
        
        if not isinstance(new_balance, dict):
            print(f"⚠️ Unexpected balance format: {type(new_balance)}")
            return changes
        
        for currency, new_amount in new_balance.items():
            if not isinstance(new_amount, (int, float)):
                continue
                
            old_amount = self.previous_balance.get(currency, 0)
            
            if new_amount != old_amount:
                changes[currency] = {
                    'old_amount': old_amount,
                    'new_amount': new_amount,
                    'difference': new_amount - old_amount
                }
                
        return changes
    
    async def watch_balance_forever(self):
        """
        Основной цикл наблюдения за изменениями баланса
        """
        print("🚀 Starting KuCoin balance watcher...")
        
        try:
            # Получаем начальный баланс
            initial_balance = await self.exchange.fetch_balance()
            self.previous_balance = initial_balance['total']
            print("✅ Initial balance loaded")
            print(f"📊 Initial USDT: {self.previous_balance.get('USDT', 0):.6f}")
            
            while True:
                try:
                    # Ждем обновления баланса через WebSocket
                    balance_update = await self.exchange.watch_balance()
                    print(f"📡 Received balance update: {type(balance_update)}")
                    # print(balance_update)
                    pprint.pprint(balance_update)
                    
                    # Вычисляем изменения
                    changes = self._calculate_balance_changes(balance_update)
                    
                    # Обрабатываем изменения
                    for currency, change_info in changes.items():
                        difference = change_info['difference']
                        
                        if difference > 0:  # Если баланс увеличился
                            if currency == 'USDT':
                                await self.on_usdt_increase(
                                    currency=currency,
                                    old_amount=change_info['old_amount'],
                                    new_amount=change_info['new_amount'],
                                    difference=difference
                                )
                            else:
                                await self.on_other_currency_increase(
                                    currency=currency,
                                    old_amount=change_info['old_amount'],
                                    new_amount=change_info['new_amount'],
                                    difference=difference
                                )
                        elif difference < 0:  # Если баланс уменьшился
                            print(f"🔻 {currency} decreased: {change_info['old_amount']:.6f} -> {change_info['new_amount']:.6f} (diff: {difference:.6f})")
                    
                    # Обновляем предыдущий баланс
                    if changes:
                        for currency, change_info in changes.items():
                            self.previous_balance[currency] = change_info['new_amount']
                    
                except Exception as e:
                    print(f"❌ Error in balance watch loop: {e}")
                    print(f"Error type: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    await asyncio.sleep(5)
                    
        except Exception as e:
            print(f"❌ Failed to start balance watcher: {e}")
            import traceback
            traceback.print_exc()
            
    async def close(self):
        """Закрытие соединения"""
        await self.exchange.close()


# Пример использования
async def main():
    # ЗАМЕНИТЕ НА ВАШИ РЕАЛЬНЫЕ КЛЮЧИ!
    API_KEY = "68eba1be03ad1c00011b0a37"
    SECRET = "e3d6c2ad-6ac3-4ae7-a605-28b59d937453"
    PASSWORD = "rABSQCS5XR5ubqh"
    
    # Запускаем наблюдатель
    watcher = KuCoinBalanceWatcher(API_KEY, SECRET, PASSWORD)
    
    # Запускаем тестер (без сделок)
    
    try:
        # Сначала показываем информацию о балансе
        # await tester.simulate_activity()
        
        # Затем запускаем наблюдатель
        print("\n🎯 Starting balance watcher...")
        await watcher.watch_balance_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping balance watcher...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await watcher.close()

if __name__ == "__main__":
    asyncio.run(main())