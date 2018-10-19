from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


mysql_user = 'root'
mysql_password = '123456'
mysql_host = '47.91.252.155'
mysql_database = 'btc_usdt_strategy'
database_url = 'mysql+mysqldb://{}:{}@{}/{}?charset=utf8'.format(mysql_user, mysql_password, mysql_host, mysql_database)
engine = create_engine(database_url, encoding="utf8", echo=False, pool_size=100, pool_pre_ping=True, pool_recycle=1800)
DBSession = scoped_session(sessionmaker(bind=engine, autocommit=False))
