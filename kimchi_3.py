from sre_constants import FAILURE, SUCCESS
from binance.client import Client
from multiprocessing import Process, Array, Value
from pytz import timezone

import os
import time
import datetime
import math
import pickle
import sys
import uuid
import json
import asyncio
import websockets
import importlib
import apiUpbit
import apiGoogle
import config
import configKimchi
import gmailReport
import kimchiOpenOrder
import kimchiCloseOrder

lightSailsName = os.environ.get('LIGHTSAILSNAME')

# Kill Process
def killProcess(removeListenKey):
    if (removeListenKey):
        os.remove('listenKey_kimchi_3.pickle')
    os.system('kill -9 `pgrep -f kimchi_3`')

# Send Gmail Report
def sendGmailReport(title, message):
    gmailReport.gmailReportSending(title, message)

# Get UPBIT Price
def getUpbitTickerPrice(ticker, upbit, upbitOrder, upbitAskSize, upbitAskSizeSum, upbitBidSize, upbitBidSizeSum, tradePosition):

    tickerName = ticker.value.decode('utf8')
    orderBookDepth = configKimchi.orderBookDepth

    async def recv_ticker():
        uri = 'wss://api.upbit.com/websocket/v1'
        markets = ['KRW-' + str(tickerName) + '.' + str(orderBookDepth)]

        async with websockets.connect(uri) as websocket:
            var = asyncio.Event()

            req = [{
                'ticket': str(uuid.uuid4())
            }, {
                'type': 'orderbook',
                'codes': markets
            }]
            await websocket.send(json.dumps(req))

            while not var.is_set():
                if (tradePosition.value == 0):
                    try:
                        recv_data = await websocket.recv()
                        orderbook = json.loads(recv_data)
                        tradePrice          = 100000000
                        tradeTargetPrice    = 0
                        tradeAskSize        = 0
                        tradeAskSizeSum     = 0
                        for order in orderbook.get('orderbook_units'):
                            if tradePrice > float(order.get('ask_price')):
                                tradePrice       = float(order.get('ask_price'))
                                tradeAskSize     = float(order.get('ask_size'))
                                tradeAskSizeSum  = tradeAskSize
                                tradeTargetPrice = float(order.get('ask_price'))
                            else:
                                tradeTargetPrice = float(order.get('ask_price'))
                                tradeAskSizeSum  = tradeAskSizeSum + float(order.get('ask_size'))
                        upbit.value           = tradePrice
                        upbitOrder.value      = tradeTargetPrice
                        upbitAskSize.value    = tradeAskSize
                        upbitAskSizeSum.value = tradeAskSizeSum
                    except:
                        upbit.value = 0
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Upbit websocket sleep and Re-start Process - kimchi_3 |', now)
                        killProcess(True)
                else:
                    try:
                        recv_data = await websocket.recv()
                        orderbook = json.loads(recv_data)
                        tradePrice       = 0
                        tradeTargetPrice = 100000000
                        tradeAskSize     = 0
                        tradeAskSizeSum  = 0
                        tradeBidSize     = 0
                        tradeBidSizeSum  = 0
                        for order in orderbook.get('orderbook_units'):
                            if tradePrice < float(order.get('bid_price')):
                                tradePrice      = float(order.get('bid_price'))
                                tradeBidSize    = float(order.get('bid_size'))
                                tradeBidSizeSum = tradeBidSize
                            else:
                                tradeBidSizeSum = tradeBidSize + float(order.get('bid_size'))
                            if tradeTargetPrice > float(order.get('ask_price')):
                                tradeTargetPrice = float(order.get('ask_price'))
                                tradeAskSize     = float(order.get('ask_size'))
                                tradeAskSizeSum  = tradeAskSize
                            else:
                                tradeTargetPrice = float(order.get('ask_price'))
                                tradeAskSizeSum  = tradeAskSizeSum + float(order.get('ask_size'))
                        upbit.value           = tradePrice
                        upbitOrder.value      = tradeTargetPrice
                        upbitAskSize.value    = tradeAskSize
                        upbitAskSizeSum.value = tradeAskSizeSum
                        upbitBidSize.value    = tradeBidSize
                        upbitBidSizeSum.value = tradeBidSizeSum
                    except:
                        upbit.value = 0
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        print('Warning #' + f'{configKimchi.ticker3:<5}', 'Upbit websocket sleep and Re-start Process - kimchi_3 |', now)
                        killProcess(True)

    try:
        asyncio.run(recv_ticker())
    except:
        upbit.value = 0
        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        if (tradePosition.value == 0):
            print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Upbit websocket sleep and Re-start Process - kimchi_3 |', now)
        else:
            print('Warning #' + f'{configKimchi.ticker3:<5}', 'Upbit websocket sleep and Re-start Process - kimchi_3 |', now)
        killProcess(True)

