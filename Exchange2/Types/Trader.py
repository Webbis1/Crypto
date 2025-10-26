import ccxt.pro as ccxtpro
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Trader:
    def __init__(self, ex: ccxtpro.Exchange, usdt_name: str = "USDT"):
        self.ex: ccxtpro.Exchange = ex
        self._USDT: str = usdt_name

    async def buy(self, coin_name: str, usdt_quantity: float):
        symbol = f"{self._USDT}/{coin_name}"
        try:
            order = await self.ex.create_order(symbol, 'market', 'sell', usdt_quantity)
            filled_amount = order.get('filled', 0)
            cost = order.get('cost', 0)
            logger.info(f"Buy order filled: {filled_amount} {coin_name} for {cost} {self._USDT}")
            return order
        except Exception as e:
            logger.error(f"Buy order failed for {symbol}: {e}")
            return None

    async def sell(self, coin_name: str, usdt_quantity: float):
        symbol = f"{self._USDT}/{coin_name}"
        try:
            order = await self.ex.create_order(symbol, 'market', 'buy', usdt_quantity)
            filled_amount = order.get('filled', 0)
            cost = order.get('cost', 0)
            logger.info(f"Sell order filled: {filled_amount} {coin_name} for {cost} {self._USDT}")
            return order
        except Exception as e:
            logger.error(f"Sell order failed for {symbol}: {e}")
            return None
