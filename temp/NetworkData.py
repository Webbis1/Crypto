import ccxt.pro as ccxt
from brain.Core.Types.Coin import Coin
from Exchange2.Types import ExFactory
from Exchange2.config import api_keys as API
from Exchange2.Types import Port, ExFactory, ExchangeConnectionError, BalanceObserver, Trader
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import asyncio
import csv
import os
import pandas as pd
from bidict import bidict

#FOR GATE IO
import time
import hashlib
import hmac
import requests
import json

def add_data_to_csv(filename, header, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not (os.path.isfile(filename) and os.path.getsize(filename) > 0):
            writer.writerow(header) 
            
        writer.writerows(data) 

def get_ex_csv_header(networks: set):
    headers = ['Coin ID', 'Coin Name']
    
    for network in networks:
        headers.append(network)
        
    return headers

def gen_sign(method, url, query_string=None, payload_string=None):
    key = API['gate']['api_key']        # api_key
    secret = API['gate']['api_secret']     # api_secret

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

async def ex_to_csv(ex: ccxt.Exchange):
    if ex.id == 'binance':
        return
    
    filename = 'exchanges_networks_data/' + str(ex.id) + '_networks_fee.csv'
    
    coins_default = list(pd.read_csv('coins.csv')[ex.id])
    
    COINS: bidict[str, int] = {} 
    
    coin_id = 0
    for coin in coins_default:
        COINS[coin] = coin_id
        coin_id += 1
    
    cur = await ex.fetch_currencies()
    networks: set = set()
    
    answer: dict[int, dict[str, float]] = {}
    for coin, data in cur.items():
        if coin not in COINS:
            continue
        
        info = data['info']
        
        if ex.id == 'bitget':
            chains = info['chains']
            for chain in chains:
                network = chain['chain']
                fee = float(chain['withdrawFee'])
                networks.add(network)
                
                coin_id = COINS[coin]
                
                if coin_id not in answer:
                    answer[coin_id] = {}
                
                answer[coin_id][network] = fee
        
        elif ex.id == 'okx':
            for chain in info:
                network = chain['chain']
                fee = float(chain['fee'])
                networks.add(network)
                
                coin_id = COINS[coin]
                
                if coin_id not in answer:
                    answer[coin_id] = {}
                
                answer[coin_id][network] = fee
                
        elif ex.id == 'kucoin':
            chains = info['chains']
            for chain in chains:
                network = chain['chainName']
                fee = float(chain['withdrawalMinFee'])
                networks.add(network)
                
                coin_id = COINS[coin]
                
                if coin_id not in answer:
                    answer[coin_id] = {}
                
                answer[coin_id][network] = fee
                
        elif ex.id == 'htx':
            chains = info['chains']
            for chain in chains:
                network = chain['displayName']
                fee = float(chain['transactFeeWithdraw'])
                networks.add(network)
                
                coin_id = COINS[coin]
                
                if coin_id not in answer:
                    answer[coin_id] = {}
                
                answer[coin_id][network] = fee
                
        else:
            continue
                
    csv_data = [] 
    
    for coin_name, coin_id in COINS.items():
        csv_line = []
        
        csv_line.append(coin_id)
        csv_line.append(coin_name)
        
        for network in networks:
            fee = answer.get(coin_id, {}).get(network, None)
            csv_line.append(fee)
            
        csv_data.append(csv_line)
        
    add_data_to_csv(filename, get_ex_csv_header(networks), csv_data)
    
    print(f"Биржа {ex.id} обработана")

def main():
    '''
    try:
        tasks = []
        
        async with ExFactory(API) as factory:
            print("ExFactory successfully initialized, exchanges connected, and balances checked.")
            
            for ex in factory:
                tasks.append(asyncio.create_task(ex_to_csv(ex)))
                
                print(f"Задача по бирже {ex.id} запущена")

            await asyncio.gather(*tasks)

    except ExchangeConnectionError as e:
        print(f"Ошибка подключения к биржам: {e}")
    except KeyboardInterrupt:
        print("Программа остановлена пользователем")
    except Exception as e:
        print(f"Другая ошибка: {e}")
    '''
    
    #Проблема: разные названия сетей, из за этого не видит пересечения хотя оно есть
    
    exhanges = ['okx', 'kucoin', 'htx', 'bitget']
    
    for ex_destination in exhanges:   
        filename_networks = f'exchanges_data/{ex_destination}/networks.csv'
        filename_fees = f'exchanges_data/{ex_destination}/fees.csv'
        
        csv_headers = ['Coin ID'] + [ex for ex in exhanges if ex != ex_destination]
        
        csv_data_networks = []
        csv_data_fees = []
        
        ex_destination_pd_data = pd.read_csv(f"exchanges_networks_data/{ex_destination}_networks_fee.csv")     
        
        coins_default = list(pd.read_csv('coins.csv')[ex_destination])
        
        COINS: bidict[str, int] = {} 
    
        coin_id = 0
        for coin in coins_default:
            COINS[coin] = coin_id
            coin_id += 1
            
        for coin_name, coin_id in COINS.items():
            csv_networks_line = []
            csv_fees_line = []
            
            csv_networks_line.append(coin_id)
            csv_fees_line.append(coin_id)
            
            for ex_departure in exhanges:            
                if ex_destination == ex_departure:
                    continue
                
                ex_departure_pd_data = pd.read_csv(f"exchanges_networks_data/{ex_departure}_networks_fee.csv")  
                
                ex_destination_coin_dict = dict(list(dict(ex_destination_pd_data.iloc[coin_id]).items())[2:])
                ex_destination_coin_dict_without_nan = {}
                
                for key in ex_destination_coin_dict:
                    if (not pd.isna(ex_destination_coin_dict[key])):
                        ex_destination_coin_dict_without_nan[key] = ex_destination_coin_dict[key]
                        
                        
                ex_departure_coin_dict = dict(list(dict(ex_departure_pd_data.iloc[coin_id]).items())[2:])
                ex_departure_coin_dict_without_nan = {}
                
                for key in ex_departure_coin_dict:
                    if (not pd.isna(ex_departure_coin_dict[key])):
                        ex_departure_coin_dict_without_nan[key] = ex_departure_coin_dict[key]
                
                networks_intersection_dict = {}
                
                for key in ex_destination_coin_dict_without_nan:
                    if key in ex_departure_coin_dict_without_nan.keys():
                        networks_intersection_dict[key] = ex_departure_coin_dict_without_nan[key]
                
                if not networks_intersection_dict:
                    min_network = ''
                    min_fee = ''
                else:
                    min_network = min(networks_intersection_dict, key=networks_intersection_dict.get)
                    min_fee = min(networks_intersection_dict.values())
                
                csv_networks_line.append(min_network)
                csv_fees_line.append(min_fee)
                
            csv_data_networks.append(csv_networks_line)
            csv_data_fees.append(csv_fees_line)


        add_data_to_csv(filename_networks, csv_headers, csv_data_networks)
        add_data_to_csv(filename_fees, csv_headers, csv_data_fees)

if __name__ == "__main__":
    main()
    #asyncio.run(main())