from urllib.parse import urlencode, unquote

import jwt
import hashlib
import requests
import uuid
import config

def upbitApiKey():
    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4())
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.get('https://api.upbit.com/v1/api_keys', headers = headers)
    return res.json()

def upbitBalance():
    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4())
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.get('https://api.upbit.com/v1/accounts', headers = headers)
    return res.json()

def upbitWalletStatus():
    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4())
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.get('https://api.upbit.com/v1/status/wallet', headers = headers)
    return res.json()

def upbitOrderbook(ticker):
    headers = {"accept": "application/json"}
    response = requests.get('https://api.upbit.com/v1/orderbook?markets=KRW-' + ticker, headers = headers)
    return response.json()

def upbitOrder(params):
    query_string = urlencode(params).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512'
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization_token = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization_token}

    res = requests.post('https://api.upbit.com/v1/orders', params = params, headers = headers)
    return res.json()

def upbitInquiryOrder(params):
    query_string = unquote(urlencode(params, doseq = True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512'
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.get('https://api.upbit.com/v1/order', params = params, headers = headers)
    return res.json()

def upbitCancelOrder(params):
    query_string = unquote(urlencode(params, doseq = True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512'
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.delete('https://api.upbit.com/v1/order', params = params, headers = headers)
    return res.json()

def upbitInquiryWithdrawStatus(params):
    query_string = unquote(urlencode(params, doseq = True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512'
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.get('https://api.upbit.com/v1/withdraws/chance', params = params, headers = headers)
    return res.json()

def upbitWithdrawCoin(params):
    query_string = unquote(urlencode(params, doseq = True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512'
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.post('https://api.upbit.com/v1/withdraws/coin', json = params, headers = headers)
    return res.json()

def upbitWithdrawCoinAddress():
    payload = {
        'access_key': config.upbitAccessKey,
        'nonce': str(uuid.uuid4())
    }

    jwt_token = jwt.encode(payload, config.upbitSecretKey)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.get('https://api.upbit.com/v1/withdraws/coin_addresses', headers = headers)
    return res.json()
