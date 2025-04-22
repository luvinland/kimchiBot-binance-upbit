from sre_constants import FAILURE, SUCCESS
from binance.client import Client
from multiprocessing import Process, Array
from pytz import timezone

import os
import time
import datetime
import math
import pickle
import apiUpbit
import config
import configKimchi
import gmailReport

while True:
    try:
        client = Client(config.binanceApiKey, config.binanceSecretKey)
    except:
        time.sleep(config.errorRetryTimer)
    else:
        break

lightSailsName = os.environ.get('LIGHTSAILSNAME')

# GMAIL
def sendGmailReport(title, message):
    gmailReport.gmailReportSending(title, message)

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

# CLOSE KIMCHI
def closeKimchi(ticker, orderSize, rateKrw, newRateKrw, upbitStopLossUUID, targetKimchi):
    ####################################### [ Order section ] #######################################

    # Close order size
    kimchiOrderSize = -float(orderSize)

    # Order Upbit cancel open orders
    params = {
        'uuid': upbitStopLossUUID
    }
    resOrderUpbitCancel = apiUpbit.upbitCancelOrder(params)
    # print('Order UPBIT cancel\n', resOrderUpbitCancel)

    # Order Binance close Short position
    while True:
        try:
            resOrderBinanceBuy = client.futures_create_order(
                symbol = ticker + 'USDT',
                type = 'MARKET',
                side = 'BUY',
                quantity = kimchiOrderSize
            )
            # print('Order BINANCE Buy\n', resOrderBinanceBuy)
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    # Order Upbit ask
    while True:
        params = {
            'market': 'KRW-' + ticker,
            'side': 'ask',
            'volume': kimchiOrderSize,
            'ord_type': 'market'
        }
        resUpbitAsk = apiUpbit.upbitOrder(params)
        # print('Order UPBIT Ask\n', resUpbitAsk)
        if (resUpbitAsk.get('error')):
            time.sleep(config.errorRetryTimer)
        else:
            break

    time.sleep(config.errorRetryTimer)

    ####################################### [ Inquiry section ] #######################################
    
    # Binance Inquiry order
    while True:
        try:
            if (configKimchi.ticker1 == ticker):
                orderID = open('orderId_kimchi_1.pickle', 'rb')
            elif (configKimchi.ticker2 == ticker):
                orderID = open('orderId_kimchi_2.pickle', 'rb')
            else:
                orderID = open('orderId_kimchi_3.pickle', 'rb')
        except:
            if (configKimchi.ticker1 == ticker):
                time.sleep(config.errorRetryTimer)
            elif (configKimchi.ticker2 == ticker):
                time.sleep(config.errorRetryTimer * 2)
            else:
                time.sleep(config.errorRetryTimer * 3)
        else:
            break

    data_read = pickle.load(orderID)
    orderID.close()

    while True:
        try:
            infoBinanceInquiry = client.futures_get_order(
                symbol = ticker + 'USDT',
                orderId = data_read.get('i')
            )
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break
    # print('Inquiry BINANCE order\n', infoBinanceInquiry)
    binanceTradesPrice = infoBinanceInquiry.get('avgPrice')
    binanceTradesSize  = infoBinanceInquiry.get('executedQty')

    if (configKimchi.ticker1 == ticker):
        os.remove('orderId_kimchi_1.pickle')
    elif (configKimchi.ticker2 == ticker):
        os.remove('orderId_kimchi_2.pickle')
    else:
        os.remove('orderId_kimchi_3.pickle')

    # Upbit Inquiry order
    params = {
        'uuid': resUpbitAsk.get('uuid')
    }
    infoUpbitInquiry = apiUpbit.upbitInquiryOrder(params)
    # print('UPBIT inquiry order\n', infoUpbitInquiry)
    for info in infoUpbitInquiry.get('trades'):
        upbitTradesPrice = info.get('price')
        upbitTradesSize = info.get('volume')

    # Binance Balance
    while True:
        try:
            info = client.futures_account()
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break
    binanceBalance = info.get('totalWalletBalance')

    # Upbit Balance
    for inf in apiUpbit.upbitBalance():
        if (inf.get('currency') == 'KRW'):
            upbitBalance = inf.get('balance')

    # Binance Inquiry position
    while True:
        try:
            info = client.futures_position_information(
                symbol = ticker + 'USDT'
            )
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break
    for inf in info:
        if (inf.get('symbol') == ticker + 'USDT'):
            binancePositionPrice = inf.get('entryPrice')
            binancePositionSize  = inf.get('positionAmt')
            binancePositionLiqui = inf.get('liquidationPrice')
    # print('Inquiry BINANCE position\n', info)

    # Order Binance cancel all open orders
    while True:
        try:
            resOrderBinanceCancel = client.futures_cancel_all_open_orders(
                symbol = ticker + 'USDT'
            )
            # print('Order BINANCE Cancel\n', resOrderBinanceCancel)
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    ####################################### [ Gmail section ] #######################################

    # Send Gmail report
    tickerName    = ticker.encode("utf-8")
    leverage      = str(config.futureLeverage).encode("utf-8")
    upbit         = str(upbitTradesPrice).encode("utf-8")
    upbitSize     = str(upbitTradesSize).encode("utf-8")
    binance       = str(binanceTradesPrice).encode("utf-8")
    binanceSize   = str(binanceTradesSize).encode("utf-8")
    positionPrice = str(binancePositionPrice).encode("utf-8")
    positionSize  = str(binancePositionSize).encode("utf-8")
    positionLiqui = str(binancePositionLiqui).encode("utf-8")
    newRateKRW    = str(newRateKrw).encode("utf-8")
    rateKRW       = str(rateKrw).encode("utf-8")

    kimchi        = (float(upbitTradesPrice) / float(binanceTradesPrice) / float(rateKrw) - 1) * 100
    kimchiValue   = str(f'{kimchi:.2f}').encode("utf-8")

    targetKimchiV = str(f'{targetKimchi:.2f}').encode("utf-8")

    totalBal      = float(upbitBalance) + (float(binanceBalance) * newRateKrw)
    totalBall     = format(math.trunc(totalBal), ',')
    totalBalance  = str(totalBall).encode("utf-8")

    title   = Array('c', b'Close Kimchi: ' + tickerName + b' ' + leverage + b'X ' + str(lightSailsName).encode("utf-8"))
    message = Array('c', b'Total Balance: ' + totalBalance + b' KRW' + b'\n\n' +
                    b' Kimchi: ' + kimchiValue + b' % (' + targetKimchiV + b'), USD/KRW: ' + rateKRW + b'\n' +
                    b' Now USD/KRW: ' + newRateKRW + b'\n\n' +
                    b' UPBIT: ' + upbit + b', Size: ' + upbitSize + b'\n' +
                    b' BINANCE: ' + binance + b', Size: ' + binanceSize + b'\n\n' + 
                    b' Remainning POSITION: ' + positionPrice + b', Size: ' + positionSize + b'\n' +
                    b'\t' + b'Liquid: ' + positionLiqui)
    p6 = Process(target = sendGmailReport, args = (title, message))
    p6.start()
    p6.join()
    # print('Sent Report.')

    ######################################## [ Log section ] ########################################

    nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
    now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
    while True:
        try:
            f = open('log.txt', 'a')
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    f.write(str(now) + ' | ' + '{0:<5}'.format(ticker) + ' | ' + str(config.futureLeverage) +  'X | ' + 'CLOSE' + ' | ' +
            'Total Balance: ' + str(totalBall) + ' KRW' + ' | ' +
            'Kimchi: ' + str(f'{kimchi:.2f}') + ' | ' + 'USD/KRW: ' + str(rateKrw) + ' | ' + 
            'UPBIT: ' + str(upbitTradesPrice) + ' | ' + 'Size: ' + str(upbitTradesSize) + ' | ' +
            'BINANCE: ' + str(binanceTradesPrice) + ' | ' + 'Size: ' + str(binanceTradesSize) + ' | ' +
            'Setting POSITION: ' + str(binancePositionPrice) + ' | ' + 'Size: ' + str(binancePositionSize) + ' | ' +
            'Liquid: ' + str(binancePositionLiqui) + '\n')
    f.close()

    ####################################### [ Print section ] #######################################
    kimChi = f'{kimchi:.2f}'

    if (configKimchi.ticker1 == ticker):
        print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Close Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_1')
    elif (configKimchi.ticker2 == ticker):
        print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Close Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_2')
    else:
        print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Close Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_3')

    return SUCCESS
