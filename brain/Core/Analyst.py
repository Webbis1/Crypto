from .Types import Assets, ScoutHead, Coin, Exchange
from .Guide import Guide
from typing import Dict, Optional, Any, AsyncIterator, List
import asyncio
from sortedcontainers import SortedList, SortedDict



class Analyst:
    def __init__(self, scout: ScoutHead, guide: Guide, threshold: float = 2):
        self.scout = scout
        self.coin_list: Dict[Coin, Dict[Exchange, float]] = {}
        self.threshold = threshold
        self.guide = guide
        self.coin_locks: Dict[Coin, asyncio.Lock] = {}
        self.sorted_coin: SortedDict[Coin, tuple[Exchange, Exchange, float]] = SortedDict(key=lambda coin_data: coin_data[1][2])
    
    async def analyse(self, exchange: Exchange, coin: Coin):
        if coin == 1: 
            return await self._usdt_analyse(exchange)
        else:
            return await self._other_analyse(exchange, coin)
        
    async def _usdt_analyse(self, exchange: Exchange):
        worst_coin, (buy_exchange, _, worst_benefit) = self.sorted_coin.peekitem(-1)
        if(worst_benefit >= self.threshold):
            if exchange == buy_exchange:
                # покупка worst_coin
                answer = {
                    'recommendation': "trade",
                    'buying': worst_coin.name
                }
                return answer
            else:
                # перевод на buy_exchange
                answer = {
                    'recommendation': "transfer",
                    'destination': buy_exchange.name
                }
                return answer
    
    async def _other_analyse(self, current_exchange: Exchange, coin: Coin):
        buy_exchange = current_exchange
        peak_point: float = -float('inf')
        sell_exchange: Exchange = None
        
        for exchange in self.coin_list[coin]:
            benefit = self.__benefit(buy_exchange, exchange, coin)
            if benefit >= peak_point:
                sell_exchange = exchange
                peak_point = benefit
        
        if sell_exchange is None:
            raise ValueError(f"No suitable sell exchange found for coin {coin}")
        
        
        if current_exchange == sell_exchange:
            # продажа
            answer = {
                    'recommendation': "trade",
                    'buying': 'USDT'
                }
            return answer
        else:
            if(peak_point >= self.threshold):   
                # перевод на sell_exchange
                answer = {
                    'recommendation': "transfer",
                    'destination': sell_exchange.name
                }
                return answer
            else:
                # продажа
                answer = {
                    'recommendation': "trade",
                    'buying': 'USDT'
                }
                return answer
            
        
    
    def __find_min_element_for_coin(self, coin: Coin) -> Exchange:
        try:
            exchanges_prices = self.coin_list[coin]
            min_exchange = min(exchanges_prices, key=exchanges_prices.get)
            return min_exchange
        
        except KeyError:
            raise ValueError(f"No data for coin {coin}")
        except ValueError:
            raise ValueError(f"No exchanges for coin {coin}")
    
    async def update(self):
        async with self.scout as scout:
            async for update_coin in scout.coin_update():
                coin: Coin = update_coin[1].currency
                new_price: float = update_coin[1].amount
                exchange: Exchange = update_coin[0]
                self.coin_list[coin][exchange] = new_price
                self.sorted_coin[coin] = await self._coin_culc(coin)
    
    async def _coin_culc(self, coin: Coin) -> tuple[Exchange, Exchange, float]:
        async with self.coin_locks[coin]:
            buy_exchange = self.__find_min_element_for_coin(coin)
            peak_point: float = -float('inf')
            sell_exchange: Exchange = None
            
            for exchange in self.coin_list[coin]:
                benefit = self.__benefit(buy_exchange, exchange, coin)
                if benefit >= peak_point:
                    sell_exchange = exchange
                    peak_point = benefit
            
            if sell_exchange is None:
                raise ValueError(f"No suitable sell exchange found for coin {coin}")
            
            return buy_exchange, sell_exchange, peak_point
                

    def __benefit(self, buy_exchange: Exchange, sell_exchange: Exchange, coin: Coin) -> float:
        try:
            procedure_time = self.guide.transfer_time[coin][buy_exchange][sell_exchange]
            roi = self.__roi(buy_exchange, sell_exchange, coin)
            return roi / procedure_time
        
        except KeyError as e:
            raise ValueError(f"Missing transfer time data: {e}") from e
        except ZeroDivisionError:
            raise ValueError("Transfer time cannot be zero") from None


    def __roi(self, buy_exchange: Exchange, sell_exchange: Exchange, coin: Coin) -> float:
        try:
            buy_commission = self.guide.buy_commission[coin][buy_exchange]
            sale_commission = self.guide.sell_commission[coin][sell_exchange]
            buy_price = self.coin_list[coin][buy_exchange]
            sale_price = self.coin_list[coin][sell_exchange]
            
            return (sale_price * (1.0 - sale_commission) - buy_price * (1.0 + buy_commission)) / buy_price
        
        except KeyError as e:
            raise ValueError(f"Missing data for ROI calculation: {e}") from e

        
    
    async def __aenter__(self):
        self.coin_list = self.scout.coin_list()
        for coin in self.coin_list: # не уверен в синтакисе 
            self.coin_locks[coin] = asyncio.Lock()
            self.sorted_coin[coin] = await self._coin_culc(coin)
        return self
    

