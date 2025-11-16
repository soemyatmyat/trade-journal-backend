from typing import Optional
from pydantic import BaseModel, Field 
from datetime import datetime
from enum import Enum

class PositionType(str, Enum):
  long = "Long"
  short = "Short"
  call = "Call"
  put = "Put"

class Position_Id(BaseModel):
  id: int 

class Position(BaseModel):
  id: Optional[int] = None
  ticker: str
  category: PositionType = PositionType.long
  qty: int = 100
  option_price: Optional[float] = None
  trade_price: float 
  open_date: datetime
  close_date: Optional[datetime] = None
  closed_price: Optional[float] = None
  remark: str = ''
  is_active: Optional[bool] = True

  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models

class Position_Create(Position):
  owner_id: int 
  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models

class Position_Owner_Details(Position):
  owner_id: int 

  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models