from . import schemas, models 
from sqlalchemy.orm import Session 
from datetime import datetime
import yfinance as yf

def get_ticker(db: Session, ticker: str):
    return db.query(models.Ticker).filter(models.Ticker.ticker==ticker).first()

def update_ticker(db: Session, ticker: schemas.TickerCreate):
    existing_ticker = get_ticker(db, ticker.ticker)
    if not existing_ticker:
        db_ticker = models.Ticker(ticker=ticker.ticker, closed_price=ticker.closed_price, closed_date=datetime.today().date())
        db.add(db_ticker)
        db.commit()
        db.refresh(db_ticker)
        return db_ticker 
    else: # update if  existing
        existing_ticker.closed_price = ticker.closed_price
        existing_ticker.closed_date = datetime.today().date()
        db.commit()
        db.refresh(db_ticker)
        return existing_ticker

def get_closed_price(db: Session, ticker_id: int):
    # check if existing in database 
    existing_ticker = get_ticker(db, ticker_id)
    if not existing_ticker:
        data = yf.Ticker(ticker_id)
        closed_price = data.history(period='1d')['Close']
        if closed_price.shape[0] == 0:
            return None
        else:
            existing_ticker = update_ticker(db, schemas.TickerCreate(ticker=ticker_id, closed_price=closed_price.iloc[-1]))   

    return schemas.Ticker(ticker=existing_ticker.ticker, closed_price= existing_ticker.closed_price, closed_date=existing_ticker.closed_date)

def get_option_by_id(db: Session, option_id: str):
    return db.query(models.Option).filter(models.Option.id == option_id).first()

def get_option(db: Session, option:schemas.Option):
    print("Getting optin from db: ", option);
    return db.query(models.Option).filter(
        models.Option.ticker == option.ticker, 
        models.Option.strike_price == option.strike_price, 
        models.Option.expire_date == option.expire_date,
        models.Option.type == option.type
    ).first()

def update_option(db:Session, option: schemas.Option_Details):
    # check if existing in database 
    existing_option = get_option_by_id(db, option.id)
    if not existing_option:
        db.add(option)
        db.commit()
        db.refresh(option)
        return option
    else: # update if existing 
        for attr, value in option.model_dump(exclude_unset=True).items():
            if value and getattr(existing_option, attr) != value: # check if new value is not empty and not the same as existing ones 
                setattr(existing_option, attr, value)
        db.commit()
        return existing_option

def get_option_price(db: Session, option: schemas.Option):
    existing_option = get_option(db, option)
    if not existing_option:
        print("OPtion is ", option)
        data = yf.Ticker(option.ticker) 
        try: 
            option_chain_data = data.option_chain(str(option.expire_date))
            if option.type == "Call":
                options_chain = option_chain_data.calls 
            else:
                options_chain = option_chain_data.puts 
            option_data = options_chain[options_chain['strike'] == option.strike_price]
            if option_data.shape[0] != 0:
                db_option = models.Option(
                        id=option_data['contractSymbol'].values[0],
                        type=option.type.value, 
                        ticker=option.ticker,
                        expire_date=option.expire_date,
                        strike_price=option_data['strike'].values[0],
                        ask=option_data['ask'].values[0],
                        bid=option_data['bid'].values[0],
                        volume=option_data['volume'].values[0],
                        iv=option_data['impliedVolatility'].values[0],
                        itm=option_data['inTheMoney'].values[0]
                    )
                existing_option = update_option(db, db_option)
            else:
                return None 
            return db_option 
        except Exception as error:
            print("Error in get_option_price: ", error)
            raise error 
    print("Option is ", existing_option)
    return existing_option

# run cron jobs to update all tickers + options every weekday at 10 pm (expired options should be removed from database)
# check if ticker has connections to postion, otherwise remove them 
def update_all_tickers(db: Session, batch_size: int = 100):
    offset = 0 
    
    while True:
        tickers = db.query(models.Ticker).offset(offset).limit(batch_size).all()
        if not tickers:
            break 
        for ticker in tickers: 
            try: 
                data = yf.Ticker(ticker.ticker)
                closed_price = data.history(period='1d')['Close'] 
                if closed_price.shape[0] == 0:
                    pass # need to log
                else:
                    ticker.closed_price = closed_price.iloc[-1]
                    ticker.closed_date = datetime.today().date()
            except Exception as e:
                pass # logging 
        db.commit()
        offset += batch_size 

    return None # 402 

def update_all_options(db: Session, batch_size: int = 100):
    offset = 0 
    while True: 
        options = db.query(models.Option).offset(offset).limit(batch_size).all()
        if not options:
            break 
        for option in options:
            try: 
                data = yf.Ticker(option.ticker)
                option_chain_data = data.option_chain(str(option.expire_date))
                if option.type == "Call":
                    options_chain = option_chain_data.calls 
                else:
                    options_chain = option_chain_data.puts 
                print("option_id: ", option.id)
                print("from yf: ", options_chain['contractSymbol'].values[0])
                option_data = options_chain[options_chain['contractSymbol'] == option.id]
                option.bid = option_data['bid'].values[0]
                option.ask = option_data['ask'].values[0]
                option.volume = option_data['volume'].values[0]
                option.iv = option_data['impliedVolatility'].values[0]
                option.itm = option_data['inTheMoney'].values[0]
            except Exception as e:
                print("error: ", e)
                pass # logging 
        db.commit()
        offset += batch_size 
    return None # 402 