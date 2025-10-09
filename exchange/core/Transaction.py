import ccxt.async_support as ccxt

class transaction:
    status = None
    
    async def __aenter__(self):
        self.source_orders = await self.source.watch_orders(symbol=self.pair)
        for order in self.source_orders:
            if order['status'] == 'open':
                raise Exception("Есть открытые ордера на покупку, транзакция прервана.")
            if order['status'] == 'closed':
                order['filled'] == order['amount']
                order['remaining'] == 0
                order['average']  # Средняя цена исполнения
                # raise Exception("Есть закрытые ордера на покупку, транзакция прервана.")
            if order['status'] == 'triggered':
                raise Exception("Есть сработавшие ордера на покупку, транзакция прервана.")
            order['status'] in ['partial', 'partially_filled']

        self.endpoint_orders = await self.endpoint.watch_orders(symbol=self.reverse_pair)
        print("Starting transaction...")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"Transaction failed: {exc_val}")
            self.status = "failed"
        else:
            print("Transaction completed successfully.")
            self.status = "completed"
        return False

    def _get_remaining_correct(order):
        if 'remaining' in order:
            return order['remaining']
        
        amount = order.get('amount', 0)
        filled = order.get('filled', 0)
        return amount - filled


    def __init__(self, source: ccxt.Exchange, endpoint: ccxt.Exchange, currency: str, network: str):
        self.source = source
        self.endpoint = endpoint
        self.currency = currency
        self.network = network
        self.pair = f"{self.currency}/USDT"
        self.reverse_pair = f"USDT/{self.currency}"
        self.deposit_address = None
        self.status = "initialized"

    async def initialize(self):
        """
        Асинхронная инициализация депозитного адреса
        """
        if self.deposit_address is None:
            self.deposit_address = await self.endpoint.fetch_deposit_address(self.currency)
            self.deposit_address['network'] = self.network
        self.status = "ready"
        print(f"✅ Инициализация завершена. Сеть: {self.network}")
        
    async def buy(self, quantity: float, stop_price: float):
        side = "buy"
        try:
            order = await self.exchange.create_order(
                symbol=self.pair,
                type='stop_loss',
                side=side,
                amount=quantity,
                stopPrice=stop_price 
            )
            return order
        
        except ccxt.BadRequest:
            order = await self.exchange.create_order(
                symbol=self.pair,
                type='stop_market',
                side=side,
                amount=quantity,
                stopPrice=stop_price
            )
        
        except ccxt.InsufficientFunds as e:
            raise Exception(f"Недостаточно средств: {e}")
            
        except ccxt.InvalidOrder as e:
            raise Exception(f"Неверные параметры ордера: {e}")
            
        except ccxt.NetworkError as e:
            raise Exception(f"Ошибка сети: {e}")
            
        except ccxt.ExchangeError as e:
            raise Exception(f"Ошибка биржи: {e}")
            
        except Exception as e:
            raise Exception(f"Неизвестная ошибка: {e}")
        
        return order

    
    async def transfer(self, amount, network: str):
        self.status = "transferring"
        withdrawal = await self.source.withdraw(
            code=self.currency,
            amount=amount,
            address=self.deposit_address['address'],
            tag=self.deposit_address.get('tag'),  # Для некоторых валют (XRP, XLM и т.д.)
            params={
                'network': self.deposit_address.get('network'),  # Сеть блокчейна
            }
        )