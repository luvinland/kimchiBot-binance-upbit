from binance.client import Client
import time
import config

while True:
    try:
        client = Client(config.binanceApiKey, config.binanceSecretKey)
    except:
        time.sleep(config.errorRetryTimer)
    else:
        break
print('logged in')

info = client.futures_exchange_info()
for i in info.get('symbols'):
    try:
        changeInitialLeverage = client.futures_change_leverage(
            symbol = i.get('symbol'),
            leverage = config.futureLeverage,
        )
    except:
        pass

    try:
        changeMaringType = client.futures_change_margin_type(
            symbol = i.get('symbol'),
            marginType = config.futureMarginType,
        )
    except:
        pass

print('Done')