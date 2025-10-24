from decimal import Decimal
import ccxt
from brain.Core.Types.Coin import Coin
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

coin_list: list[Coin] = [
    Coin('USDT'),
    Coin('BTC'),
    Coin('ETH'),
    Coin('BNB'),
    Coin('SOL'),
    Coin('XRP'),
    Coin('ADA'),
    Coin('DOT'),
    Coin('DOGE'),
    Coin('AVAX'),
    Coin('MATIC'),
    Coin('LTC'),
    Coin('LINK'),
    Coin('ATOM'),
    Coin('UNI'),
    Coin('XLM'),
    Coin('ALGO'),
    Coin('NEAR'),
    Coin('FTM'),
    Coin('ETC'),
    Coin('BCH'),
    # Coin('XMR'),
    Coin('EOS'),
    Coin('AAVE'),
    Coin('MKR'),
    Coin('COMP'),
    Coin('YFI'),
    Coin('SUSHI'),
    Coin('CRV'),
    Coin('SNX'),
    Coin('RUNE'),
    Coin('GRT'),
    Coin('BAT'),
    Coin('ENJ'),
    Coin('MANA'),
    Coin('SAND'),
    Coin('AXS'),
    Coin('CHZ'),
    Coin('HBAR'),
    Coin('XTZ'),
    Coin('FIL'),
    Coin('THETA'),
    Coin('VET'),
    Coin('ICP'),
    Coin('FLOW'),
    Coin('EGLD'),
    Coin('KLAY'),
    Coin('ONE'),
    Coin('CELO'),
    Coin('IOTA'),
    Coin('ZIL'),
    Coin('WAVES'),
    Coin('NEO'),
    # Coin('ZEC'),
    # Coin('DASH'),
    Coin('QTUM'),
    Coin('ONT'),
    Coin('SC'),
    Coin('BTT'),
    Coin('WIN'),
    Coin('JST'),
    Coin('SUN'),
    Coin('ANKR'),
    Coin('OCEAN'),
    Coin('BAND'),
    Coin('OMG'),
    Coin('ZRX'),
    Coin('KAVA'),
    Coin('INJ'),
    Coin('ROSE'),
    Coin('IOTX'),
    Coin('AUDIO'),
    Coin('RSR'),
    Coin('COTI'),
    Coin('DODO'),
    Coin('PERP'),
    Coin('TRB'),
    Coin('UMA'),
    Coin('REN'),
    Coin('KNC'),
    Coin('REQ'),
    Coin('ORN'),
    Coin('TOMO'),
    Coin('DGB'),
    Coin('ICX'),
    Coin('AR'),
    Coin('RVN'),
    Coin('CELR'),
    Coin('SKL'),
    Coin('OGN'),
    Coin('CVC'),
    Coin('STORJ'),
    Coin('DATA'),
    Coin('ANT'),
    Coin('MIR'),
    Coin('TRU'),
    Coin('DENT'),
    Coin('HOT'),
    Coin('VTHO'),
    Coin('MTL'),
    Coin('NKN'),
    Coin('RLC'),
    Coin('POLY'),
    Coin('DIA'),
    Coin('BEL'),
    Coin('PSG'),
    Coin('JUV'),
    Coin('CITY'),
    Coin('ATM'),
    Coin('ASR'),
]

exchange_list = [
    ccxt.bitget(),
    ccxt.bybit(),
    ccxt.gate(),
    ccxt.kucoin(),
    ccxt.okx()
]

exchange_names_list = [
    'Bitget',
    'Bybit',
    'Gate',
    'Kucoin',
    'Okx'
]

def get_available_networks(exchange_from, exchange_to, symbol='USDT'):
    """Получить доступные сети для вывода"""
    try:
        networks_exchange_from = []
        currencies = exchange_from.fetch_currencies()
        if symbol in currencies:
            currency_info = currencies[symbol]
            networks_exchange_from = currency_info.get('networks', {})
        
        networks_exchange_to = []
        currencies = exchange_to.fetch_currencies()
        if symbol in currencies:
            currency_info = currencies[symbol]
            networks_exchange_to = currency_info.get('networks', {})
        
        networks = list(set(networks_exchange_from) & set(networks_exchange_to))
        
        if (len(networks) != 0):
            return networks
        
        return {}
    except Exception as e:
        print(f"Ошибка получения сетей: {e}")
        return {}
    
