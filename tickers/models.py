from sqlalchemy import Column, Float, String, Date,ForeignKey, Boolean 
from sqlalchemy.types import Enum
from sqlalchemy.orm import relationship 
from database import Base
from datetime import date

class Ticker(Base):
    __tablename__ = "tickers"

    ticker = Column(String, primary_key=True)
    closed_price = Column(Float)
    closed_date = Column(Date, default=date.today)

    positions = relationship("Position", back_populates="ticker_belongs_to")
    options = relationship("Option", back_populates="ticker_of")

class Option(Base):
    __tablename__ = "options"

    id = Column(String, primary_key=True)
    type = Column(Enum('Call','Put')) 
    ticker = Column(String, ForeignKey("tickers.ticker"))
    strike_price = Column(Float)
    bid = Column(Float)
    ask = Column(Float)
    expire_date = Column(Date) 
    volume = Column(Float)
    iv = Column(Float)
    itm = Column(Boolean)

    ticker_of = relationship("Ticker", back_populates="options")    

## need to run cron job::