from config import api_keys
from core import *
import socket
import json
import ccxt


SOCKET_PATH = '/tmp/my_socket'


def send_json_request(data):
    """Отправка структурированных данных в формате JSON"""
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    try:
        client.connect(SOCKET_PATH)
        
        message = json.dumps(data)
        client.sendall(message.encode())
        
        response = b""
        while True:
            chunk = client.recv(1024)
            if not chunk:
                break
            response += chunk
            if len(chunk) < 1024:
                break
        
        if response:
            return json.loads(response.decode())
        return None
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        client.close()

def get_exchange_from_str(exchange: str) -> ccxt.Exchange:
    """Получить объект биржи по строковому идентификатору"""
    exchange = exchange.lower()
    if exchange == 'binance':
        return ccxt.binance({
            'apiKey': api_keys['binance']['api_key'],
            'secret': api_keys['binance']['api_secret'],
        })
    elif exchange == 'okx':
        return ccxt.okx({
            'apiKey': api_keys['okx']['api_key'],
            'secret': api_keys['okx']['api_secret'],
            'password': api_keys['okx']['password'],
        })
    elif exchange == 'bitget':
        return ccxt.bitget({
            'apiKey': api_keys['bitget']['api_key'],
            'secret': api_keys['bitget']['api_secret'],
            'password': api_keys['bitget']['password'],
        })
    elif exchange == 'gate':
        return ccxt.gate({
            'apiKey': api_keys['gate']['api_key'],
            'secret': api_keys['gate']['api_secret'],
        })
    else:
        raise ValueError(f"Неизвестная биржа: {exchange}")



if __name__ == "__main__":
    message = input("Введите сообщение: ")
    data = {
        "command": "greeting",
        "message": message,
        "timestamp": "2024-01-01 12:00:00"
    }
    
    response = send_json_request(data)
    if response:
        print(f"JSON ответ: {response}")
        if response['buy']:
            print("Можно покупать")
            source = get_exchange_from_str(response['source'])
            endpoint = get_exchange_from_str(response['endpoint'])
            currency = response['currency']
            network = response['network']
            async with transaction(source=source, endpoint=endpoint, currency=currency, network=network) as tx:
                await tx.initialize()
                print(f"Депозитный адрес: {tx.deposit_address['address']} в сети {tx.deposit_address['network']}")
                print(f"Статус транзакции: {tx.status}")
                # Пример покупки
                try:
                    order = await tx.buy(quantity=0.001, stop_price=30000)
                    print(f"Ордер на покупку создан: {order}")
                except Exception as e:
                    print(f"Ошибка при покупке: {e}")
            
    