def get_withdrawal_info(exchange, symbol='USDT', network='BSC'):
    """Получить информацию о выводе: комиссию, минимальную и максимальную сумму"""
    try:
        currencies = exchange.fetch_currencies()
        if symbol in currencies:
            currency_info = currencies[symbol]
            if network in currency_info.get('networks', {}):
                
                network_info = currency_info['networks'][network]
                fee = Decimal(str(network_info.get('fee', 0)))
                min_amount_decimal = Decimal(str(network_info.get('limits', {}).get('withdraw', {}).get('min', 0)))
                max_amount = network_info.get('limits', {}).get('withdraw', {}).get('max', 0)

                if (max_amount is not None):
                    max_amount_decimal = Decimal(str(network_info.get('limits', {}).get('withdraw', {}).get('max', 0)))
                else:
                    max_amount_decimal = Decimal('Infinity')
                
                return fee
                
            else:
                print('Нет переданной сети' + str(network) +  'для выбранной монеты ' + str(symbol) + ' на бирже ' + str(exchange.name))
                return None
                
        else:
            print('Нет переданной монеты: ' + str(symbol) + ' на бирже ' + str(exchange.name))
            return None

    except Exception as e:
        print(f"Ошибка получения информации о выводе: {e}")
        print()
        return None
        
def get_fee_matrix():
    '''Строит трехмерную матрицу комиссий'''
    
    mat = [[[[]]]]
    coin_index = 0 
    exchange_from_index = 0
    exchange_to_index = 0
    
    for coin in coin_list:
        mat.append([[[]]])
        exchange_from_index = 0
        
        for exchange_from in exchange_list:
            mat.append([[]])
            
            for exchange_to in exchange_list:
                if (exchange_from.name == exchange_to.name):
                    continue
            
                mat[coin_index].append([])
                networks_list = get_available_networks(exchange_from, exchange_to, coin.name)
                            
                if (len(networks_list) == 0):
                    print('Монета ' + str(coin.name) + ' не торгуется на бирже ' + str(exchange_from.name))
                    continue
                
                for network in networks_list:
                    fee = get_withdrawal_info(exchange_from, coin.name, network)
                    print('Монета: ' + str(coin.name) + '; Биржа отправления: ' + str(exchange_from.name) + '; Биржа получения: ' + str(exchange_to.name) +  '; Сеть: ' + str(network) + '; Комиссия: ' + str(fee))
                    print('============')
                    
                    mat[coin_index][exchange_from_index][exchange_to_index].append(fee)
                    
                exchange_to_index += 1
                
            exchange_from_index += 1

        coin_index += 1
        print('Монета №' + str(coin_index) + ' обработана')

    print('Матрица комиссий построена')
    return mat

def get_min_fees_matrix(mat):
    '''Строит матрицу минимальных комиссий'''
    n_coins = len(mat)
    n_ex = len(mat[0]) if mat else 0

    min_fees = [[None for _ in range(n_ex)] for _ in range(n_coins)]
    popularity_counts = [0 for _ in range(n_ex)]  # счётчик для каждой биржи

    for i in range(n_coins):
        for j in range(n_ex):
            fees = mat[i][j]
            # Фильтруем None и пустые списки
            valid_fees = [f for f in fees if f is not None]
            
            if valid_fees:
                min_fees[i][j] = min(valid_fees)
                popularity_counts[j] += len(valid_fees)  # или += 1, если считать "наличие данных", а не кол-во записей
            else:
                min_fees[i][j] = None
                
    return min_fees

def display_min_fees_matrix(min_fees):
    '''Визуализирует матрицу минимальных комиссий'''
    
    # Преобразуем в числовой массив с NaN вместо None
    min_fees_numeric = np.array([
        [x if x is not None else np.nan for x in row]
        for row in min_fees
    ])

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        min_fees_numeric,
        xticklabels=exchange_names_list,
        yticklabels=map(lambda coin: coin.name, coin_list),
        annot=True,
        fmt=".4f",
        cmap="viridis",
        cbar_kws={'label': 'Минимальная комиссия'},
        mask=np.isnan(min_fees_numeric)  # скрыть NaN
    )
    plt.title("Минимальные комиссии по монетам и биржам")
    plt.xlabel("Биржа")
    plt.ylabel("Монета")
    plt.tight_layout()
    plt.show()

# Пример использования
def main():
    mat = get_fee_matrix()
    min_fees = get_min_fees_matrix(mat)
    #display_min_fees_matrix(min_fees)

    
if __name__ == "__main__":
    main()
    