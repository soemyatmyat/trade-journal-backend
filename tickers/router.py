from fastapi import APIRouter, Depends, HTTPException
from database import get_db 
from sqlalchemy.orm import Session 

from . import schemas, service

router = APIRouter() 

@router.get("/{ticker_id}", response_model=schemas.Ticker, tags=["tickers"])
async def get_closed_price(ticker_id: str, db: Session=Depends(get_db)):
    existing_ticker = service.get_closed_price(db, ticker_id)
    if not existing_ticker:
        raise HTTPException(status_code=404, detail="No data found, symbol may be delisted.")
    return existing_ticker 

@router.post("/options/", response_model=schemas.Option_Details, tags=["tickers"])
async def get_option(option: schemas.Option, db: Session=Depends(get_db)):
    try: 
        existing_option = service.get_option_price(db, option)
        if not existing_option:
            raise HTTPException(status_code=404, detail="No data found, strike price may not be correct.")
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))
    return existing_option

@router.get("/updates", include_in_schema=False) 
async def update_tickers(db: Session=Depends(get_db)):
    service.update_all_tickers(db)
    service.update_all_options(db)
    pass #12 factor logging....