from typing import Optional
from pydantic import BaseModel, Field 
from datetime import date
from enum import Enum

class PositionType(str, Enum):
    long = "Long"
    short = "Short"
    call = "Call"
    put = "Put"

class Position_Id(BaseModel):
    id: int 

class Position(BaseModel):
    ticker: str
    category: PositionType = PositionType.long
    qty: int = 100
    option_price: Optional[float] = None
    trade_price: float 
    open_date: date
    close_date: Optional[date] = None
    closed_price: Optional[float] = None
    remark: str = ''

class Position_Create(Position):
    owner_id: int 
    is_active: bool | None = True 

class Position_Details(Position):
    id: int 
    is_active: bool

    class Config:
        from_attributes = True # compatible with ORMs

class Position_Owner_Details(Position_Details):
    owner_id: int 

    class Config:
        from_attributes = True # compatible with ORMs
