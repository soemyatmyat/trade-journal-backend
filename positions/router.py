from hmac import new
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db 
from sqlalchemy.orm import Session 
from auth import schema as user_schema 
from auth.router import get_current_user
from tickers import service as tickers_service, schemas as tickers_schemas 
from . import schemas, service
# app.include_router(pos_router, prefix="/positions")
router = APIRouter() 

# Create
@router.post("/", response_model=schemas.Position, tags=["positions"])
async def add_position(position: schemas.Position, current_user: user_schema.UserId = Depends(get_current_user), db: Session=Depends(get_db)) -> schemas.Position | None:
  try:
    ticker = tickers_service.get_closed_price(db, position.ticker)
    if not ticker:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found, symbol may be delisted.")
      
    if (position.category.lower == 'put' or position.category == 'call'): # option position validation
      if position.close_date is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Option positions must have an expire date.")
      if position.category.lower == 'call' and position.trade_price < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Call option strike price must be non-negative.")
      if position.category.lower == 'put' and position.trade_price <= 0:  
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Put option strike price must be positive.")
      
      # check if option exists in db
      option = tickers_service.get_option_price(db, tickers_schemas.Option(ticker=position.ticker, type=position.category.lower, expire_date=position.close_date, strike_price=position.trade_price))
      if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found, strike price may not be correct.")

    # pass validation check, move it along to service
    position = schemas.Position_Create(**position.model_dump(), owner_id=current_user.id)  
    new_position = service.create_position(db, position)
    return new_position
  except Exception as error:
    raise HTTPException(status_code=404, detail=str(error))

# READ ALL
@router.get("/", response_model=list[schemas.Position], tags=["positions"])
async def retrieve_positions(current_user: user_schema.UserId = Depends(get_current_user),db: Session=Depends(get_db)):
  positions = service.retrieve_positions(db, current_user.id) # limit and offset incorporated.
  return [schemas.Position.model_validate(p) for p in positions] 

# READ 
@router.get("/{position_id}", response_model=schemas.Position, tags=["positions"])
async def retrieve_a_position(position_id: int, current_user: user_schema.UserId = Depends(get_current_user),db: Session=Depends(get_db)):
    position = service.get_position_by_id(db, position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="No data found, id may be invalid.")
    return service.orm_to_pydantic(position)

# UPDATE
@router.put("/{position_id}", response_model=schemas.Position, tags=["positions"])
async def update_position(position_id: int, update_position: schemas.Position, current_user: user_schema.UserId = Depends(get_current_user),db: Session=Depends(get_db)):
    ticker = tickers_service.get_closed_price(db, position.ticker)
    if not ticker: 
      raise HTTPException(status_code=404, detail="No data found, symbol may be delisted.")
    
    position = service.update_position_by_id(db, position_id, update_position)
    if position is None:
        raise HTTPException(status_code=404, detail="No data found, id may be invalid.")
    
    
    return service.orm_to_pydantic(position)

# DELETE 
@router.delete("/{position_id}", status_code=204, tags=["positions"])
async def remove_position(position_id: int, current_user: user_schema.UserId = Depends(get_current_user),db: Session=Depends(get_db)):
  existing_position = service.remove_position(db, position_id)
  if existing_position is None:
    raise HTTPException(status_code=404, detail="No data found, id may be invalid.")
  return None

