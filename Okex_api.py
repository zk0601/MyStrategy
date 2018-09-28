import requests
import hashlib
from logs import log

logger = log()

class OKEX_API(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.url = 'https://www.okex.com/api/v1'
        self.apiKey = '9d503b22-f43c-4114-a352-70eaa9376104'
        self.secretKey = '95E58818F00DE5E4733A726EFC351369'
        self.header = {"Content-type": "application/x-www-form-urlencoded"}

    def buildMySign(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) + '&'
        data = sign + 'secret_key=' + self.secretKey
        return hashlib.md5(data.encode("utf8")).hexdigest().upper()

    def get_kline(self, interval, size=None, since=None):
        request_url = self.url + '/kline.do?symbol=%s&type=%s' % (self.symbol, interval)
        if size:
            request_url += '&size=%s' % str(size)
        if since:
            request_url += '&since=%s' % str(since)
        try:
            logger.info("GET Kline info for %s with %s interval" % (self.symbol, interval))
            res = requests.get(request_url, timeout=10)
            return res.json()
        except Exception as e:
            print(e)
            logger.error("GET Kline info Failed")
            return None

    def get_userinfo(self):
        post_data = dict()
        post_data['api_key'] = self.apiKey
        post_data['sign'] = self.buildMySign(post_data)
        request_url = self.url + '/userinfo.do'
        try:
            logger.info("Get user info")
            res = requests.post(request_url, data=post_data, headers=self.header, timeout=10)
            return res.json()
        except Exception as e:
            print(e)
            logger.error('Get user info Failed')
            return None

    def trade(self, type, **kwargs):
        post_data = dict()
        post_data['api_key'] = self.apiKey
        post_data['symbol'] = self.symbol
        post_data['type'] = type
        if type == 'buy_market':
            post_data['price'] = kwargs['price']
        if type == 'sell_market':
            post_data['amount'] = kwargs['amount']
        else:
            post_data['price'] = kwargs['price']
            post_data['amount'] = kwargs['amount']
        post_data['sign'] = self.buildMySign(post_data)
        request_url = self.url + '/trade.do'
        try:
            res = requests.post(request_url, data=post_data, headers=self.header, timeout=10)
            if res.json()["result"] is True:
                logger.info("Make %s trade successfully" % self.symbol)
                return res.json()["order_id"]
            else:
                logger.info("Make %s trade fail, Error code: %s" % (self.symbol, res.json()['error_code']))
                return None
        except Exception as e:
            logger.info("Make %s trade fail with  %s" % (self.symbol, e))
            return None


if __name__ == '__main__':
    a = OKEX_API('insur_usdt')
    print(a.get_kline('15min', 3))
    # # print(a.get_userinfo())
    # print(a.trade('sell_market', amount=100))
