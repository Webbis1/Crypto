from .Types import Assets, ScoutHead, Coin, Exchange
from .Guide import Guide
from typing import Dict, Optional, Any, AsyncIterator, List
import asyncio
from sortedcollections import ValueSortedDict
from datetime import datetime
import logging


def save_coin_table_to_html(coin_list: Dict[Coin, Dict[Exchange, float]], filename=None):
    """Сохранение в HTML файл с красивой таблицей"""
    if filename is None:
        filename = f"coin_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    # Собираем все уникальные exchanges
    all_exchanges = set()
    for exchanges in coin_list.values():
        all_exchanges.update(exchanges.keys())
    all_exchanges = sorted(all_exchanges, key=lambda x: str(x))
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Coin Prices</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            th {{ background-color: #f2f2f2; position: sticky; top: 0; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .empty {{ background-color: #ffe6e6; }}
        </style>
    </head>
    <body>
        <h2>Coin Prices - {timestamp}</h2>
        <table>
            <thead>
                <tr>
                    <th>Coin</th>
    """
    
    # Заголовки exchanges
    for exchange in all_exchanges:
        html_content += f"<th>{exchange}</th>"
    html_content += "</tr></thead><tbody>"
    
    # Данные
    for coin, exchanges in sorted(coin_list.items(), key=lambda x: str(x[0])):
        html_content += f"<tr><td><strong>{coin}</strong></td>"
        for exchange in all_exchanges:
            value = exchanges.get(exchange)
            cell_class = "empty" if value is None else ""
            cell_value = f"{value:.8f}" if value is not None else "—"
            html_content += f'<td class="{cell_class}">{cell_value}</td>'
        html_content += "</tr>"
    
    html_content += "</tbody></table></body></html>"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML table saved to {filename}")

def print_to_html(sorted_coin_dict, title="Coin Data"):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <thead>
                <tr>
                    <th>Coin</th>
                    <th>Exchange 1</th>
                    <th>Exchange 2</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Добавляем строки таблицы
    for coin, (ex1, ex2, value) in sorted_coin_dict.items():
        value *= 100
        html += f"""
                <tr>
                    <td>{coin}</td>
                    <td>{ex1}</td>
                    <td>{ex2}</td>
                    <td>{value:.5f}</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    with open("coins.html", "w", encoding="utf-8") as f:
        f.write(html)

class Analyst:
    def __init__(self, scout: 'ScoutHead', guide: 'Guide', threshold: float = 2):
        # if scout is None:
        #     raise ValueError("Scout cannot be None")
        # print(f"[DEBUG] Analyst.__init__ called with scout: {scout}")  # DEBUG
        # print(f"[DEBUG] Scout type: {type(scout)}")  # DEBUG
        # print(f"[DEBUG] Scout id: {id(scout)}")  # DEBUG
        self.scout: 'ScoutHead' = scout
        
        self.coin_list: Dict[Coin, Dict[Exchange, float]] = {}
        self.threshold = threshold
        self.guide = guide
        
        # print(self.guide)
        self.coin_locks: Dict[Coin, asyncio.Lock] = {}
        self.sorted_coin: ValueSortedDict[Coin, tuple[Exchange, Exchange, float]] = ValueSortedDict(lambda value: value[2])
    
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
    
    async def start_update(self):
        print("🔄 Analyst: starting data collection")
        
        await self.scout.start_monitoring()
        print("✅ Analyst: monitoring started")
        
        update_count = 0
        async for update_coin in self.scout.coin_update():
            update_count += 1
            exchange: Exchange = update_coin[0]
            coin: Coin = update_coin[1].currency
            new_price: float = update_coin[1].amount
            
            print(f"📊 Analyst: update #{update_count} - {exchange.name}: {coin.name} = {new_price:.6f}")
            
            # Обновляем цену
            self.coin_list[coin][exchange] = new_price
            print(f"💰 Analyst: price updated for {coin.name} on {exchange.name}")
            
            # Пересчитываем монету
            try:
                self.sorted_coin[coin]  = await self._coin_culc(coin)
                print(f"🎯 Analyst: recalculated {coin.name}")
            except Exception as e:
                print(f"❌ Analyst: error recalculating {coin.name} - {e}")
            
            # Периодический статус
            if update_count % 10 == 0:
                print(f"📈 Analyst: processed {update_count} updates total")
    
    async def _coin_culc(self, coin: Coin) -> tuple[Exchange, Exchange, float]:
        async with self.coin_locks[coin]:
            buy_exchange = self.__find_min_element_for_coin(coin)
            peak_point: float = -float('inf')
            sell_exchange: Exchange = None
            
            for exchange in self.coin_list[coin]:
                benefit = self.__benefit(buy_exchange, exchange, coin)
                if benefit is not None and benefit >= peak_point:
                    sell_exchange = exchange
                    peak_point = benefit
            
            if sell_exchange is None:
                raise ValueError(f"No suitable sell exchange found for coin {coin}")
            
            return buy_exchange, sell_exchange, peak_point
                

    def __benefit(self, buy_exchange: Exchange, sell_exchange: Exchange, coin: Coin) -> float | None:
        try:
            # Безопасное получение времени перевода через цепочку get()
            procedure_time = self.guide.transfer_time.get(coin, {}).get(buy_exchange, {}).get(sell_exchange)
            
            # Если данных нет или время невалидно - пропускаем
            if procedure_time is None or procedure_time <= 0:
                return None
                
            roi = self.__roi(buy_exchange, sell_exchange, coin)
            return roi / procedure_time
            
        except ZeroDivisionError:
            return None
        except Exception:
            return None


    

    def __roi(self, buy_exchange: Exchange, sell_exchange: Exchange, coin: Coin) -> float:
        try:
            # Получаем комиссии
            buy_commission = self.guide.buy_commission[coin][buy_exchange]
            sale_commission = self.guide.sell_commission[coin][sell_exchange]
            
            # Получаем цены
            buy_price = self.coin_list[coin][buy_exchange]
            sale_price = self.coin_list[coin][sell_exchange]
            
            # Проверяем нулевые цены
            if buy_price == 0 or sale_price == 0:
                return 0.0
            
            commission: float = (1.0 - sale_commission) * (1.0 - buy_commission)
            effective_sale = ((1 * sale_price) / buy_price) * commission
            roi = (effective_sale - 1) / 1
                
            return roi
            
        except KeyError as e:
            print(f"Critical: Missing data for ROI calculation - {e}")
            return 0.0
            
        except ZeroDivisionError:
            print(f"Critical: Zero buy price for {coin} on {buy_exchange}")
            return 0.0
            
        except Exception as e:
            print(f"Critical: Unexpected error in ROI calculation - {e}")
            return 0.0
        
    
    async def __aenter__(self):
        print("Запуск аналитика")
        # if self.scout is not None:
        #     print("ScoutHead is normal")
        self.coin_list: dict[Coin, dict[Exchange, float]] = await self.scout.coin_list()
        print(f"Стартовые данные собраны\n Обрабатывается {len(self.coin_list)} монет")
        for coin in self.coin_list: # не уверен в синтакисе 
            self.coin_locks[coin] = asyncio.Lock()
            self.sorted_coin[coin] = await self._coin_culc(coin)
            
        worst_coin, (buy_exchange, sale_exchange, worst_benefit) = self.sorted_coin.peekitem(-1)
        print(f"Стартовые данные обработаны лучшая сделка: купить {worst_coin} на {buy_exchange} и продать на {sale_exchange} заработав {worst_benefit*100}%")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("rip Analyst")
        

