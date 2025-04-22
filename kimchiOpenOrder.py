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
import binanceTradingRules

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

# OPEN KIMCHI
def openKimchi(ticker, upbit, orderPrice, tradePosition, rateKrw, upbitStopLossUUID, prevKimchi, targetKimchi):
    ####################################### [ Order section ] #######################################

    kimchi              = 0.0
    binancePositionSize = 0.0
    emptyBalance        = 0

    tryCount            = 0

    # Calculate order size
    binanceStepSize = float(binanceTradingRules.binanceStepSize.get(ticker))
    kimchiOrderSize = f'{(configKimchi.kimchiOrderPrice / upbit // binanceStepSize * binanceStepSize):.3f}'

    # Order Binance open Short position
    try:
        resOrderBinanceSell = client.futures_create_order(
            symbol = ticker + 'USDT',
            side = 'SELL',
            type = 'MARKET',
            quantity = kimchiOrderSize
        )
        # print('Order BINANCE Sell\n', resOrderBinanceSell)
    except Exception as e:
        if (('code=-2019' in str(e)) or ('code=-4003' in str(e))):
            emptyBalance = 1
            return upbitStopLossUUID, kimchi, binancePositionSize, emptyBalance, FAILURE
        else:
            nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
            now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
            if (tradePosition == 0):
                if (configKimchi.ticker1 == ticker):
                    print('Warning  ' + f'{ticker:<5}', 'BINANCE failed Sell order and Cancel order - kimchi_1 |', now)
                elif (configKimchi.ticker2 == ticker):
                    print('Warning  ' + f'{ticker:<5}', 'BINANCE failed Sell order and Cancel order - kimchi_2 |', now)
                else:
                    print('Warning  ' + f'{ticker:<5}', 'BINANCE failed Sell order and Cancel order - kimchi_3 |', now)
            else:
                if (configKimchi.ticker1 == ticker):
                    print('Warning #' + f'{ticker:<5}', 'BINANCE failed Sell order and Cancel order - kimchi_1 |', now)
                elif (configKimchi.ticker2 == ticker):
                    print('Warning #' + f'{ticker:<5}', 'BINANCE failed Sell order and Cancel order - kimchi_2 |', now)
                else:
                    print('Warning #' + f'{ticker:<5}', 'BINANCE failed Sell order and Cancel order - kimchi_3 |', now)
            time.sleep(config.errorRetryTimer)
            return upbitStopLossUUID, kimchi, binancePositionSize, emptyBalance, FAILURE

    # Order Upbit bid
    params = {
        'market': 'KRW-' + ticker,
        'side': 'bid',
        'volume': kimchiOrderSize,
        'price': orderPrice,
        'ord_type': 'limit'
    }
    resUpbitBid = apiUpbit.upbitOrder(params)
    # print('Order UPBIT Bid\n', resUpbitBid)
    if (resUpbitBid.get('error')):
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

        while True:
            if (configKimchi.ticker1 == ticker):
                if (not os.path.isfile('orderId_kimchi_1.pickle')):
                    time.sleep(config.errorRetryTimer)
                else:
                    os.remove('orderId_kimchi_1.pickle')
                    break
            elif (configKimchi.ticker2 == ticker):
                if (not os.path.isfile('orderId_kimchi_2.pickle')):
                    time.sleep(config.errorRetryTimer)
                else:
                    os.remove('orderId_kimchi_2.pickle')
                    break
            else:
                if (not os.path.isfile('orderId_kimchi_3.pickle')):
                    time.sleep(config.errorRetryTimer)
                else:
                    os.remove('orderId_kimchi_3.pickle')
                    break

        if (resUpbitBid.get('error').get('name') == 'insufficient_funds_bid'):
            emptyBalance = 2
            return upbitStopLossUUID, kimchi, binancePositionSize, emptyBalance, FAILURE
        else:
            nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
            now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
            if (tradePosition == 0):
                if (configKimchi.ticker1 == ticker):
                    print('Warning  ' + f'{ticker:<5}', 'UPBIT failed Bid order, Cancel Open Kimchi - kimchi_1 |', now)
                elif (configKimchi.ticker2 == ticker):
                    print('Warning  ' + f'{ticker:<5}', 'UPBIT failed Bid order, Cancel Open Kimchi - kimchi_2 |', now)
                else:
                    print('Warning  ' + f'{ticker:<5}', 'UPBIT failed Bid order, Cancel Open Kimchi - kimchi_3 |', now)
            else:
                if (configKimchi.ticker1 == ticker):
                    print('Warning #' + f'{ticker:<5}', 'UPBIT failed Bid order, Cancel Open Kimchi - kimchi_1 |', now)
                elif (configKimchi.ticker2 == ticker):
                    print('Warning #' + f'{ticker:<5}', 'UPBIT failed Bid order, Cancel Open Kimchi - kimchi_2 |', now)
                else:
                    print('Warning #' + f'{ticker:<5}', 'UPBIT failed Bid order, Cancel Open Kimchi - kimchi_3 |', now)
            return upbitStopLossUUID, kimchi, binancePositionSize, emptyBalance, FAILURE

    time.sleep(config.errorRetryTimer)

    ###################################### [ Inquiry section ] ######################################

    # Upbit Inquiry order
    while True:
        params = {
            'uuid': resUpbitBid.get('uuid')
        }
        infoUpbitInquiry = apiUpbit.upbitInquiryOrder(params)
        # print('Inquiry UPBIT order\n', infoUpbitInquiry)
        upbitTradesSize = infoUpbitInquiry.get('executed_volume')
        if (float(upbitTradesSize) == float(kimchiOrderSize)):
            for info in infoUpbitInquiry.get('trades'):
                upbitTradesPrice = info.get('price')
            break
        else:
            tryCount = tryCount + 1
            if (tryCount == 60):
                # Cancel Order Upbit bid
                while True:
                    params = {
                        'uuid': resUpbitBid.get('uuid')
                    }
                    resUpbitDelete = apiUpbit.upbitCancelOrder(params)
                    # print('Delete UPBIT order\n', resUpbitDelete)
                    if (resUpbitDelete.get('error')):
                        nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                        now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                        if (tradePosition == 0):
                            if (configKimchi.ticker1 == ticker):
                                print('Warning  ' + f'{ticker:<5}', 'UPBIT failed Bid order Cancel and ReCancel - kimchi_1 |', now)
                            elif (configKimchi.ticker2 == ticker):
                                print('Warning  ' + f'{ticker:<5}', 'UPBIT failed Bid order Cancel and ReCancel - kimchi_2 |', now)
                            else:
                                print('Warning  ' + f'{ticker:<5}', 'UPBIT failed Bid order Cancel and ReCancel - kimchi_3 |', now)
                        else:
                            if (configKimchi.ticker1 == ticker):
                                print('Warning #' + f'{ticker:<5}', 'UPBIT failed Bid order Cancel and ReCancel - kimchi_1 |', now)
                            elif (configKimchi.ticker2 == ticker):
                                print('Warning #' + f'{ticker:<5}', 'UPBIT failed Bid order Cancel and ReCancel - kimchi_2 |', now)
                            else:
                                print('Warning #' + f'{ticker:<5}', 'UPBIT failed Bid order Cancel and ReCancel - kimchi_3 |', now)
                        time.sleep(config.errorRetryTimer)
                    else:
                        break

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
                        binancePositionUnRealizedProfit = float(inf.get('unRealizedProfit'))
                        binanceUnRealizedProfit = f'{binancePositionUnRealizedProfit:.2f}'

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

                while True:
                    if (configKimchi.ticker1 == ticker):
                        if (not os.path.isfile('orderId_kimchi_1.pickle')):
                            time.sleep(config.errorRetryTimer)
                        else:
                            os.remove('orderId_kimchi_1.pickle')
                            break
                    elif (configKimchi.ticker2 == ticker):
                        if (not os.path.isfile('orderId_kimchi_2.pickle')):
                            time.sleep(config.errorRetryTimer)
                        else:
                            os.remove('orderId_kimchi_2.pickle')
                            break
                    else:
                        if (not os.path.isfile('orderId_kimchi_3.pickle')):
                            time.sleep(config.errorRetryTimer)
                        else:
                            os.remove('orderId_kimchi_3.pickle')
                            break

                nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
                now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
                if (tradePosition == 0):
                    print('Warning  ' + f'{ticker:<5}', 'Upbit not Full Filled, Binance unRealized:', f'{binanceUnRealizedProfit:>5}', 'USDT |', now)
                    title   = Array('c', b'UPBIT not Filled: ' + ticker.encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                    message = Array('c', b'Warning UPBIT not Full Filled, Binance unRealizedProfit: ' + str(binanceUnRealizedProfit).encode("utf-8") + b' USDT')
                else:
                    print('Warning #' + f'{ticker:<5}', 'Upbit not Full Filled, Binance unRealized:', f'{binanceUnRealizedProfit:>5}', 'USDT |', now)
                    title   = Array('c', b'UPBIT not Filled: #' + ticker.encode("utf-8") + b' ' + str(lightSailsName).encode("utf-8"))
                    message = Array('c', b'Warning UPBIT not Full Filled, Binance unRealizedProfit: ' + str(binanceUnRealizedProfit).encode("utf-8") + b' USDT')
                p6 = Process(target = sendGmailReport, args = (title, message))
                p6.start()
                p6.join()
                time.sleep(config.errorRetryTimer)
                return upbitStopLossUUID, kimchi, binancePositionSize, emptyBalance, FAILURE

            time.sleep(config.errorRetryTimer)

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

    # Upbit Balance
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
    binanceBalance = info['totalWalletBalance']

    time.sleep(config.errorRetryTimer)

    ################################## [ Order Stop Loss section ] ##################################
    
    # Order Binance cancel all open orders
    if (tradePosition == 1):
        while True:
            try:
                resOrderBinanceCancel = client.futures_cancel_all_open_orders(
                    symbol = ticker + 'USDT'
                )
                # print('Order BINANCE Cancel for Stop Loss\n', resOrderBinanceCancel)
            except:
                time.sleep(config.errorRetryTimer)
            else:
                break

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

    # Order Binance buy for Stop Loss
    # Calculate order size
    binancePriceMove = float(binanceTradingRules.binancePriceMove.get(ticker))
    binanceStopLoss  = f'{(float(binancePositionLiqui) * 0.95 // binancePriceMove * binancePriceMove):.6f}'

    while True:
        try:
            resOrderBinanceBuy = client.futures_create_order(
                symbol = ticker + 'USDT',
                side = 'BUY',
                type = 'STOP_MARKET',
                stopPrice = binanceStopLoss,
                closePosition = 'true'
            )
            # print('Order BINANCE Sell for Stop Loss\n', resOrderBinanceBuy)
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break

    # Order Upbit cancel open orders
    if (tradePosition == 1):
        params = {
            'uuid': upbitStopLossUUID
        }
        resOrderUpbitCancel = apiUpbit.upbitCancelOrder(params)
        # print('Order UPBIT Cancel for Stop Loss\n', resOrderUpbitCancel)

    # Order Upbit ask for Stop Loss
    upbitStopLoss = config.calUpbitPriceMove(float(binanceStopLoss) * float(rateKrw))
    upbitStopLossVolume = -float(binancePositionSize)

    while True:
        params = {
            'market': 'KRW-' + ticker,
            'side': 'ask',
            'volume': upbitStopLossVolume,
            'price': upbitStopLoss,
            'ord_type': 'limit'
        }
        resUpbitSLAsk = apiUpbit.upbitOrder(params)
        if (resUpbitSLAsk.get('error')):
            time.sleep(config.errorRetryTimer)
        else:
            break
    # print('Order UPBIT Ask for Stop Loss\n', resUpbitSLAsk)
    upbitStopLossUUID = resUpbitSLAsk.get('uuid')

    # Binance Inquiry Last Funding Rate
    while True:
        try:
            info = client.futures_mark_price(
                symbol = ticker + 'USDT'
            )
        except:
            time.sleep(config.errorRetryTimer)
        else:
            break
    lastFundingRate = float(info.get('lastFundingRate')) * 100
    # print('Last FundingRate: ', lastFundingRate)

    ####################################### [ Gmail section ] #######################################

    # Send Gmail report
    if (tradePosition == 0):
        positionName = ''
    else:
        positionName = 'Add'

    tickerName    = ticker.encode("utf-8")
    leverage      = str(config.futureLeverage).encode("utf-8")
    upbit         = str(upbitTradesPrice).encode("utf-8")
    upbitSize     = str(upbitTradesSize).encode("utf-8")
    tradePri      = float(upbitTradesPrice) * float(upbitTradesSize)
    tradePric     = format(math.trunc(tradePri), ',')
    tradePrice    = str(tradePric).encode("utf-8")
    binance       = str(binanceTradesPrice).encode("utf-8")
    binanceSize   = str(binanceTradesSize).encode("utf-8")
    positionPrice = str(binancePositionPrice).encode("utf-8")
    positionSize  = str(binancePositionSize).encode("utf-8")
    positionLiqui = str(binancePositionLiqui).encode("utf-8")
    rateKRW       = str(rateKrw).encode("utf-8")
    lastFunding   = str(f'{lastFundingRate:.4f}').encode("utf-8")
    tradePosName  = str(positionName).encode("utf-8")

    kimchi        = (float(upbitTradesPrice) / float(binanceTradesPrice) / float(rateKrw) - 1) * 100
    if (tradePosition == 1):
        kimchi    = (kimchi + prevKimchi) / 2
    kimchiValue   = str(f'{kimchi:.2f}').encode("utf-8")

    targetKimchiV = str(f'{targetKimchi:.2f}').encode("utf-8")

    totalBal      = float(upbitBalance) + (float(binanceBalance) * rateKrw) + tradePri
    totalBall     = format(math.trunc(totalBal), ',')
    totalBalance  = str(totalBall).encode("utf-8")

    title   = Array('c', tradePosName + b' Open Kimchi: ' + tickerName + b' ' + leverage + b'X ' + str(lightSailsName).encode("utf-8"))
    message = Array('c', b'Total Balance: ' + totalBalance + b' KRW' + b'\n\n' +
                    b' Kimchi: ' + kimchiValue + b' % (' + targetKimchiV + b'), USD/KRW: ' + rateKRW + b'\n\n' + 
                    b' UPBIT: ' + upbit + b', Size: ' + upbitSize + b', Price: ' + tradePrice + b' KRW' + b'\n' +
                    b' BINANCE: ' + binance + b', Size: ' + binanceSize + b'\n\n' + 
                    b' Setting POSITION: ' + positionPrice + b', Size: ' + positionSize + b'\n' +
                    b'\t' + b'Liquid: ' + positionLiqui + b'\n\n' + 
                    b' Funding Rate: ' + lastFunding + b' %')
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

    f.write(str(now) + ' | ' + '{0:<5}'.format(ticker) + ' | ' + str(config.futureLeverage) +  'X | ' + 'OPEN ' + ' | ' +
            'Total Balance: ' + str(totalBall) + ' KRW' + ' | ' +
            'Kimchi: ' + str(f'{kimchi:.2f}') + ' | ' + 'USD/KRW: ' + str(rateKrw) + ' | ' + 
            'UPBIT: ' + str(upbitTradesPrice) + ' | ' + 'Size: ' + str(upbitTradesSize) + ' | ' +
            'BINANCE: ' + str(binanceTradesPrice) + ' | ' + 'Size: ' + str(binanceTradesSize) + ' | ' +
            'Setting POSITION: ' + str(binancePositionPrice) + ' | ' + 'Size: ' + str(binancePositionSize) + ' | ' +
            'Liquid: ' + str(binancePositionLiqui) + ' | ' + 'Funding Rate: ' + str(f'{lastFundingRate:.4f}') + '\n')
    f.close()

    ####################################### [ Print section ] #######################################
    kimChi = f'{kimchi:.2f}'

    if (tradePosition == 0):
        if (configKimchi.ticker1 == ticker):
            print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Open  Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_1')
        elif (configKimchi.ticker2 == ticker):
            print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Open  Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_2')
        else:
            print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Open  Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_3')
    else:
        if (configKimchi.ticker1 == ticker):
            print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Open2 Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_1')
        elif (configKimchi.ticker2 == ticker):
            print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Open2 Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_2')
        else:
            print('→' + now, '|', f'{ticker:<5}', '| $:', f'{rateKrw:<7}', '| Open2 Order | O:', f'{kimChi:>5}', '% |', getStatusDW(ticker), '| kimchi_3')

    return upbitStopLossUUID, kimchi, binancePositionSize, emptyBalance, SUCCESS
