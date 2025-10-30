import asyncio
import logging

from .Types import *
from Exchange2.config import api_keys as API
from Exchange2.Types.ExFactory import ExFactory, ExchangeConnectionError
from bidict import bidict
from collections import defaultdict
from pprint import pprint
import csv
from pathlib import Path

import csv
from pathlib import Path
from collections import defaultdict
from typing import DefaultDict


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

all_ex: dict[str, set[Coin]] = {}
all_adresess: dict[str, int] = {}
actual_adresess: dict[str, int] = {}
all_coin_names: defaultdict[str, bidict[int, str]] = defaultdict(bidict)
all_network_names: defaultdict[str, bidict[int, str]] = defaultdict(bidict)

best_transfer: defaultdict[str, dict[str, dict[int, Coin]]] = defaultdict(lambda: defaultdict(dict))



import csv
from pathlib import Path
from collections import defaultdict
from typing import DefaultDict, Dict



def create_exchange_csv_tables(
    best_transfer: DefaultDict[str, Dict[str, Dict[int, Coin]]], 
    output_dir: str = "output"
):
    """
    Создает CSV таблицы для каждой биржи из best_transfer с группировкой по ID
    
    Args:
        best_transfer: словарь с лучшими вариантами перевода сгруппированный по ID
        output_dir: директория для сохранения CSV файлов
    """
    # Создаем директорию если её нет
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Получаем список всех бирж
    all_exchanges = set()
    for source_exchange, targets in best_transfer.items():
        all_exchanges.add(source_exchange)
        all_exchanges.update(targets.keys())
    
    all_exchanges = sorted(all_exchanges)
    
    # Создаем CSV для каждой биржи-источника
    for source_exchange in all_exchanges:
        if source_exchange not in best_transfer:
            continue
            
        filename = Path(output_dir) / f"{source_exchange}_transfers.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Заголовок CSV
            writer.writerow(['Coin ID', 'Target Exchange', 'Address', 'Coin Name', 'Network', 'Fee'])
            
            # Собираем все записи для этой биржи-источника
            all_records = []
            for target_exchange, coins_dict in best_transfer[source_exchange].items():
                for coin_id, coin in coins_dict.items():
                    all_records.append((coin_id, target_exchange, coin))
            
            # Сортируем по ID для удобства
            all_records.sort(key=lambda x: x[0])
            
            # Записываем данные
            for coin_id, target_exchange, coin in all_records:
                writer.writerow([
                    coin_id,
                    target_exchange,
                    coin.address,
                    coin.name,
                    coin.chain,
                    coin.fee if coin.has_known_fee else 'unknown'
                ])
        
        print(f"Создан файл: {filename}")

    # Создаем сводную таблицу по всем переводам
    create_summary_table_by_id(best_transfer, output_dir, all_exchanges)

def create_summary_table_by_id(
    best_transfer: DefaultDict[str, Dict[str, Dict[int, Coin]]], 
    output_dir: str, 
    all_exchanges: list
):
    """
    Создает сводную CSV таблицу с группировкой по ID монет
    """
    filename = Path(output_dir) / "all_transfers_by_id.csv"
    
    # Собираем все уникальные ID монет
    all_coin_ids = set()
    for source_exchange, targets in best_transfer.items():
        for target_exchange, coins_dict in targets.items():
            all_coin_ids.update(coins_dict.keys())
    
    all_coin_ids = sorted(all_coin_ids)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Заголовок: Coin ID + все пары бирж
        header = ['Coin ID', 'Coin Name', 'Address', 'Network']
        for source in all_exchanges:
            for target in all_exchanges:
                if source != target:
                    header.append(f'{source}→{target}')
        
        writer.writerow(header)
        
        # Заполняем таблицу для каждого ID
        for coin_id in all_coin_ids:
            # Находим любую монету с этим ID чтобы получить общую информацию
            sample_coin = None
            for source_exchange, targets in best_transfer.items():
                for target_exchange, coins_dict in targets.items():
                    if coin_id in coins_dict:
                        sample_coin = coins_dict[coin_id]
                        break
                if sample_coin:
                    break
            
            if not sample_coin:
                continue
            
            row = [
                coin_id,
                sample_coin.name,
                sample_coin.address,
                sample_coin.chain
            ]
            
            # Добавляем комиссии для всех пар бирж
            for source_exchange in all_exchanges:
                for target_exchange in all_exchanges:
                    if source_exchange == target_exchange:
                        continue
                    
                    coin = best_transfer[source_exchange].get(target_exchange, {}).get(coin_id)
                    if coin:
                        fee_str = f"{coin.fee}" if coin.has_known_fee else "unknown"
                        row.append(fee_str)
                    else:
                        row.append('—')
            
            writer.writerow(row)
    
    print(f"Создана сводная таблица по ID: {filename}")

# Дополнительная функция для нахождения абсолютных минимумов для каждого ID
def find_global_minimums(best_transfer: DefaultDict[str, Dict[str, Dict[int, Coin]]]):
    """
    Находит абсолютно минимальные комиссии для каждого ID монеты среди всех пар бирж
    """
    global_minimums = {}
    
    for source_exchange, targets in best_transfer.items():
        for target_exchange, coins_dict in targets.items():
            for coin_id, coin in coins_dict.items():
                if (coin_id not in global_minimums or 
                    coin < global_minimums[coin_id][1]):
                    global_minimums[coin_id] = (f"{source_exchange}→{target_exchange}", coin)
    
    return global_minimums

