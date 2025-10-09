from collections import defaultdict
from config import COINS, EXCHANGES

class EfficiencyCalculator:
    def __init__(self):
        self.arbitrage_opportunities = []
    
    def calculate_efficiency(self, prices):
        """
        Расчет эффективности арбитража для всех пар бирж и монет
        Возвращает список возможностей отсортированный по эффективности
        """
        opportunities = []
        
        for coin in COINS:
            # Находим биржу с минимальной ценой покупки (ask)
            buy_exchanges = []
            for exchange in EXCHANGES:
                if coin in prices.get(exchange, {}):
                    ask_price = prices[exchange][coin]['ask']
                    if ask_price > 0:
                        buy_exchanges.append((exchange, ask_price))
            
            # Находим биржу с максимальной ценой продажи (bid)
            sell_exchanges = []
            for exchange in EXCHANGES:
                if coin in prices.get(exchange, {}):
                    bid_price = prices[exchange][coin]['bid']
                    if bid_price > 0:
                        sell_exchanges.append((exchange, bid_price))
            
            if not buy_exchanges or not sell_exchanges:
                continue
            
            # Сортируем по лучшим ценам
            best_buy = min(buy_exchanges, key=lambda x: x[1])
            best_sell = max(sell_exchanges, key=lambda x: x[1])
            
            if best_buy[0] == best_sell[0]:
                continue  # Пропускаем если одна биржа
            
            buy_price = best_buy[1]
            sell_price = best_sell[1]
            
            if buy_price > 0 and sell_price > buy_price:
                # Расчет эффективности (комиссии приблизительные)
                efficiency = ((sell_price - buy_price) / buy_price) * 100
                
                # Вычитаем приблизительные комиссии (0.2% на операцию)
                """
                ДОБАВИТЬ ПОЛУЧЕНИЕ КОМИССИИ ДЛЯ КАЖДОЙ ВАЛЮТЫ ИЗ CONFIG
                """
                net_efficiency = efficiency - 0.4
                
                if net_efficiency > 0:
                    opportunities.append({
                        'coin': coin,
                        'buy_exchange': best_buy[0],
                        'sell_exchange': best_sell[0],
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'efficiency': net_efficiency,
                        'potential_profit': sell_price - buy_price
                    })
        
        # Сортируем по эффективности
        opportunities.sort(key=lambda x: x['efficiency'], reverse=True)
        return opportunities
    
    def get_best_opportunity(self, prices):
        """Получить лучшую арбитражную возможность"""
        opportunities = self.calculate_efficiency(prices)
        return opportunities[0] if opportunities else None