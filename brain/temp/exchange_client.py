import requests
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode
from config import EXCHANGES, COINS

class ExchangeClient:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {}
        self.base_urls = {
            'bybit': 'https://api.bybit.com',
            'gateio': 'https://api.gateio.ws/api/v4',
            'mexc': 'https://api.mexc.com',
            'okx': 'https://www.okx.com/api/v5',
            'bingx': 'https://open-api.bingx.com',
            'bitget': 'https://api.bitget.com/api/v2',
            'htx': 'https://api.huobi.pro',
            'kucoin': 'https://api.kucoin.com/api/v1',
            'phemex': 'https://api.phemex.com',
            'bitfinex': 'https://api-pub.bitfinex.com/v2'
        }
        
    def _get_signature(self, exchange, params, method='GET', endpoint=''):
        """Генерация подписи для разных бирж"""
        if exchange not in self.api_keys:
            return ''
            
        api_key = self.api_keys[exchange].get('api_key', '')
        secret_key = self.api_keys[exchange].get('secret_key', '')
        
        if exchange == 'bybit':
            timestamp = str(int(time.time() * 1000))
            signature_str = timestamp + api_key + "5000" + json.dumps(params)
            return hmac.new(secret_key.encode(), signature_str.encode(), hashlib.sha256).hexdigest()
            
        elif exchange == 'binance':
            query_string = urlencode(params)
            signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
            return signature
            
        elif exchange == 'gateio':
            timestamp = str(time.time())
            signature_str = method + "\n" + endpoint + "\n\n" + json.dumps(params) if method == 'POST' else ''
            signature = hmac.new(secret_key.encode(), signature_str.encode(), hashlib.sha512).hexdigest()
            return signature
            
        elif exchange == 'okx':
            timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
            message = timestamp + method + endpoint + (json.dumps(params) if params else '')
            signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
            return signature
            
        elif exchange == 'bitget':
            timestamp = str(int(time.time() * 1000))
            signature_str = timestamp + method + endpoint + (json.dumps(params) if params else '')
            signature = hmac.new(secret_key.encode(), signature_str.encode(), hashlib.sha256).hexdigest()
            return signature
            
        elif exchange == 'htx':
            timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
            params['AccessKeyId'] = api_key
            params['SignatureMethod'] = 'HmacSHA256'
            params['SignatureVersion'] = '2'
            params['Timestamp'] = timestamp
            sorted_params = sorted(params.items())
            signature_str = method + '\napi.huobi.pro\n' + endpoint + '\n' + urlencode(sorted_params)
            signature = hmac.new(secret_key.encode(), signature_str.encode(), hashlib.sha256).hexdigest()
            return signature
            
        elif exchange == 'kucoin':
            timestamp = str(int(time.time() * 1000))
            signature_str = timestamp + method + endpoint + (json.dumps(params) if params else '')
            signature = hmac.new(secret_key.encode(), signature_str.encode(), hashlib.sha256).hexdigest()
            return signature
            
        return ''

    def create_order(self, exchange, symbol, side, amount, price=None, order_type='market'):
        """
        Создание ордера на бирже
        """
        try:
            if exchange == 'bybit':
                return self._bybit_order(symbol, side, amount, price, order_type)
            elif exchange == 'gateio':
                return self._gateio_order(symbol, side, amount, price, order_type)
            elif exchange == 'mexc':
                return self._mexc_order(symbol, side, amount, price, order_type)
            elif exchange == 'okx':
                return self._okx_order(symbol, side, amount, price, order_type)
            elif exchange == 'bingx':
                return self._bingx_order(symbol, side, amount, price, order_type)
            elif exchange == 'bitget':
                return self._bitget_order(symbol, side, amount, price, order_type)
            elif exchange == 'htx':
                return self._htx_order(symbol, side, amount, price, order_type)
            elif exchange == 'kucoin':
                return self._kucoin_order(symbol, side, amount, price, order_type)
            elif exchange == 'phemex':
                return self._phemex_order(symbol, side, amount, price, order_type)
            elif exchange == 'bitfinex':
                return self._bitfinex_order(symbol, side, amount, price, order_type)
            else:
                print(f"Биржа {exchange} не поддерживается")
                return None
        except Exception as e:
            print(f"Ошибка создания ордера на {exchange}: {e}")
            return None

    # Bybit
    def _bybit_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['bybit']}/spot/v3/private/order"
        
        params = {
            "symbol": symbol,
            "qty": str(amount),
            "side": side.upper(),
            "type": order_type.upper(),
            "timeInForce": "GTC"
        }
        
        if price and order_type.lower() == 'limit':
            params["price"] = str(price)
            
        timestamp = str(int(time.time() * 1000))
        signature = self._get_signature('bybit', params, 'POST', '/spot/v3/private/order')
        
        headers = {
            'X-BAPI-API-KEY': self.api_keys.get('bybit', {}).get('api_key', ''),
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '5000',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if data.get('retCode') == 0:
            return {'order_id': data['result']['orderId'], 'status': 'success'}
        else:
            print(f"Bybit order error: {data.get('retMsg')}")
            return None

    # Gate.io
    def _gateio_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['gateio']}/spot/orders"
        
        params = {
            "currency_pair": f"{symbol}_USDT",
            "type": order_type,
            "side": side,
            "amount": str(amount),
            "price": str(price) if price else "0"
        }
        
        signature = self._get_signature('gateio', params, 'POST', '/spot/orders')
        
        headers = {
            'KEY': self.api_keys.get('gateio', {}).get('api_key', ''),
            'SIGN': signature,
            'Timestamp': str(time.time()),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if 'id' in data:
            return {'order_id': data['id'], 'status': 'success'}
        else:
            print(f"Gate.io order error: {data.get('message', 'Unknown error')}")
            return None

    # MEXC
    def _mexc_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['mexc']}/api/v3/order"
        
        params = {
            "symbol": f"{symbol}USDT",
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": amount
        }
        
        if price and order_type.lower() == 'limit':
            params["price"] = price
            
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_keys.get('mexc', {}).get('secret_key', '').encode(),
            query_string.encode(), hashlib.sha256
        ).hexdigest()
        
        headers = {
            'X-MEXC-APIKEY': self.api_keys.get('mexc', {}).get('api_key', ''),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, params=params, headers=headers)
        data = response.json()
        
        if 'orderId' in data:
            return {'order_id': data['orderId'], 'status': 'success'}
        else:
            print(f"MEXC order error: {data.get('msg', 'Unknown error')}")
            return None

    # OKX
    def _okx_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['okx']}/trade/order"
        
        params = {
            "instId": f"{symbol}-USDT",
            "tdMode": "cash",
            "side": side,
            "ordType": order_type,
            "sz": str(amount)
        }
        
        if price and order_type.lower() == 'limit':
            params["px"] = str(price)
            
        signature = self._get_signature('okx', params, 'POST', '/trade/order')
        
        headers = {
            'OK-ACCESS-KEY': self.api_keys.get('okx', {}).get('api_key', ''),
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()),
            'OK-ACCESS-PASSPHRASE': self.api_keys.get('okx', {}).get('passphrase', ''),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if data.get('code') == '0':
            return {'order_id': data['data'][0]['ordId'], 'status': 'success'}
        else:
            print(f"OKX order error: {data.get('msg', 'Unknown error')}")
            return None

    # BingX
    def _bingx_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['bingx']}/openApi/spot/v1/trade/order"
        
        params = {
            "symbol": f"{symbol}-USDT",
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": amount,
            "timestamp": int(time.time() * 1000)
        }
        
        if price and order_type.lower() == 'limit':
            params["price"] = price
            
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_keys.get('bingx', {}).get('secret_key', '').encode(),
            query_string.encode(), hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        
        headers = {
            'X-BX-APIKEY': self.api_keys.get('bingx', {}).get('api_key', ''),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, params=params, headers=headers)
        data = response.json()
        
        if data.get('code') == 0:
            return {'order_id': data['data']['orderId'], 'status': 'success'}
        else:
            print(f"BingX order error: {data.get('msg', 'Unknown error')}")
            return None

    # Bitget
    def _bitget_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['bitget']}/spot/trade/place-order"
        
        params = {
            "symbol": f"{symbol}USDT",
            "side": side,
            "orderType": order_type,
            "force": "normal",
            "quantity": str(amount),
            "timestamp": str(int(time.time() * 1000))
        }
        
        if price and order_type.lower() == 'limit':
            params["price"] = str(price)
            
        signature = self._get_signature('bitget', params, 'POST', '/api/v2/spot/trade/place-order')
        
        headers = {
            'ACCESS-KEY': self.api_keys.get('bitget', {}).get('api_key', ''),
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': params['timestamp'],
            'ACCESS-PASSPHRASE': self.api_keys.get('bitget', {}).get('passphrase', ''),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if data.get('code') == '00000':
            return {'order_id': data['data']['orderId'], 'status': 'success'}
        else:
            print(f"Bitget order error: {data.get('msg', 'Unknown error')}")
            return None

    # HTX (Huobi)
    def _htx_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['htx']}/v1/order/orders/place"
        
        params = {
            'account-id': self.api_keys.get('htx', {}).get('account_id', ''),
            'symbol': f"{symbol.lower()}usdt",
            'type': f"{side}-{order_type}",
            'amount': amount,
            'source': 'spot-api'
        }
        
        if price and order_type.lower() == 'limit':
            params['price'] = price
            
        signature = self._get_signature('htx', params, 'POST', '/v1/order/orders/place')
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Signature': signature
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if data.get('status') == 'ok':
            return {'order_id': data['data'], 'status': 'success'}
        else:
            print(f"HTX order error: {data.get('err-msg', 'Unknown error')}")
            return None

    # KuCoin
    def _kucoin_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['kucoin']}/orders"
        
        params = {
            "clientOid": str(int(time.time() * 1000)),
            "side": side,
            "symbol": f"{symbol}-USDT",
            "type": order_type,
            "size": str(amount)
        }
        
        if price and order_type.lower() == 'limit':
            params["price"] = str(price)
            
        signature = self._get_signature('kucoin', params, 'POST', '/api/v1/orders')
        
        headers = {
            'KC-API-KEY': self.api_keys.get('kucoin', {}).get('api_key', ''),
            'KC-API-SIGN': signature,
            'KC-API-TIMESTAMP': str(int(time.time() * 1000)),
            'KC-API-PASSPHRASE': self.api_keys.get('kucoin', {}).get('passphrase', ''),
            'KC-API-KEY-VERSION': '2',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if data.get('code') == '200000':
            return {'order_id': data['data']['orderId'], 'status': 'success'}
        else:
            print(f"KuCoin order error: {data.get('msg', 'Unknown error')}")
            return None

    # Phemex
    def _phemex_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['phemex']}/spot/orders"
        
        params = {
            "symbol": f"{symbol}USDT",
            "clOrdID": f"order_{int(time.time()*1000)}",
            "side": side.capitalize(),
            "orderQty": amount,
            "ordType": order_type.capitalize()
        }
        
        if price and order_type.lower() == 'limit':
            params["price"] = price
            
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_keys.get('phemex', {}).get('secret_key', '').encode(),
            query_string.encode(), hashlib.sha256
        ).hexdigest()
        
        headers = {
            'x-phemex-access-token': self.api_keys.get('phemex', {}).get('api_key', ''),
            'x-phemex-request-signature': signature,
            'x-phemex-request-expiry': str(int(time.time()) + 60),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if data.get('code') == 0:
            return {'order_id': data['data']['orderID'], 'status': 'success'}
        else:
            print(f"Phemex order error: {data.get('msg', 'Unknown error')}")
            return None

    # Bitfinex
    def _bitfinex_order(self, symbol, side, amount, price, order_type):
        url = f"{self.base_urls['bitfinex']}/auth/w/order/submit"
        
        params = {
            "type": order_type.upper(),
            "symbol": f"t{symbol}USD",
            "amount": str(amount if side == 'buy' else -amount),
            "meta": {}
        }
        
        if price and order_type.lower() == 'limit':
            params["price"] = str(price)
            
        nonce = str(int(time.time() * 1000))
        signature = f"/api{v2}/auth/w/order/submit{nonce}{json.dumps(params)}"
        signature = hmac.new(
            self.api_keys.get('bitfinex', {}).get('secret_key', '').encode(),
            signature.encode(), hashlib.sha384
        ).hexdigest()
        
        headers = {
            'bfx-nonce': nonce,
            'bfx-apikey': self.api_keys.get('bitfinex', {}).get('api_key', ''),
            'bfx-signature': signature,
            'content-type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        if data[0] and 'id' in data[0]:
            return {'order_id': data[0]['id'], 'status': 'success'}
        else:
            print(f"Bitfinex order error: {data}")
            return None

    def get_balance(self, exchange, coin):
        """Получение баланса"""
        try:
            if exchange == 'bybit':
                return self._get_bybit_balance(coin)
            elif exchange == 'gateio':
                return self._get_gateio_balance(coin)
            elif exchange == 'mexc':
                return self._get_mexc_balance(coin)
            elif exchange == 'okx':
                return self._get_okx_balance(coin)
            elif exchange == 'bingx':
                return self._get_bingx_balance(coin)
            elif exchange == 'bitget':
                return self._get_bitget_balance(coin)
            elif exchange == 'htx':
                return self._get_htx_balance(coin)
            elif exchange == 'kucoin':
                return self._get_kucoin_balance(coin)
            elif exchange == 'phemex':
                return self._get_phemex_balance(coin)
            elif exchange == 'bitfinex':
                return self._get_bitfinex_balance(coin)
            else:
                return 0
        except Exception as e:
            print(f"Ошибка получения баланса на {exchange}: {e}")
            return 0

    def _get_bybit_balance(self, coin):
        url = f"{self.base_urls['bybit']}/spot/v3/private/account"
        timestamp = str(int(time.time() * 1000))
        signature = self._get_signature('bybit', {}, 'GET', '/spot/v3/private/account')
        
        headers = {
            'X-BAPI-API-KEY': self.api_keys.get('bybit', {}).get('api_key', ''),
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '5000'
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data.get('retCode') == 0:
            for balance in data['result']['balances']:
                if balance['coin'] == coin:
                    return float(balance['free'])
        return 0

    def _get_gateio_balance(self, coin):
        url = f"{self.base_urls['gateio']}/spot/accounts"
        signature = self._get_signature('gateio', {}, 'GET', '/spot/accounts')
        
        headers = {
            'KEY': self.api_keys.get('gateio', {}).get('api_key', ''),
            'SIGN': signature,
            'Timestamp': str(time.time())
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        for account in data:
            if account['currency'] == coin:
                return float(account['available'])
        return 0

    def _get_okx_balance(self, coin):
        url = f"{self.base_urls['okx']}/asset/balances"
        params = {'ccy': coin}
        signature = self._get_signature('okx', params, 'GET', '/asset/balances')
        
        headers = {
            'OK-ACCESS-KEY': self.api_keys.get('okx', {}).get('api_key', ''),
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()),
            'OK-ACCESS-PASSPHRASE': self.api_keys.get('okx', {}).get('passphrase', '')
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if data.get('code') == '0':
            for balance in data['data']:
                if balance['ccy'] == coin:
                    return float(balance['availBal'])
        return 0

    # Аналогичные методы для других бирж...
    def _get_mexc_balance(self, coin):
        # Реализация для MEXC
        return 0

    def _get_bingx_balance(self, coin):
        # Реализация для BingX
        return 0

    def _get_bitget_balance(self, coin):
        # Реализация для Bitget
        return 0

    def _get_htx_balance(self, coin):
        # Реализация для HTX
        return 0

    def _get_kucoin_balance(self, coin):
        # Реализация для KuCoin
        return 0

    def _get_phemex_balance(self, coin):
        # Реализация для Phemex
        return 0

    def _get_bitfinex_balance(self, coin):
        # Реализация для Bitfinex
        return 0

    def withdraw(self, exchange, coin, amount, address):
        """Вывод средств"""
        try:
            if exchange == 'bybit':
                return self._bybit_withdraw(coin, amount, address)
            elif exchange == 'gateio':
                return self._gateio_withdraw(coin, amount, address)
            elif exchange == 'okx':
                return self._okx_withdraw(coin, amount, address)
            # Добавить методы для других бирж
            else:
                print(f"Вывод с {exchange} не реализован")
                return False
        except Exception as e:
            print(f"Ошибка вывода с {exchange}: {e}")
            return False

    def _bybit_withdraw(self, coin, amount, address):
        url = f"{self.base_urls['bybit']}/asset/v1/private/withdraw"
        
        params = {
            "coin": coin,
            "amount": str(amount),
            "address": address,
            "timestamp": str(int(time.time() * 1000))
        }
        
        signature = self._get_signature('bybit', params, 'POST', '/asset/v1/private/withdraw')
        
        headers = {
            'X-BAPI-API-KEY': self.api_keys.get('bybit', {}).get('api_key', ''),
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': params['timestamp'],
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        return data.get('retCode') == 0

    def _gateio_withdraw(self, coin, amount, address):
        url = f"{self.base_urls['gateio']}/withdrawals"
        
        params = {
            "currency": coin,
            "amount": str(amount),
            "address": address
        }
        
        signature = self._get_signature('gateio', params, 'POST', '/withdrawals')
        
        headers = {
            'KEY': self.api_keys.get('gateio', {}).get('api_key', ''),
            'SIGN': signature,
            'Timestamp': str(time.time()),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        return 'id' in data

    def _okx_withdraw(self, coin, amount, address):
        url = f"{self.base_urls['okx']}/asset/withdrawal"
        
        params = {
            "ccy": coin,
            "amt": str(amount),
            "dest": "4",  # внутренний вывод
            "toAddr": address,
            "fee": "0.0005"  # комиссия сети
        }
        
        signature = self._get_signature('okx', params, 'POST', '/asset/withdrawal')
        
        headers = {
            'OK-ACCESS-KEY': self.api_keys.get('okx', {}).get('api_key', ''),
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()),
            'OK-ACCESS-PASSPHRASE': self.api_keys.get('okx', {}).get('passphrase', ''),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=params, headers=headers)
        data = response.json()
        
        return data.get('code') == '0'

    def get_deposit_address(self, exchange, coin):
        """Получение адреса для депозита"""
        try:
            if exchange == 'bybit':
                return self._get_bybit_deposit_address(coin)
            elif exchange == 'gateio':
                return self._get_gateio_deposit_address(coin)
            elif exchange == 'okx':
                return self._get_okx_deposit_address(coin)
            # Добавить методы для других бирж
            else:
                print(f"Получение адреса для {exchange} не реализовано")
                return None
        except Exception as e:
            print(f"Ошибка получения адреса на {exchange}: {e}")
            return None

    def _get_bybit_deposit_address(self, coin):
        url = f"{self.base_urls['bybit']}/asset/v1/private/deposit/address"
        params = {'coin': coin}
        timestamp = str(int(time.time() * 1000))
        signature = self._get_signature('bybit', params, 'GET', '/asset/v1/private/deposit/address')
        
        headers = {
            'X-BAPI-API-KEY': self.api_keys.get('bybit', {}).get('api_key', ''),
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '5000'
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if data.get('retCode') == 0:
            return data['result']['address']
        return None

    def _get_gateio_deposit_address(self, coin):
        url = f"{self.base_urls['gateio']}/wallet/deposit_address"
        params = {'currency': coin}
        signature = self._get_signature('gateio', params, 'GET', '/wallet/deposit_address')
        
        headers = {
            'KEY': self.api_keys.get('gateio', {}).get('api_key', ''),
            'SIGN': signature,
            'Timestamp': str(time.time())
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if 'address' in data:
            return data['address']
        return None

    def _get_okx_deposit_address(self, coin):
        url = f"{self.base_urls['okx']}/asset/deposit-address"
        params = {'ccy': coin}
        signature = self._get_signature('okx', params, 'GET', '/asset/deposit-address')
        
        headers = {
            'OK-ACCESS-KEY': self.api_keys.get('okx', {}).get('api_key', ''),
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime()),
            'OK-ACCESS-PASSPHRASE': self.api_keys.get('okx', {}).get('passphrase', '')
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if data.get('code') == '0' and data['data']:
            return data['data'][0]['addr']
        return None

    def get_order_status(self, exchange, order_id, symbol):
        """Проверка статуса ордера"""
        try:
            # Реализация для каждой биржи
            if exchange == 'bybit':
                url = f"{self.base_urls['bybit']}/spot/v3/private/order"
                params = {'orderId': order_id}
                timestamp = str(int(time.time() * 1000))
                signature = self._get_signature('bybit', params, 'GET', '/spot/v3/private/order')
                
                headers = {
                    'X-BAPI-API-KEY': self.api_keys.get('bybit', {}).get('api_key', ''),
                    'X-BAPI-SIGN': signature,
                    'X-BAPI-TIMESTAMP': timestamp,
                    'X-BAPI-RECV-WINDOW': '5000'
                }
                
                response = requests.get(url, params=params, headers=headers)
                data = response.json()
                
                if data.get('retCode') == 0:
                    return data['result']['status']
            # Добавить методы для других бирж
            
            return 'unknown'
        except Exception as e:
            print(f"Ошибка проверки статуса ордера на {exchange}: {e}")
            return 'unknown'