def create_global_minimums_csv(global_minimums: dict, output_dir: str = "output"):
    """
    Создает CSV с абсолютно минимальными комиссиями для каждого ID
    """
    filename = Path(output_dir) / "global_minimum_fees.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Coin ID', 'Best Transfer', 'Address', 'Coin Name', 'Network', 'Min Fee'])
        
        for coin_id, (best_pair, coin) in sorted(global_minimums.items()):
            writer.writerow([
                coin_id,
                best_pair,
                coin.address,
                coin.name,
                coin.chain,
                coin.fee if coin.has_known_fee else 'unknown'
            ])
    
    print(f"Создан файл с глобальными минимумами: {filename}")
    

def save_coin_names_to_csv_detailed(all_coin_names: dict[str, bidict[int, str]], output_dir: str = "coin_data"):
    """Сохраняет с дополнительной информацией и красивым форматированием"""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    print("💾 Сохранение данных по биржам:")
    print("=" * 50)
    
    for ex_name, coin_bidict in all_coin_names.items():
        filename = Path(output_dir) / f"{ex_name}_coins.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Заголовок с комментарием
            writer.writerow(['# Exchange:', ex_name])
            writer.writerow(['# Total coins:', len(coin_bidict)])
            writer.writerow([])  # пустая строка
            writer.writerow(['iterator', 'coin_name'])
            
            # Данные отсортированные по iterator
            for iterator in sorted(coin_bidict.keys()):
                coin_name = coin_bidict[iterator]
                writer.writerow([iterator, coin_name])
        
        print(f"📊 {ex_name:15} → {filename.name:20} ({len(coin_bidict):3} монет)")
    
    print("=" * 50)
    print(f"🎯 Всего бирж: {len(all_coin_names)}")




