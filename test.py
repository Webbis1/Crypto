# coding: utf-8
import requests
import time
import hashlib
import hmac


def gen_sign(method, url, query_string=None, payload_string=None):
    key = '3c161daae69c4add254f58a221b3df3a'        # api_key
    secret = 'ac93d7767b2e652da91ee959bfce0e1a34873e632c17e1858986ba75e9d55b09'     # api_secret

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}



host = "https://api.gateio.ws/api/v4"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

url = '/wallet/withdrawals'
query_param = ''
# for `gen_sign` implementation, refer to section `Authentication` above
sign_headers = gen_sign('GET', prefix + url, query_param)
headers.update(sign_headers)
r = requests.request('GET', host + prefix + url, headers=headers)
print(r)
