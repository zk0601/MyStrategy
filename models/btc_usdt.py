from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, String, Integer, DECIMAL


Base = declarative_base()

class StrategyModel(Base):
    __tablename__ = 'strategy'

    id = Column(String, primary_key=True)
    btc_balance = Column(DECIMAL(16, 8), nullable=False)
    usdt_balance = Column(DECIMAL(16, 8), nullable=False)
    description = Column(String(255))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class KlineInfoModel(Base):
    __tablename__ = 'kline_info'

    id = Column(Integer, primary_key=True)
    timestamp = Column(String, nullable=False)
    open_value = Column(DECIMAL(10, 2), nullable=False)
    high_value = Column(DECIMAL(10, 2), nullable=False)
    low_value = Column(DECIMAL(10, 2), nullable=False)
    close_value = Column(DECIMAL(10, 2), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    interval = Column(String, nullable=False)
    from_strategy_id = Column(String, ForeignKey('strategy.id'))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TradeModel(Base):
    __tablename__ = 'trade'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    price = Column(DECIMAL(16, 8), nullable=False)
    amount = Column(DECIMAL(16, 8), nullable=False)
    time_str = Column(String, nullable=False)
    from_strategy_id = Column(String, ForeignKey('strategy.id'))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