def save_coins_to_csv(coins_set: set[Coin], filename: str):
    """Сохраняет множество Coin в CSV файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        # Записываем заголовок
        f.write(Coin.csv_header() + '\n')
        
        # Записываем данные
        for coin in coins_set:
            f.write(coin.to_csv() + '\n')

def print_reverse_mapping(all_addresses: dict[str, int]) -> None:
    """Красиво выводит обратное отображение: для каждого int все str которые на него ссылались"""
    
    # Создаем обратное отображение
    reverse_map: dict[int, list[str]] = {}
    
    for address, number in all_addresses.items():
        if number not in reverse_map:
            reverse_map[number] = []
        reverse_map[number].append(address)
    
    # Сортируем по числам для красивого вывода
    sorted_numbers = sorted(reverse_map.keys())
    
    # Красивый вывод
    print("=" * 60)
    print("ОБРАТНОЕ ОТОБРАЖЕНИЕ:")
    print("=" * 60)
    
    for number in sorted_numbers:
        addresses = reverse_map[number]
        print(f"\n🔢 Число: {number}")
        print(f"   📍 Количество адресов: {len(addresses)}")
        print(f"   📋 Адреса:")
        
        # Выводим адреса с переносами и отступами
        for i, address in enumerate(addresses, 1):
            print(f"      {i:2d}. {address}")
    
    print("=" * 60)
    print(f"Всего уникальных чисел: {len(reverse_map)}")
    print(f"Всего адресов: {len(all_addresses)}")

async def is_trading_with_usdt(markets, coin_name):
    """Асинхронная проверка, торгуется ли монета с USDT"""
    try:
        for market in markets:
            if (market['base'] == coin_name and 
                market['quote'] == 'USDT' and 
                market['active']):
                return True, market['symbol']
        return False, None
    except Exception as e:
        print(f"Ошибка при проверке торговых пар: {e}")
        return False, None




async def main():    
    try:
        async with ExFactory(API) as factory:
            logger.info("ExFactory successfully initialized, exchanges connected, and balances checked.")
            iterator = 0
            for ex in factory:
                markets = await ex.fetch_markets()
                currencies = await ex.fetch_currencies()
                coins: set[Coin] = set()
                for coin_name, item in currencies.items():
                    if coin_name != "USDT":
                        trades_with_usdt, pair_symbol = await is_trading_with_usdt(markets, coin_name)
                        if not trades_with_usdt:
                            # print(f"{coin_name} не торгуется с USDT: {pair_symbol} на {ex.id}")
                            continue
                    temp_id = None
                    addresess = set()
                    if ex.id == 'binance':
                        networkList = item['info']['networkList']
                        for net in networkList:
                            chain = net['network']
                            if chain == "ETH":
                                continue     
                            if 'contractAddress' not in net or not net['contractAddress']: address = f'{coin_name}_{chain}'
                            else: address = net['contractAddress']
                            
                            if address in all_adresess:
                                temp_id = all_adresess[address]
                        
                            fee = float(net['withdrawFee'])
                            coin: Coin = Coin(_address = address, name=coin_name, chain=chain, fee=fee)
                            coins.add(coin)
                            addresess.add(address)      
                    elif ex.id == 'bitget':
                        networkList = item['info']['chains']
                        for net in networkList:
                            chain = net['chain']
                            if chain == "ERC20":
                                continue
                            if 'contractAddress' not in net or not net['contractAddress']: address = f'{coin_name}_{chain}'
                            else: address = net['contractAddress']
                            
                            if address in all_adresess:
                                temp_id = all_adresess[address]
                            
                            fee = float(net['withdrawFee'])
                            coin: Coin = Coin(_address = address, name=coin_name, chain=chain, fee=fee)
                            coins.add(coin)
                            addresess.add(address)
                    elif ex.id == 'kucoin':
                        networkList = item['info']['chains']
                        if networkList:
                            for net in networkList:
                                chain = net['chainId']
                                if chain == "ERC20":  # или "ETH" в зависимости от того, как называется Ethereum сеть в KuCoin
                                    continue
                                if 'contractAddress' not in net or not net['contractAddress']: 
                                    address = f'{coin_name}_{chain}'
                                else: 
                                    address = net['contractAddress']
                                
                                if address in all_adresess:
                                    temp_id = all_adresess[address]
                                
                                fee = float(net['withdrawalMinFee']) if net['withdrawalMinFee'] is not None else -1
                                coin: Coin = Coin(_address=address, name=coin_name, chain=chain, fee=fee)
                                coins.add(coin)
                                addresess.add(address)
                    elif ex.id == 'okx':
                        networkList = item['info']
                        for net in networkList:
                            chain = net['chain']
                            if chain == "ERC20":  # или другая сеть которую хотите исключить
                                continue
                            if 'ctAddr' not in net or not net['ctAddr']: 
                                address = f'{coin_name}_{chain}'
                            else: 
                                address = net['ctAddr']
                            
                            if address in all_adresess:
                                temp_id = all_adresess[address]
                            
                            fee = float(net['fee']) if net['fee'] else -1
                            coin: Coin = Coin(_address=address, name=coin_name, chain=chain, fee=fee)
                            coins.add(coin)
                            addresess.add(address)
                    elif ex.id == 'htx':
                        networkList = item['info']['chains']
                        if networkList:
                            for net in networkList:
                                chain = net['chain']
                                if chain == "ERC20":  # или "ETH" в зависимости от того, как называется Ethereum сеть в KuCoin
                                    continue
                                if 'contractAddress' not in net or not net['contractAddress']: 
                                    address = f'{coin_name}_{chain}'
                                else: 
                                    address = net['contractAddress']
                                
                                if address in all_adresess:
                                    temp_id = all_adresess[address]
                                
                                # Безопасное получение комиссии с проверкой наличия поля
                                fee = -1  # значение по умолчанию
                                if 'transactFeeWithdraw' in net and net['transactFeeWithdraw'] is not None:
                                    try:
                                        fee = float(net['transactFeeWithdraw'])
                                    except (ValueError, TypeError):
                                        fee = -1
                                # Альтернативные поля для комиссии, если основное отсутствует
                                elif 'withdrawFee' in net and net['withdrawFee'] is not None:
                                    try:
                                        fee = float(net['withdrawFee'])
                                    except (ValueError, TypeError):
                                        fee = -1
                                coin: Coin = Coin(_address=address, name=coin_name, chain=chain, fee=fee)
                                coins.add(coin)
                                addresess.add(address)
                    
                    
                    
                    if temp_id is None:
                        if len(addresess) > 0:
                            for addr in addresess:
                                all_adresess[addr] = iterator
                            all_coin_names[ex.id][iterator] = coin_name
                            iterator+=1
                    else: 
                        for addr in addresess: all_adresess[addr] = temp_id
                        all_coin_names[ex.id][temp_id] = coin_name
                    
                    # if coin_name == "USDT": print(coin)
                all_ex[ex.id] = coins
                save_coins_to_csv(coins, f"Data/{ex}_coins.csv")


            # merge = all_ex['binance'] & all_ex['bitget']
            # save_coins_to_csv(merge, f"Data/merge_coins.csv")

            # pprint(all_adresess)
            save_coin_names_to_csv_detailed(all_coin_names)
            # print_reverse_mapping(all_adresess)
            
    except ExchangeConnectionError as e:
        logger.error(f"Ошибка подключения к биржам: {e}")
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Другая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    for ex_name, coins in all_ex.items():
        for ex_name2, coins2 in all_ex.items():
            if ex_name == ex_name2: continue
            marge = coins & coins2
            for coin in marge:
                coin_id = all_adresess[coin.address]
                if (coin_id not in best_transfer[ex_name][ex_name2] or 
                    coin < best_transfer[ex_name][ex_name2][coin_id]):
                    best_transfer[ex_name][ex_name2][coin_id] = coin
                if coin in actual_adresess: continue
                actual_adresess[coin.address] = coin_id
    
    
    print(f'Всего адресов: {len(actual_adresess)}')
    # print_reverse_mapping(actual_adresess)
    create_exchange_csv_tables(best_transfer, "transfer_results")
    