# Get BINANCE Price
def getBinanceTickerPrice(ticker, binance, binanceBidSize, binanceAskSize, tradePosition):

    tickerName = ticker.value.decode('utf8')

    async def recv_ticker():
        uri = 'wss://fstream.binance.com/ws/' + str(tickerName).lower() + 'usdt@bookTicker'

        async with websockets.connect(uri) as websocket:
            var = asyncio.Event()

            while not var.is_set():
                if (tradePosition.value == 0):
                    try:
                        recv_data = await websocket.recv()
                        temp = json.loads(recv_data)
                        binance.value = float(temp.get('b'))
                        binanceBidSize.value = float(temp.get('B'))
                    except:
                        binance.value = 0
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Binance websoc. sleep and Re-start Process - kimchi_3 |', now)
                        killProcess(True)
                else:
                    try:
                        recv_data = await websocket.recv()
                        temp = json.loads(recv_data) 
                        binance.value = float(temp.get('a'))
                        binanceAskSize.value = float(temp.get('A'))
                        binanceBidSize.value = float(temp.get('B'))
                    except:
                        binance.value = 0
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        print('Warning #' + f'{configKimchi.ticker3:<5}', 'Binance websoc. sleep and Re-start Process - kimchi_3 |', now)
                        killProcess(True)

    try:
        asyncio.run(recv_ticker())
    except:
        binance.value = 0
        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        if (tradePosition.value == 0):
            print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Binance websoc. sleep and Re-start Process - kimchi_3 |', now)
        else:
            print('Warning #' + f'{configKimchi.ticker3:<5}', 'Binance websoc. sleep and Re-start Process - kimchi_3 |', now)
        killProcess(True)

# Get USD/KRW
def getCurrencyKrw(rateKrw, newRateKrw, tradePosition): 
    while True:
        try:
            if (tradePosition.value == 0):
                rateKrw.value = apiGoogle.getGoogleKRWUSD()
            else:
                newRateKrw.value = apiGoogle.getGoogleKRWUSD()
        except:
            nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
            now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
            print('Warning Google KRWUSD rate Crawling fail and Pass Process - kimchi_3 |', now)
            pass

        time.sleep(config.rateKrwSleepTimer)

