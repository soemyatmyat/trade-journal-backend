from pydantic import BaseModel 
from datetime import date

from enum import Enum


class Ticker_Id(BaseModel):
    ticker: str = ""

class TickerCreate(Ticker_Id):
    closed_price: float 

class Ticker(Ticker_Id):
    closed_price: float 
    closed_date: date

    class Config:
        orm_mode = True 

class OptionType(str, Enum):
    call = "Call"
    put = "Put"

class Option(Ticker_Id):
    type: OptionType = OptionType.call
    expire_date: date
    strike_price: float

class Option_Details(Option):
    id: str 
    ask: float 
    bid: float 
    volume: float 
    iv: float 
    itm: bool

