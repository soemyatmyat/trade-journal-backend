from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_db 
from sqlalchemy.orm import Session 
from datetime import datetime, date, timedelta
from typing import Optional

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

@router.get("/historical_prices/{ticker_id}", tags=["tickers"])
async def get_price_history(
    ticker_id: str, 
    from_date: Optional[datetime] =  Query(date.today()- timedelta(days=14), description="Start date for historical data"),
    to_date: Optional[datetime] = Query(date.today(), description="End date for historical data"), 
    frequency: Optional[str] = Query("W", description="Frequency of data (d for daily, w for weekly, m for monthly)"),
    db: Session=Depends(get_db)
):
    # frequency check 
    allowed_historical_frequencies = ['W', 'D', 'M'] # this needs to go into utils
    if frequency.upper() not in allowed_historical_frequencies:
        raise HTTPException(status_code=400, detail="Frequency must be one of 'W' (weekly), 'D' (daily), 'M' (monthly)")

    # from_date and to_date check
    if from_date and to_date and from_date > to_date: 
        raise HTTPException(status_code=400, detail="from_date cannot be after to_date")

    existing_ticker = service.get_closed_price(db, ticker_id) # validation check: ticker_id
    if not existing_ticker:
        raise HTTPException(status_code=404, detail="No data found, symbol may be delisted.")
    
    # retrieve data 
    return service.get_historical_price(ticker_id, from_date, to_date, frequency.upper())

@router.get("/metrics/{ticker_id}", tags=["tickers"])
async def get_metrics(ticker_id: str, db: Session=Depends(get_db)):
    existing_ticker = service.get_closed_price(db, ticker_id) # validation check: ticker_id
    if not existing_ticker:
        raise HTTPException(status_code=404, detail="No data found, symbol may be delisted.")
    
    # retrieve data 
    return service.get_metrics(ticker_id)

@router.get("/updates", include_in_schema=False) 
async def update_tickers(db: Session=Depends(get_db)):
    service.update_all_tickers(db)
    service.update_all_options(db)
    pass #12 factor logging....