# Get Binance Futures User Data Streams
def getFStream():
    while True:
        try:
            client = Client(config.binanceApiKey, config.binanceSecretKey)
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    try:
        listenKey = client.futures_stream_get_listen_key()
    except:
        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        if (not os.path.isfile('orderId_kimchi_3.pickle')):
            print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Binance get ListenKey and Re-start Process - kimchi_3 |', now)
        else:
            print('Warning #' + f'{configKimchi.ticker3:<5}', 'Binance get ListenKey and Re-start Process - kimchi_3 |', now)
        killProcess(True)

    while True:
        try:
            listenKEY = open('listenKey_kimchi_3.pickle', 'wb')
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    data = {'l': listenKey}
    pickle.dump(data, listenKEY)
    listenKEY.close()

    async def recv_ticker():
        uri = 'wss://fstream.binance.com/ws/' + listenKey

        async with websockets.connect(uri) as websocket:
            var = asyncio.Event()

            while not var.is_set():
                try:
                    recv_data = await websocket.recv()
                    temp = json.loads(recv_data)
                except:
                    nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                    now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                    if (not os.path.isfile('orderId_kimchi_3.pickle')):
                        print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Binance streams sleep and Re-start Process - kimchi_3 |', now)
                    else:
                        print('Warning #' + f'{configKimchi.ticker3:<5}', 'Binance streams sleep and Re-start Process - kimchi_3 |', now)
                    killProcess(True)

                try:
                    if ((temp.get('o').get('s') == (configKimchi.ticker3 + 'USDT')) and (temp.get('o').get('x') == 'TRADE') and (temp.get('o').get('X') == 'FILLED')):
                        while True:
                            try:
                                orderID = open('orderId_kimchi_3.pickle', 'wb')
                            except:
                                time.sleep(config.errorRetryTimer)
                            else:
                                break

                        data = {'i': temp.get('o').get('i')}
                        pickle.dump(data, orderID)
                        orderID.close()

                    elif ((temp.get('o').get('s') == (configKimchi.ticker3 + 'USDT')) and (temp.get('o').get('o') == 'STOP_MARKET') and (temp.get('o').get('X') == 'EXPIRED')):
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        print('Error #' + f'{configKimchi.ticker3:<5}', 'Liqudation Position Binance and Kill Process - kimchi_3 |', now)
                        title   = Array('c', b'Liq. Position: #' + str(configKimchi.ticker3).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                        message = Array('c', b'Error Liqudation Position Binance and Kill Process - kimchi_3')
                        p6 = Process(target = sendGmailReport, args = (title, message))
                        p6.start()
                        p6.join()
                        killProcess(False)
                except:
                    pass

    try:
        asyncio.run(recv_ticker())
    except:
        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        if (not os.path.isfile('orderId_kimchi_3.pickle')):
            print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Binance streams sleep and Re-start Process - kimchi_3 |', now)
        else:
            print('Warning #' + f'{configKimchi.ticker3:<5}', 'Binance streams sleep and Re-start Process - kimchi_3 |', now)
        killProcess(True)

# Get Status Deposit/Withdraw
def getStatusDW(tickerName):
    statusU = 'X/X'
    statusB = 'X/X'

    while True:
        try:
            # Upbit wallet status
            resUpbitStatus = apiUpbit.upbitWalletStatus()
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    for res in resUpbitStatus:
        if (res.get('currency') == tickerName):
            statusUpbit = res.get('wallet_state')
            if (statusUpbit == 'working'):
                statusU = 'O/O'
            elif (statusUpbit == 'withdraw_only'):
                statusU = 'X/O'
            elif (statusUpbit == 'deposit_only'):
                statusU = 'O/X'
            elif (statusUpbit == 'paused'):
                statusU = 'X/X'

    # Binance wallet status
    while True:
        try:
            client = Client(config.binanceApiKey, config.binanceSecretKey)
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    while True:
        try:
            resBinanceStatus = client.get_all_coins_info()
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    for res in resBinanceStatus:
        if (res.get('coin') == tickerName):
            statusBinanceD = res.get('depositAllEnable')
            statusBinanceW = res.get('withdrawAllEnable')
            if ((statusBinanceD == 1) and (statusBinanceW == 1)):
                statusB = 'O/O'
            elif ((statusBinanceD == 0) and (statusBinanceW == 1)):
                statusB = 'X/O'
            elif ((statusBinanceD == 1) and (statusBinanceW == 0)):
                statusB = 'O/X'
            elif ((statusBinanceD == 0) and (statusBinanceW == 0)):
                statusB = 'X/X'

    ret = 'U:' + statusU + '·B:' + statusB
    return ret

# Set Binance Keep Alive Streams
def keepAlive(ticker, tradePosition, aliveKimchi, aliveOrderK):
    while True:
        try:
            client = Client(config.binanceApiKey, config.binanceSecretKey)
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    tickerName = ticker.value.decode('utf8')

    while True:
        if (aliveKimchi.value != 0.0):
            break

    while True:
        if (tradePosition.value == 0):
            # Check Upbit Balance
            for inf in apiUpbit.upbitBalance():
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

            if ((not os.path.isfile('orderId_kimchi_3.pickle')) and (float(upbitBalance) < configKimchi.kimchiOrderPrice)):
                nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                print('Error  ' + f'{tickerName:<5}', 'Insufficient Upbit KRW fund and Stop Process ∞ kimchi_3 |', now)
                title   = Array('c', b'Insufficient Upbit KRW: ' + str(tickerName).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                message = Array('c', b'Insufficient Upbit KRW fund and Stop Process' + ' ∞ '.encode("utf-8") + b'kimchi_3')
                p6 = Process(target = sendGmailReport, args = (title, message))
                p6.start()
                p6.join()
                killProcess(True)

            elif ((not os.path.isfile('orderId_kimchi_3.pickle')) and (float(binanceBalance) < (configKimchi.kimchiOrderPrice / config.futureLeverage / apiGoogle.getGoogleKRWUSD()))):
                nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                print('Error  ' + f'{tickerName:<5}', 'Insufficient Bin. USDT fund and Stop Process ∞ kimchi_3 |', now)
                title   = Array('c', b'Insufficient Bin. USDT: ' + str(tickerName).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                message = Array('c', b'Insufficient Bin. USDT fund and Stop Process' + ' ∞ '.encode("utf-8") + b'kimchi_3')
                p6 = Process(target = sendGmailReport, args = (title, message))
                p6.start()
                p6.join()
                killProcess(True)

        while True:
            try:
                listenKEY = open('listenKey_kimchi_3.pickle', 'rb')
            except:
                time.sleep(config.errorRetryTimer)
            else:
                break

        data_read = pickle.load(listenKEY)
        listenKEY.close()

        try:
            client.futures_stream_keepalive(data_read.get('l'))
        except:
            nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
            now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
            if (not os.path.isfile('orderId_kimchi_3.pickle')):
                print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Binance keeped stream and Re-start Process - kimchi_3 |', now)
            else:
                print('Warning #' + f'{configKimchi.ticker3:<5}', 'Binance keeped stream and Re-start Process - kimchi_3 |', now)
            killProcess(True)

        # Binance Inquiry Last Funding Rate
        try:
            info = client.futures_mark_price(
                symbol = tickerName + 'USDT'
            )
        except:
            nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
            now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
            if (not os.path.isfile('orderId_kimchi_3.pickle')):
                print('Warning  ' + f'{configKimchi.ticker3:<5}', 'Binance Funding-Rates and Re-start Process - kimchi_3 |', now)
            else:
                print('Warning #' + f'{configKimchi.ticker3:<5}', 'Binance Funding-Rates and Re-start Process - kimchi_3 |', now)
            killProcess(True)

        lastFundingRate = float(info.get('lastFundingRate')) * 100
        fundingRate     = f'{lastFundingRate:.3f}'
        aliveK          = f'{aliveKimchi.value:.2f}'
        aliveO          = f'{aliveOrderK.value:.2f}'

        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        if (tradePosition.value == 0):
            print('', now, '|', f'{tickerName:<5}', '| $:', f'{apiGoogle.getGoogleKRWUSD():<7}', '| K:', f'{aliveK:>5}', '% | F:', f'{fundingRate:>6}', '% |', getStatusDW(tickerName), '| kimchi_3')
        elif (tradePosition.value == 1):
            sign = '#'
            print('', now, '|', f'{tickerName:<5}', '| $:', f'{apiGoogle.getGoogleKRWUSD():<7}', '| →K:', f'{aliveK:>5}', '% · O:', f'{aliveO:>5}', '% |', getStatusDW(tickerName), '| F:', f'{fundingRate:>6}', '% | kimchi_3 |', sign)
        else:
            sign = '##'
            print('', now, '|', f'{tickerName:<5}', '| $:', f'{apiGoogle.getGoogleKRWUSD():<7}', '| →K:', f'{aliveK:>5}', '% · O:', f'{aliveO:>5}', '% |', getStatusDW(tickerName), '| F:', f'{fundingRate:>6}', '% | kimchi_3 |', sign)

        time.sleep(config.aliveSleepTimer)

# Get Trade Information
def getTradeInfo():
    try:
        tradeInfo = open('tradeInfo_kimchi_3.pickle', 'rb')
    except:
        return 0, None, 0.0, 0.0, 0.0

    data_read = pickle.load(tradeInfo)
    tradeInfo.close()

    t = data_read.get('t')
    u = data_read.get('u')
    o = data_read.get('o')
    r = data_read.get('r')
    b = data_read.get('b')

    return t, u, o, r, b

# Check UPBIT & BINANCE API Key
def checkApiKey():
    # Binance Key check
    try:
        info = client.get_account_api_permissions()
    except:
        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        print('Error get_account_api_permissions() & sys.exit() - kimchi_3')
        sys.exit(now)

    # Upbit Key check
    try:
        if (apiUpbit.upbitApiKey()[2].get('access_key') != config.upbitAccessKey):
            nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
            now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
            print('Error request.get(access_key) & sys.exit() - kimchi_3')
            sys.exit(now)
    except:
        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        if (not os.path.isfile('orderId_kimchi_1.pickle')):
            print('Error  ' + f'{ticker:<5}', 'Upbit API Keys check failed and Kill Process - kimchi_1 |', now)
            title   = Array('c', b'Upbit API Keys check failed: ' + str(ticker).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
            message = Array('c', b'Upbit API Keys check failed and Kill Process - kimchi_1')
        else:
            print('Error #' + f'{ticker:<5}', 'Upbit API Keys check failed and Kill Process - kimchi_1 |', now)
            title   = Array('c', b'Upbit API Keys check failed: #' + str(ticker).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
            message = Array('c', b'Upbit API Keys check failed and Kill Process - kimchi_1')
        p6 = Process(target = sendGmailReport, args = (title, message))
        p6.start()
        p6.join()
        killProcess(False)

# KIMCHI main function
if __name__ == "__main__":

    while True:
        try:
            client = Client(config.binanceApiKey, config.binanceSecretKey)
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    # Ticker update
    ticker = configKimchi.ticker3

    # # Ticker Sleep Timer
    tickerSleepTimer = 0.0

    # main process
    checkApiKey()

    # Get currency USD/KRW
    try:
        initRateKrw = apiGoogle.getGoogleKRWUSD()
    except:
        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
        print('Error getGoogleKRWUSD() & sys.exit() - kimchi_3')
        title   = Array('c', b'Error report')
        message = Array('c', b'Error getGoogleKRWUSD() & sys.exit() - kimchi_3')
        p6 = Process(target = sendGmailReport, args = (title, message))
        p6.start()
        p6.join()
        sys.exit(now)

    targetTicker  = Array('c', b'     ')
    targetTicker.value = ticker.encode("utf-8")

    tradePosition   = Value('d', 0.0)
    rateKrw         = Value('d', 0.0)
    newRateKrw      = Value('d', 0.0)
    upbit           = Value('d', 0.0)
    upbitOrder      = Value('d', 0.0)
    upbitAskSize    = Value('d', 0.0)
    upbitAskSizeSum = Value('d', 0.0)
    upbitBidSize    = Value('d', 0.0)
    upbitBidSizeSum = Value('d', 0.0)
    binance         = Value('d', 0.0)
    binanceBidSize  = Value('d', 0.0)
    binanceAskSize  = Value('d', 0.0)
    aliveKimchi     = Value('d', 0.0)
    aliveOrderK     = Value('d', 0.0)

    upbitStopLossUUID = ''
    prevKimchi = 0.0
    orderKimchi = 0.0

    # 0: Close, 1: Open, 2: Add Open
    nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
    now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
    tradePosition.value, upbitStopLossUUID, orderKimchi, rateKrw.value, binancePositionSize = getTradeInfo()
    prevKimchi = orderKimchi
    print('\n', now, '|', f'{ticker:<5}', '| $:', f'{initRateKrw:<7}', '| tradePosion:', tradePosition.value, '| PosionSize:', binancePositionSize)

    p1 = Process(target = getUpbitTickerPrice,   args = (targetTicker, upbit, upbitOrder, upbitAskSize, upbitAskSizeSum, upbitBidSize, upbitBidSizeSum, tradePosition))
    p1.start()
    time.sleep(config.errorRetryTimer)

    p2 = Process(target = getBinanceTickerPrice, args = (targetTicker, binance, binanceBidSize, binanceAskSize, tradePosition))
    p2.start()
    time.sleep(config.errorRetryTimer)

    p3 = Process(target = getCurrencyKrw,        args = (rateKrw, newRateKrw, tradePosition))
    p3.start()
    time.sleep(config.errorRetryTimer)

    p4 = Process(target = getFStream)
    p4.start()
    time.sleep(config.errorRetryTimer)

    while True:
        if (os.path.isfile('listenKey_kimchi_3.pickle')):
            break

    p5 = Process(target = keepAlive,             args = (targetTicker, tradePosition, aliveKimchi, aliveOrderK))
    p5.start()
    time.sleep(config.errorRetryTimer)

    while True:
        if ((upbit.value != 0.0) and (binance.value != 0.0) and (rateKrw.value != 0.0)):

            # Calculate values
            kimchi                = (upbit.value / binance.value / rateKrw.value - 1) * 100
            upbitAskGap           = upbitOrder.value / (upbit.value / 100) - 100

            upbitAskSizeKrwRaw    = math.trunc(upbit.value * upbitAskSize.value)
            upbitAskSizeSumKrwRaw = math.trunc(upbit.value * upbitAskSizeSum.value)
            upbitBidSizeKrwRaw    = math.trunc(upbit.value * upbitBidSize.value)
            upbitBidSizeSumKrwRaw = math.trunc(upbit.value * upbitBidSizeSum.value)
            binanceBidSizeKrwRaw  = math.trunc(binance.value * binanceBidSize.value * rateKrw.value)
            binanceAskSizeKrwRaw  = math.trunc(binance.value * binanceAskSize.value * rateKrw.value)

            upbitAskSizeKrw       = format(upbitAskSizeKrwRaw, ',')
            upbitAskSizeSumKrw    = format(upbitAskSizeSumKrwRaw, ',')
            upbitBidSizeKrw       = format(upbitBidSizeKrwRaw, ',')
            upbitBidSizeSumKrw    = format(upbitBidSizeSumKrwRaw, ',')
            binanceBidSizeKrw     = format(binanceBidSizeKrwRaw, ',')
            binanceAskSizeKrw     = format(binanceAskSizeKrwRaw, ',')

            kimChi            = f'{kimchi:.2f}'
            upbitAskGAP       = f'{upbitAskGap:.2f}'
            orderKimChi       = f'{orderKimchi:.2f}'
            aliveKimchi.value = kimchi
            aliveOrderK.value = orderKimchi

            # Print Kimchi value
            if (configKimchi.debugPrint):
                if (tradePosition.value == 0):
                    print('', f'{ticker:<5}', '| $:', f'{rateKrw.value:<7}', 
                        '| U:', f'{upbit.value:10}', f'{upbitAskSizeKrw:>13}', f'{upbitAskSizeSumKrw:>13}', f'↔ {upbitAskGAP:>4}', 
                        '% | B:', f'{binance.value:8}', f'{binanceBidSizeKrw:>13}', 
                        '| K:', f'{kimChi:>5}',
                        '| kimchi_3')
                else:
                    if (tradePosition.value == 1):
                        sign = '#'
                    else:
                        sign = '##'

                    print('', f'{ticker:<5}', '| $:', f'{rateKrw.value:<7}', '·', f'{newRateKrw.value:<7}',
                        '| U:', f'{upbit.value:10}', f'{upbitBidSizeKrw:>13}', f'{upbitBidSizeSumKrw:>13}', f'↔ {upbitAskGAP:>4}', 
                        '% | B:', f'{binance.value:8}', f'{binanceAskSizeKrw:>13}', 
                        '| K:', f'{kimChi:>5}', '· O:', f'{orderKimChi:>5}',
                        '| kimchi_3 |', sign)

            # Pre-order ticker
            if ((ticker == configKimchi.preOrder) and (tradePosition.value != 0)):
                if ((kimchi > configKimchi.PreOrderKimchi) and 
                    (upbitBidSizeKrwRaw > configKimchi.targetSize) and (upbitBidSizeSumKrwRaw > configKimchi.targetSizeSum) and 
                    (binanceAskSizeKrwRaw > (configKimchi.targetSizeSum / config.futureLeverage))):

                    orderSize  = binancePositionSize

                    if (orderSize != 0.0):
                        kimchiCloseOrder.closeKimchi(ticker, orderSize, rateKrw.value, newRateKrw.value, upbitStopLossUUID, kimchi)

                    tradePosition.value = 0
                    upbitStopLossUUID   = ''
                    upbitSLUUID         = ''
                    prevKimchi          = 0
                    orderKimchi         = 0
                    os.remove('tradeInfo_kimchi_3.pickle')

            # Open Kimchi
            if ((kimchi < configKimchi.targetOpenKimchi) and (tradePosition.value == 0) and 
                (upbitAskSizeKrwRaw > configKimchi.targetSize) and (upbitAskSizeSumKrwRaw > configKimchi.targetSizeSum) and upbitAskGap < configKimchi.allowAskGap and 
                (binanceBidSizeKrwRaw > (configKimchi.targetSizeSum / config.futureLeverage))):

                upbitSLUUID, orderKimchi, binancePositionSize, emptyBalance, Ret = kimchiOpenOrder.openKimchi(ticker, upbit.value, upbitOrder.value, tradePosition.value, rateKrw.value, upbitStopLossUUID, prevKimchi, kimchi)
                if (Ret == SUCCESS):
                    upbitStopLossUUID = upbitSLUUID
                    prevKimchi = orderKimchi
                    tradePosition.value = 1
                    newRateKrw.value = rateKrw.value

                    while True:
                        try:
                            tradeInfo = open('tradeInfo_kimchi_3.pickle', 'wb')
                        except:
                            time.sleep(config.errorRetryTimer)
                        else:
                            break

                    data = {'t': 1,'u': upbitSLUUID, 'o': orderKimchi, 'r': rateKrw.value, 'b': binancePositionSize}
                    pickle.dump(data, tradeInfo)
                    tradeInfo.close()
                else:
                    if (emptyBalance != 0):
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        if (emptyBalance == 1):
                            print('Error  ' + f'{ticker:<5}', 'Insufficient Bin. USDT fund and Stop Process - kimchi_3 |', now)
                            title   = Array('c', b'Insufficient Bin. USDT: ' + str(ticker).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                            message = Array('c', b'Insufficient Bin. USDT fund and Stop Process - kimchi_3')
                        else:
                            print('Error  ' + f'{ticker:<5}', 'Insufficient Upbit KRW fund and Stop Process √ kimchi_3 |', now)
                            title   = Array('c', b'Insufficient Upbit KRW: ' + str(ticker).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                            message = Array('c', b'Insufficient Upbit KRW fund and Stop Process' + ' √ '.encode("utf-8") + b'kimchi_3')
                        p6 = Process(target = sendGmailReport, args = (title, message))
                        p6.start()
                        p6.join()
                        killProcess(True)

            # Add Open Kimchi
            elif ((kimchi < configKimchi.targetAddKimchi) and (tradePosition.value == 1) and 
                  (upbitAskSizeKrwRaw > configKimchi.targetSize) and (upbitAskSizeSumKrwRaw > configKimchi.targetSizeSum) and upbitAskGap < configKimchi.allowAskGap and 
                  (binanceBidSizeKrwRaw > (configKimchi.targetSizeSum / config.futureLeverage))):

                upbitSLUUID, orderKimchi, binancePositionSize, emptyBalance, Ret = kimchiOpenOrder.openKimchi(ticker, upbit.value, upbitOrder.value, tradePosition.value, rateKrw.value, upbitStopLossUUID, prevKimchi, kimchi)
                if (Ret == SUCCESS):
                    upbitStopLossUUID = upbitSLUUID
                    tradePosition.value = 2

                    while True:
                        try:
                            tradeInfo = open('tradeInfo_kimchi_3.pickle', 'wb')
                        except:
                            time.sleep(config.errorRetryTimer)
                        else:
                            break

                    data = {'t': 2,'u': upbitSLUUID, 'o': orderKimchi, 'r': rateKrw.value, 'b': binancePositionSize}
                    pickle.dump(data, tradeInfo)
                    tradeInfo.close()
                else:
                    if (emptyBalance != 0):
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        if (emptyBalance == 1):
                            print('Error #' + f'{ticker:<5}', 'Insufficient Bin. USDT fund and Stop Process - kimchi_3 |', now)
                            title   = Array('c', b'Insufficient Bin. USDT: #' + str(ticker).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                            message = Array('c', b'Insufficient Bin. USDT fund and Stop Process - kimchi_3')
                        else:
                            print('Error #' + f'{ticker:<5}', 'Insufficient Upbit KRW fund and Stop Process - kimchi_3 √', now)
                            title   = Array('c', b'Insufficient Upbit KRW: #' + str(ticker).encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                            message = Array('c', b'Insufficient Upbit KRW fund and Stop Process' + ' √ '.encode("utf-8") + b'kimchi_3')
                        p6 = Process(target = sendGmailReport, args = (title, message))
                        p6.start()
                        p6.join()
                        killProcess(True)

            # Close Kimchi
            elif ((((kimchi > configKimchi.targetCloseKimchi) and (tradePosition.value == 1)) or ((kimchi > configKimchi.targetFinalKimchi) and (tradePosition.value == 2))) and 
                  (upbitBidSizeKrwRaw > configKimchi.targetSize) and (upbitBidSizeSumKrwRaw > configKimchi.targetSizeSum) and 
                  (binanceAskSizeKrwRaw > (configKimchi.targetSizeSum / config.futureLeverage))):

                orderSize  = binancePositionSize

                # Order Normal Close Kimchi
                Ret = kimchiCloseOrder.closeKimchi(ticker, orderSize, rateKrw.value, newRateKrw.value, upbitStopLossUUID, kimchi)
                if (Ret == SUCCESS):
                    tradePosition.value = 0
                    upbitStopLossUUID   = ''
                    upbitSLUUID         = ''
                    prevKimchi          = 0
                    orderKimchi         = 0
                    os.remove('tradeInfo_kimchi_3.pickle')

            while True:
                try:
                    importlib.reload(configKimchi)
                except:
                    time.sleep(config.errorRetryTimer)
                else:
                    break

            # Sleep Timer update
            if (configKimchi.tickerSleepTimer == 0.0):
                if (((tradePosition.value == 0) and (kimchi <= (configKimchi.targetOpenKimchi + 1.0))) or 
                      ((tradePosition.value == 1) and ((kimchi >= (configKimchi.targetCloseKimchi - 1.0)) or (kimchi <= (configKimchi.targetAddKimchi + 1.0)))) or 
                      ((tradePosition.value == 2) and (kimchi >= (configKimchi.targetFinalKimchi - 1.0)))):
                    tickerSleepTimer = configKimchi.tickerFastTimer
                else:
                    tickerSleepTimer = configKimchi.tickerSlowTimer
            else:
                if (tickerSleepTimer != configKimchi.tickerSleepTimer):
                    print(' -------------------------------[ Sleep Timer update: {0:>4} > {1:>4} ]-------------------------------'.format(tickerSleepTimer, configKimchi.tickerSleepTimer))
                    tickerSleepTimer = configKimchi.tickerSleepTimer

        time.sleep(tickerSleepTimer)
