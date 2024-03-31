from sqlalchemy import Column, Integer, Float, Boolean, Date, String, ForeignKey
from sqlalchemy.types import Enum
from sqlalchemy.orm import relationship 
from database import Base 

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    category = Column(Enum('Long', 'Short', 'Call','Put')) # would be better to separate as a new model maybe
    ticker = Column(String, ForeignKey("tickers.ticker")) 
    qty = Column(Integer, default = 100)
    option_price = Column(Float, default=0)
    trade_price = Column(Float, default=0)
    closed_price = Column(Float, default=None) # (enter manually)
    is_active = Column(Boolean, default=True)
    open_date = Column(Date)
    close_date = Column(Date, nullable=True) # set is_active = false 
    remark = Column(String, default = None)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="positions")
    ticker_belongs_to = relationship("Ticker", back_populates="positions")


