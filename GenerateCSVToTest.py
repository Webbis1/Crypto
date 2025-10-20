import csv
import random
from datetime import datetime, timedelta

def generate_crypto_data(num_records):
    """
    Генерирует тестовые данные для арбитражных сделок
    """
    # Базовые настройки
    coins = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'MATIC']
    exchanges = ['Binance', 'Kraken', 'Coinbase', 'Bybit', 'Kucoin', 'Huobi']
    
    # Словарь с типичной волатильностью для каждой монеты (для более реалистичных данных)
    volatility = {
        'BTC': 0.8, 'ETH': 1.2, 'SOL': 2.5, 'XRP': 1.8, 
        'ADA': 2.0, 'DOT': 1.5, 'MATIC': 2.2
    }
    
    data = []
    base_time = datetime.strptime("10:00:00.000", "%H:%M:%S.%f")
    
    for i in range(num_records):
        # Время увеличивается на 0.5 секунды для каждой записи
        current_time = base_time + timedelta(milliseconds=500 * i)
        time_str = current_time.strftime("%H:%M:%S.%f")[:-3]  # Обрезаем до миллисекунд
        
        # Выбираем случайную монету
        coin = random.choice(coins)
        
        # Выбираем случайные биржи для покупки и продажи (разные)
        buy_exchange = random.choice(exchanges)
        sell_exchange = random.choice([ex for ex in exchanges if ex != buy_exchange])
        
        # Генерируем прибыль с учетом волатильности монеты
        base_profit = random.uniform(-0.3, 1.5)
        profit = round(base_profit * volatility.get(coin, 1.0), 2)
        
        data.append([
            coin,
            buy_exchange,
            sell_exchange,
            profit,
            time_str
        ])
    
    return data

def create_test_csv(filename, num_records=100):
    """
    Создает CSV файл с тестовыми данными
    """
    data = generate_crypto_data(num_records)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Записываем заголовок
        writer.writerow(['Монета', 'место где купить', 'место куда продать', 'прибыль', 'время'])
        
        # Записываем данные
        writer.writerows(data)
    
    print(f"Файл '{filename}' успешно создан с {num_records} записями")

# Дополнительная функция для создания данных, похожих на ваш пример
def create_similar_to_example(filename, num_seconds=10):
    """
    Создает данные, похожие на ваш пример файла
    """
    coins = ['BTC', 'ETH', 'SOL', 'XRP']
    exchange_pairs = {
        'BTC': [('Binance', 'Kraken')],
        'ETH': [('Coinbase', 'Binance')],
        'SOL': [('Kraken', 'Coinbase')],
        'XRP': [('Bybit', 'Binance')]
    }
    
    data = []
    base_time = datetime.strptime("10:00:00.000", "%H:%M:%S.%f")
    
    record_count = 0
    for second in range(num_seconds):
        for half in [0, 500]:  # 0.0 и 0.5 секунд
            current_time = base_time + timedelta(seconds=second, milliseconds=half)
            time_str = current_time.strftime("%H:%M:%S.%f")[:-3]
            
            for coin in coins:
                buy_exchange, sell_exchange = random.choice(exchange_pairs[coin])
                
                # Генерируем прибыль, которая немного меняется со временем
                base_range = {
                    'BTC': (-0.2, 0.7),
                    'ETH': (-0.3, 0.4),
                    'SOL': (0.8, 1.3),
                    'XRP': (-0.02, 0.07)
                }
                
                profit = round(random.uniform(*base_range[coin]), 2)
                
                data.append([
                    coin,
                    buy_exchange,
                    sell_exchange,
                    profit,
                    time_str
                ])
                record_count += 1
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Монета', 'место где купить', 'место куда продать', 'прибыль', 'время'])
        writer.writerows(data)
    
    print(f"Файл '{filename}' успешно создан с {record_count} записями (похоже на ваш пример)")

if __name__ == "__main__":
    # Создаем файл со случайными данными
    # create_test_csv("crypto_arbitrage_test.csv", 500)
    
    # Создаем файл, похожий на ваш пример
    create_similar_to_example("crypto_arbitrage_similar.csv", 500)
    
    # print("\nПример первых 5 записей из сгенерированного файла:")
    # with open("crypto_arbitrage_test.csv", 'r', encoding='utf-8') as f:
    #     for i, line in enumerate(f):
    #         if i < 6:  # Заголовок + 5 записей
    #             print(line.strip())