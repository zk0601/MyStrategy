import time
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from Okex_api import OKEX_API
from logs import log
from models.btc_usdt import StrategyModel, KlineInfoModel, TradeModel

logger = log()


class MysqlConnection(object):
    def __init__(self):
        mysql_user = 'root'
        mysql_password = '123456'
        mysql_host = '47.91.252.155'
        mysql_database = 'btc_usdt_strategy'
        database_url = 'mysql+mysqldb://{}:{}@{}/{}?charset=utf8'.format(mysql_user, mysql_password, mysql_host, mysql_database)
        engine = create_engine(database_url, encoding="utf8", echo=False, pool_size=5)
        DBSession = scoped_session(sessionmaker(bind=engine, autocommit=False))
        self.session = DBSession()

    def get_user_balance(self, strategy_id):
        strategy = self.session.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
        return {'btc': strategy.btc_balance, 'usdt': strategy.usdt_balance}

    def save_kline_data(self, strategy_id, **kwargs):
        try:
            timestamp = kwargs['timestamp']
            open_value = kwargs['open_value']
            high_value = kwargs['high_value']
            low_value = kwargs['low_value']
            close_value = kwargs['close_value']
            amount = kwargs['amount']
            interval = kwargs['interval']
            kline_data = KlineInfoModel(timestamp=timestamp, open_value=open_value, high_value=high_value,low_value=low_value,
                                         close_value=close_value, amount=amount, interval=interval, from_strategy_id=strategy_id)
            self.session.add(kline_data)
            self.session.commit()
        except Exception as e:
            logger.error("Save kline data Failed because of %s" % e)

    def trade_record(self, strategy_id, **kwargs):
        try:
            type = kwargs['type']
            price = kwargs['price']
            amount = kwargs['amount']
            time_str = kwargs['time_str']
            trade = TradeModel(type=type, price=price, amount=amount, time_str=time_str, from_strategy_id=strategy_id)
            self.session.add(trade)
            self.session.commit()
        except Exception as e:
            logger.error("Save trade data Failed because of %s" % e)

    def trade_mock(self, strategy_id, **kwargs):
        try:
            type = kwargs['type']
            price = kwargs['price']
            amount = kwargs['amount']
            balance = self.get_user_balance(strategy_id)
            if type == 'buy':
                balance['usdt'] = float(balance['usdt']) - round(float(amount), 8)
                balance['btc'] = float(balance['btc']) + round(float(amount / float(price)), 8)
            if type == 'sell':
                balance['btc'] = float(balance['btc']) - round(float(amount), 8)
                balance['usdt'] = float(balance['usdt']) + round(float(amount * float(price)), 8)
            strategy = self.session.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
            strategy.btc_balance = balance['btc']
            strategy.usdt_balance = balance['usdt']
            self.session.commit()
            logger.info('Finish trade %s %s with %s btc/sudt' % (type, amount, price))
        except Exception as e:
            self.session.rollback()
            logger.error('Trade Failed because of %s' % e)


class MyStrategy(MysqlConnection):
    def __init__(self):
        super(MyStrategy, self).__init__()
        self.time_format = "%Y%m%d %H:%M"
        self.now_time_str = datetime.datetime.now().strftime(self.time_format)
        self.last_candle_time = datetime.datetime.strptime(self.now_time_str, self.time_format) + datetime.timedelta(minutes=-1)
        self.last_candle_time_stamp = int(time.mktime(self.last_candle_time.timetuple()))

    def strategy_1(self):
        symbol = OKEX_API('btc_usdt')
        interval = '15min'
        trade_percent = 0.5
        time_count = 0
        while True:
            kline_info = symbol.get_kline(interval, 3)
            if not kline_info[-1][0] == self.last_candle_time_stamp * 1000:
                time.sleep(5)
                time_count += 5
                if time_count == 25:
                    return
                continue
            break
        first_candle, second_candle, third_candle = kline_info[0], kline_info[1], kline_info[2]
        self.save_kline_data("1", timestamp=str(third_candle[0]), open_value=round(float(third_candle[1]), 2),
                             high_value=round(float(third_candle[2]), 2), low_value=round(float(third_candle[3]), 2),
                             close_value=round(float(third_candle[4]), 2), amount=round(float(third_candle[5]), 2),
                             interval=interval)
        if float(first_candle[-1]) * 1.5 <= float(second_candle[-1]) and float(second_candle[-1]) * 1.5 <= float(third_candle[-1]):
            if float(first_candle[-2]) < float(second_candle[-2]) < float(third_candle[-2]):
                logger.info("Close price: %s, %s, %s.  Trade amount: %s, %s, %s" %
                            (first_candle[-2], second_candle[-2], third_candle[-2], first_candle[-1], second_candle[-1], third_candle[-1]))
                logger.info("There's a sign of buy")
                buy_price = symbol.get_market_info()['buy']
                usdt_amount = float(self.get_user_balance("1")['usdt']) * trade_percent
                self.trade_mock("1", type='buy', price=buy_price, amount=usdt_amount)
                self.trade_record("1", type='buy', price=buy_price, amount=usdt_amount,time_str=self.now_time_str)
                return

            if float(first_candle[-2]) > float(second_candle[-2]) > float(third_candle[-2]):
                logger.info("Close price: %s, %s, %s.  Trade amount: %s, %s, %s" %
                            (first_candle[-2], second_candle[-2], third_candle[-2], first_candle[-1], second_candle[-1], third_candle[-1]))
                logger.info("There's a sign of sell")
                sell_price = symbol.get_market_info()['sell']
                btc_amount = float(self.get_user_balance("1")['btc']) * trade_percent
                self.trade_mock("1", type='sell', price=sell_price, amount=btc_amount)
                self.trade_record("1", type='sell', price=sell_price, amount=btc_amount,time_str=self.now_time_str)
                return

            logger.info("Close price: %s, %s, %s.  Trade amount: %s, %s, %s" %
                        (first_candle[-2], second_candle[-2], third_candle[-2], first_candle[-1], second_candle[-1], third_candle[-1]))
            logger.info("There're no trade sign")
        else:
            logger.info("Close price: %s, %s, %s.  Trade amount: %s, %s, %s" %
                        (first_candle[-2], second_candle[-2], third_candle[-2], first_candle[-1], second_candle[-1], third_candle[-1]))
            logger.info("There're no trade sign")
            return


if __name__ == '__main__':
    my = MyStrategy()
    my.strategy_1()
