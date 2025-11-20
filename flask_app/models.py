from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Date, UniqueConstraint, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    
    # Relationship to ticker_data
    ticker_data = relationship("TickerData", back_populates="ticker_obj")

class TickerData(Base):
    __tablename__ = 'ticker_data'
    __table_args__ = (UniqueConstraint('ticker_id', 'date', name='_ticker_date_uc'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    vwap = Column(Float)  # Volume weighted average price
    transactions = Column(Integer)
    collected_at = Column(String)
    
    # Relationship to ticker
    ticker_obj = relationship("Ticker", back_populates="ticker_data")

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

class IndicatorType(Base):
    __tablename__ = 'indicator_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code (e.g., #FF5733)
    created_at = Column(String)
    updated_at = Column(String)

class Indicator(Base):
    __tablename__ = 'indicators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    url = Column(String(500), nullable=True)  # Optional URL for reference/documentation
    indicator_type_id = Column(Integer, ForeignKey('indicator_types.id'), nullable=True)
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
