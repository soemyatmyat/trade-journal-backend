from sqlalchemy.orm import Session 
from . import models # database models

# read
def get_ticker(db: Session, ticker: str) -> models.Ticker | None:
  return db.query(models.Ticker).filter(models.Ticker.ticker==ticker).first()

# create
def create_ticker(db: Session, ticker: models.Ticker) -> models.Ticker:
  db.add(ticker)
  db.commit()
  db.refresh(ticker)
  return ticker 

# update
def update_ticker(db: Session, ticker: models.Ticker) -> models.Ticker:
  db.merge(ticker) # merge is used to update an existing record
  db.commit()
  db.refresh(ticker)
  return ticker

# read 
def get_option_by_id(db: Session, option_id: str) -> models.Option | None:
  return db.query(models.Option).filter(models.Option.id == option_id).first()

# read 
def get_option(db: Session, option:models.Option) -> models.Option | None:
  return db.query(models.Option).filter(
    models.Option.ticker == option.ticker.upper(), 
    models.Option.strike_price == option.strike_price, 
    models.Option.expire_date == option.expire_date,
    models.Option.type == option.type
  ).first()

# create
def create_option(db: Session, option: models.Option) -> models.Option:
  db.add(option)
  db.commit()
  db.refresh(option)
  return option

# update
def update_option(db: Session, option: models.Option) -> models.Option:
  db.merge(option) # merge is used to update an existing record
  db.commit()
  db.refresh(option)
  return option