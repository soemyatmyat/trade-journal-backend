from sqlalchemy import Column, Float, String, DateTime, ForeignKey, Boolean 
from sqlalchemy.types import Enum
from sqlalchemy.orm import relationship 
from database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class Ticker(Base):
    __tablename__ = "tickers"

    ticker = Column(String, primary_key=True)
    closed_price = Column(Float)
    # fetched_date = Column(Date, default=date.today) 
    fetched_date = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("UTC")))

    positions = relationship("Position", back_populates="ticker_belongs_to")
    options = relationship("Option", back_populates="ticker_of") # one-to-many relationship with Option

class Option(Base):
    __tablename__ = "options"

    id = Column(String, primary_key=True)
    type = Column(Enum('Call','Put')) 
    ticker = Column(String, ForeignKey("tickers.ticker"))
    strike_price = Column(Float)
    bid = Column(Float)
    ask = Column(Float)
    # expire_date = Column(Date) 
    expire_date = Column(DateTime(timezone=True))
    volume = Column(Float)
    iv = Column(Float)
    itm = Column(Boolean)
    #fetched_date = Column(Date, default=date.today)
    fetched_date = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("UTC")))

    ticker_of = relationship("Ticker", back_populates="options") 
