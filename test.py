# coding: utf-8
import requests
import time
import hashlib
import hmac

host = "https://api.gateio.ws"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

url = '/wallet/withdrawals'
query_param = ''
# for `gen_sign` implementation, refer to section `Authentication` above
sign_headers = gen_sign('GET', prefix + url, query_param)
headers.update(sign_headers)
r = requests.request('GET', host + prefix + url, headers=headers)
print(r.json())
