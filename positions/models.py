from sqlalchemy import Column, Integer, Float, Boolean, Date, String, ForeignKey
from sqlalchemy.types import Enum
from sqlalchemy.orm import relationship 
from database import Base 

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    category = Column(Enum('Long', 'Short', 'Call','Put')) 
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

    def __str__(self):
        return f"Position ID: {self.id}, Category: {self.category}, ticker: {self.ticker}, option_price: {self.option_price}, Open Date: {self.open_date}, Close Date: {self.close_date}, Is Active: {self.is_active}, Closed Price: {self.closed_price}"
