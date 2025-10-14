from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Date, UniqueConstraint, Text
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
    market_cap = Column(Float)
    last_trade_timestamp = Column(Float)
    last_updated = Column(String)
    is_favorite = Column(Boolean, default=False)

class TickerData(Base):
    __tablename__ = 'ticker_data'
    __table_args__ = (UniqueConstraint('ticker', 'date', name='_ticker_date_uc'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    vwap = Column(Float)  # Volume weighted average price
    transactions = Column(Integer)
    collected_at = Column(String)

class GlobalLiquidity(Base):
    __tablename__ = 'global_liquidity'
    __table_args__ = (UniqueConstraint('series_id', 'date', name='_series_date_uc'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(String, nullable=False, index=True)  # FRED series ID (e.g., M2SL, WALCL)
    series_name = Column(String)  # Human-readable name
    date = Column(Date, nullable=False, index=True)
    value = Column(Float)  # Value in billions
    units = Column(String)  # Units (e.g., "Billions of Dollars")
    frequency = Column(String)  # Data frequency (e.g., "Monthly", "Weekly")
    collected_at = Column(String)

class Indicator(Base):
    __tablename__ = 'indicators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(String)
    updated_at = Column(String)

class IndicatorData(Base):
    __tablename__ = 'indicator_data'
    __table_args__ = (UniqueConstraint('indicator_id', 'date', name='_indicator_date_uc'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    value = Column(Float, nullable=False)  # Between -1.0 and 1.0
    created_at = Column(String)
    updated_at = Column(String)
