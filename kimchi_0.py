from binance.client import Client

import os
import time
import importlib
import apiUpbit
import apiGoogle
import config
import configKimchi

while True:
    try:
        client = Client(config.binanceApiKey, config.binanceSecretKey)
    except:
        time.sleep(config.errorRetryTimer)
    else:
        break

# Get Binance Trading Rules
def getBinanceTradingRules():
    if (os.path.isfile('binanceTradingRules.py')):
        os.remove('binanceTradingRules.py')

    info = client.futures_exchange_info()

    while True:
        try:
            binanceTradingRules = open('binanceTradingRules.py', 'a')
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    _head = 'binanceStepSize = {'
    binanceTradingRules.write(_head)

    for i in info.get('symbols'):
        if (i.get('symbol')[-4:] == 'USDT'):
            _body = '\'' + i.get('symbol')[:-4] + '\'' + ':' + '\'' + i.get('filters')[1].get('minQty') + '\'' + ', '
            binanceTradingRules.write(_body)

    _tail = '}'
    binanceTradingRules.write(_tail)

    _head = '\nbinancePriceMove = {'
    binanceTradingRules.write(_head)

    for i in info.get('symbols'):
        if (i.get('symbol')[-4:] == 'USDT'):
            _body = '\'' + i.get('symbol')[:-4] + '\'' + ':' + '\'' + i.get('filters')[0].get('tickSize') + '\'' + ', '
            binanceTradingRules.write(_body)

    _tail = '}'
    binanceTradingRules.write(_tail)

    binanceTradingRules.close()

if __name__ == "__main__":

    # Get Binance Trading Rules
    getBinanceTradingRules()

    if (configKimchi.ticker1):
        os.system('nohup python3 -u kimchi_1.py &')
        time.sleep(10.0)

    if (configKimchi.ticker2):
        os.system('nohup python3 -u kimchi_2.py &')
        time.sleep(10.0)

    if (configKimchi.ticker3):
        os.system('nohup python3 -u kimchi_3.py &')
        time.sleep(10.0)

    while True:
        while True:
            try:
                importlib.reload(configKimchi)
            except:
                time.sleep(config.errorRetryTimer)
            else:
                break

        # Check Upbit Balance
        while True:
            try:
                infoUpbitBalance = apiUpbit.upbitBalance()
            except:
                time.sleep(config.errorRetryTimer)
            else:
                break
        for inf in infoUpbitBalance:
            if (inf.get('currency') == 'KRW'):
                upbitBalance = inf.get('balance')

        # Binance Balance
        while True:
            try:
                info = client.futures_account()
            except:
                time.sleep(config.errorRetryTimer)
            else:
                break
        binanceBalance = info.get('availableBalance')

        if (configKimchi.ticker1):
            if ((not os.path.isfile('listenKey_kimchi_1.pickle')) and 
                (((float(upbitBalance) > configKimchi.kimchiOrderPrice) and 
                  (float(binanceBalance) > (configKimchi.kimchiOrderPrice / config.futureLeverage / apiGoogle.getGoogleKRWUSD()))) or 
                 os.path.isfile('tradeInfo_kimchi_1.pickle'))):
                os.system('nohup python3 -u kimchi_1.py &')
                time.sleep(10.0)

        if (configKimchi.ticker2):
            if ((not os.path.isfile('listenKey_kimchi_2.pickle')) and 
                (((float(upbitBalance) > configKimchi.kimchiOrderPrice) and 
                  (float(binanceBalance) > (configKimchi.kimchiOrderPrice / config.futureLeverage / apiGoogle.getGoogleKRWUSD()))) or 
                 os.path.isfile('tradeInfo_kimchi_2.pickle'))):
                os.system('nohup python3 -u kimchi_2.py &')
                time.sleep(10.0)

        if (configKimchi.ticker3):
            if ((not os.path.isfile('listenKey_kimchi_3.pickle')) and 
                (((float(upbitBalance) > configKimchi.kimchiOrderPrice) and 
                  (float(binanceBalance) > (configKimchi.kimchiOrderPrice / config.futureLeverage / apiGoogle.getGoogleKRWUSD()))) or 
                 os.path.isfile('tradeInfo_kimchi_3.pickle'))):
                os.system('nohup python3 -u kimchi_3.py &')
                time.sleep(10.0)

        time.sleep(300)
