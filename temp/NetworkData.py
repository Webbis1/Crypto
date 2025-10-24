import ccxt
from brain.Core.Types.Coin import Coin
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import asyncio
import csv

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

# ... (coin_list, exchange_list, exchange_names_list остаются без изменений)

async def get_available_networks(exchange_from, exchange_to, symbol='USDT'):
    try:
        currencies_from = exchange_from.fetch_currencies()
        currencies_to = exchange_to.fetch_currencies()

        networks_from = set(currencies_from[symbol]['networks'].keys()) if symbol in currencies_from else set()
        networks_to = set(currencies_to[symbol]['networks'].keys()) if symbol in currencies_to else set()

        return list(networks_from & networks_to)
    except Exception as e:
        print(f"Ошибка получения сетей для {symbol}: {e}")
        return []

async def get_withdrawal_info(exchange, symbol='USDT', network='BSC'):
    try:        
        currencies = exchange.fetch_currencies()
        if symbol not in currencies:
            print(f'Монета {symbol} отсутствует на бирже {exchange.name}')
            return None

        currency_info = currencies[symbol]
        networks = currency_info.get('networks', {})
        if network not in networks:
            print(f'Сеть {network} недоступна для {symbol} на {exchange.name}')
            return None

        network_info = networks[network]
                
        fee = str(network_info.get('fee', 0))
        return fee
    except Exception as e:
        print(f"Ошибка получения комиссии для {symbol}/{network} на {exchange.name}: {e}")
        return None

async def get_fee_matrix():
    n_coins = len(coin_list)
    n_exchanges = len(exchange_list)
    
    mat = [[[[] for _ in range(n_exchanges)] for _ in range(n_exchanges)] for _ in range(n_coins)]

    for coin_idx, coin in enumerate(coin_list):
        coin_csv_filename = 'coins_networks_data/' + coin.name + '_networks_data.csv'
        coin_csv_data = []

        for ex_from_idx, exchange_from in enumerate(exchange_list):
            for ex_to_idx, exchange_to in enumerate(exchange_list):
                if exchange_from.name == exchange_to.name:
                    continue  # пропускаем одинаковые биржи

                networks = await get_available_networks(exchange_from, exchange_to, coin.name)
                if not networks:
                    continue

                fees_for_pair = []
                for network in networks:
                    fee = await get_withdrawal_info(exchange_from, coin.name, network)
                    if fee is not None:
                        fees_for_pair.append(fee)
                        print(f'Монета: {coin.name}; От: {exchange_from.name}; Куда: {exchange_to.name}; Сеть: {network}; Комиссия: {fee}')
                        print('============')
                        
                    line = [
                        exchange_from.name,
                        exchange_to.name,
                        network,
                        fee
                    ]
                    
                    coin_csv_data.append(line)

                mat[coin_idx][ex_from_idx][ex_to_idx] = fees_for_pair

        with open(coin_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Биржа ОТКУДА', 'Биржа КУДА', 'Сеть', 'Комиссия'])
            writer.writerows(coin_csv_data)
        
        print(f'Монета №{coin_idx + 1} ({coin.name}) обработана')

    print('Матрица комиссий построена')
    return mat

def get_min_fees_matrix(mat):
    n_coins = len(mat)
    if n_coins == 0:
        return []
    n_ex = len(mat[0])

    min_fees = [[None for _ in range(n_ex)] for _ in range(n_coins)]

    for i in range(n_coins):
        for j in range(n_ex):
            # Берём минимальную комиссию среди всех "куда" (но в вашем случае — по каждому направлению отдельно)
            # Но в текущей логике: mat[i][j][k] — это список комиссий для пары (j → k)
            # Однако в get_min_fees_matrix вы, кажется, хотите агрегировать по отправляющей бирже?
            # Поскольку визуализация — по монетам и биржам (отправка), будем брать минимум по всем направлениям из j
            all_fees = []
            for k in range(len(mat[i][j])):
                fees = mat[i][j][k]
                if isinstance(fees, list):
                    all_fees.extend([f for f in fees if f is not None])
            if all_fees:
                min_fees[i][j] = min(all_fees)
            else:
                min_fees[i][j] = None

    return min_fees

# display_min_fees_matrix остаётся без изменений (но убедитесь, что размеры совпадают)

async def main():
    mat = await get_fee_matrix()
    min_fees = get_min_fees_matrix(mat)
    # display_min_fees_matrix(min_fees)

if __name__ == "__main__":
    asyncio.run(main())