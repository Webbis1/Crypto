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
                
        elif ex.id == 'gate':
            host = "https://api.gateio.ws"
            prefix = "/api/v4"
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

            url = '/wallet/withdrawals'
            query_param = ''
            # for gen_sign implementation, refer to section Authentication above
            sign_headers = gen_sign('GET', prefix + url, query_param)
            headers.update(sign_headers)
            r = requests.request('GET', host + prefix + url, headers=headers)
            print('GATE:')
            print(r.json())
                
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

async def main():
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


if __name__ == "__main__":
    #asyncio.run(main())
    
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/wallet/withdrawals'
    query_param = ''
    # for gen_sign implementation, refer to section Authentication above
    sign_headers = gen_sign('GET', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('GET', host + prefix + url, headers=headers)
    from pprint import pprint
    pprint(r.content)