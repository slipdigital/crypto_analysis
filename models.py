from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ticker(Base):
    __tablename__ = 'tickers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String)
    crypto_symbol = Column(String)
    market = Column(String)
    locale = Column(String)
    active = Column(Boolean)
    is_usd_pair = Column(Boolean)
    currency_symbol = Column(String)
    currency_name = Column(String)
    base_currency_symbol = Column(String)
    base_currency_name = Column(String)
    current_price = Column(Float)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    price_change_24h = Column(Float)
    last_trade_timestamp = Column(Float)
    last_updated = Column(String)
    delisted = Column(String)
    collected_date = Column(DateTime)
