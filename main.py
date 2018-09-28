import time
import datetime
from Okex_api import OKEX_API
from logs import log

logger = log()


class MyStrategy(object):
    def __init__(self):
        self.time_format = "%Y%m%d %H%M"
        self.last_candle_time = datetime.datetime.strptime(datetime.datetime.now().strftime(self.time_format), self.time_format) \
                                + datetime.timedelta(minutes=-1)
        self.last_candle_time_stamp = int(time.mktime(self.last_candle_time.timetuple()))

    def btc_usdt(self):
        symbol = OKEX_API('btc_usdt')
        sell_amount = 5
        buy_price = 50000
        while True:
            kline_info = symbol.get_kline('15min', 3)
            if not kline_info[-1][0] == self.last_candle_time_stamp * 1000:
                continue
            break
        first_candle, second_candle, third_candle = kline_info[0], kline_info[1], kline_info[2]
        if float(first_candle[-1]) * 1.5 <= float(second_candle[-1]) and float(second_candle[-1]) * 1.5 <= float(third_candle):
            if float(first_candle[-2]) < float(second_candle[-2]) < float(third_candle[-2]):
                logger.info("Close price: %s, %s, %s.  Trade amount: %s, %s, %s" %
                            (first_candle[-2], second_candle[-2], third_candle[-2], first_candle[-1], second_candle[-1], third_candle[-1]))
                logger.info("There's a sign of buy")
                symbol.trade('buy_market', price=buy_price)
            if float(first_candle[-2]) > float(second_candle[-2]) > float(third_candle[-2]):
                logger.info("Close price: %s, %s, %s.  Trade amount: %s, %s, %s" %
                            (first_candle[-2], second_candle[-2], third_candle[-2], first_candle[-1], second_candle[-1], third_candle[-1]))
                logger.info("There's a sign of sell")
                symbol.trade('sell_market', amount=sell_amount)
        else:
            logger.info("Close price: %s, %s, %s.  Trade amount: %s, %s, %s" %
                        (first_candle[-2], second_candle[-2], third_candle[-2], first_candle[-1], second_candle[-1], third_candle[-1]))
            logger.info("There're no trade sign")
            return

