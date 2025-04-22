from binance.client import Client

import time
import requests
import json
import config

def checkTimeInterval():
    url = "https://api.binance.com/api/v1/time"
    t = time.time() * 1000
    r = requests.get(url)

    result = json.loads(r.content)
    return (int(t) - result["serverTime"])

class Binance:
    def __init__(self, public_key = '', secret_key = '', sync = False):
        self.time_offset = 0
        while True:
            try:
                self.b = Client(public_key, secret_key)
            except:
                time.sleep(config.errorRetryTimer)
            else:
                break
        if sync:
            self.time_offset = self._get_time_offset()

    def _get_time_offset(self):
        res = self.b.get_server_time()
        return res['serverTime'] - int(time.time() * 1000)

    def synced(self, fn_name, **args):
        args['timestamp'] = int(time.time() - self.time_offset)
        return getattr(self.b, fn_name)(**args)
