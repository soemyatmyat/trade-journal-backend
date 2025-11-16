from pydantic import BaseModel 
from datetime import datetime
from enum import Enum

class Ticker_Id(BaseModel):
  ticker: str = ""

class TickerCreate(Ticker_Id):
  closed_price: float 

class Ticker(Ticker_Id):
  closed_price: float 
  fetched_date: datetime

  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models

class OptionType(str, Enum):
  call = "Call"
  put = "Put"

class Option(Ticker_Id):
  type: OptionType = OptionType.call
  expire_date: datetime
  strike_price: float

  model_config = {
    "from_attributes": True
  } # Enable ORM mode to work with SQLAlchemy models

class Option_Details(Option):
  id: str 
  ask: float 
  bid: float 
  volume: float 
  iv: float 
  itm: bool
  fetched_date: datetime

  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models

