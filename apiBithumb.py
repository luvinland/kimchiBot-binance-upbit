import requests

def bithumbWalletStatus():
    url = "https://api.bithumb.com/public/assetsstatus/ALL"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers = headers)
    return response.json()

def bithumbOrderbook(ticker):
    url = "https://api.bithumb.com/public/orderbook/" + ticker + "_KRW"
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.get(url, headers = headers)
    return response.json()
