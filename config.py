binanceApiKey     = ''
binanceSecretKey  = ''

upbitAccessKey    = ''
upbitSecretKey    = ''

bithumbConnectKey = ''
bithumbSecretKey  = ''

gmailAccount      = '@gmail.com'
gmailAppPassword  = ''

futureLeverage    = 4
futureMarginType  = 'ISOLATED'

aliveSleepTimer   = 3000
rateKrwSleepTimer = 60
errorRetryTimer   = 1.0

def calUpbitPriceMove(upbitStopLossPrice):
    if (upbitStopLossPrice >= 2000000.0):
        return f'{(upbitStopLossPrice // 1000 * 1000):.8f}'
    elif (upbitStopLossPrice >= 1000000.0 and upbitStopLossPrice < 2000000.0):
        return f'{(upbitStopLossPrice // 500 * 500):.8f}'
    elif (upbitStopLossPrice >= 500000.0 and upbitStopLossPrice < 1000000.0):
        return f'{(upbitStopLossPrice // 100 * 100):.8f}'
    elif (upbitStopLossPrice >= 100000.0 and upbitStopLossPrice < 500000.0):
        return f'{(upbitStopLossPrice // 50 * 50):.8f}'
    elif (upbitStopLossPrice >= 10000.0 and upbitStopLossPrice < 100000.0):
        return f'{(upbitStopLossPrice // 10 * 10):.8f}'
    elif (upbitStopLossPrice >= 1000.0 and upbitStopLossPrice < 10000.0):
        return f'{(upbitStopLossPrice // 1 * 1):.8f}'
    elif (upbitStopLossPrice >= 100.0 and upbitStopLossPrice < 1000.0):
        return f'{(upbitStopLossPrice // 0.1 * 0.1):.8f}'
    elif (upbitStopLossPrice >= 10.0 and upbitStopLossPrice < 100.0):
        return f'{(upbitStopLossPrice // 0.01 * 0.01):.8f}'
    elif (upbitStopLossPrice >= 1.0 and upbitStopLossPrice < 10.0):
        return f'{(upbitStopLossPrice // 0.001 * 0.001):.8f}'
    elif (upbitStopLossPrice >= 0.1 and upbitStopLossPrice < 1.0):
        return f'{(upbitStopLossPrice // 0.0001 * 0.0001):.8f}'
    elif (upbitStopLossPrice >= 0.01 and upbitStopLossPrice < 0.1):
        return f'{(upbitStopLossPrice // 0.00001 * 0.00001):.8f}'
    elif (upbitStopLossPrice >= 0.001 and upbitStopLossPrice < 0.01):
        return f'{(upbitStopLossPrice // 0.000001 * 0.000001):.8f}'
    elif (upbitStopLossPrice >= 0.0001 and upbitStopLossPrice < 0.001):
        return f'{(upbitStopLossPrice // 0.0000001 * 0.0000001):.8f}'
    elif (upbitStopLossPrice > 0 and upbitStopLossPrice < 0.0001):
        return f'{(upbitStopLossPrice // 0.00000001 * 0.00000001):.8f}'
    else:
        return 0
