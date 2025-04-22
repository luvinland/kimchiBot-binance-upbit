import time
import datetime
import requests
import config

from pytz import timezone
from bs4 import BeautifulSoup

def getGoogleKRWUSD():
    params = {
        "q": "환율 1달러",
        "hl": "ko"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    }

    while True:
        try:
            soup = BeautifulSoup(requests.get('https://www.google.com/search', params = params, headers = headers).text, 'lxml')
            krwUsd = float(soup.select_one('.SwHCTb').text.replace(',', ''))
        except:
            nowRaw = datetime.datetime.now(timezone('Asia/Seoul'))
            now = '{0}-{1:>02}-{2:>02} {3:>02}:{4:>02}:{5:>02}'.format(nowRaw.year, nowRaw.month, nowRaw.day, nowRaw.hour, nowRaw.minute, nowRaw.second)
            print('Warning Google KRWUSD rate Crawling fail and Re-try Crawling |', now)
            time.sleep(config.rateKrwSleepTimer)
        else:
            break

    return krwUsd
