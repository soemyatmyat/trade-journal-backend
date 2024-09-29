from . import schemas, models 
from sqlalchemy.orm import Session 
from datetime import datetime
import yfinance as yf
import pandas as pd

def get_ticker(db: Session, ticker: str):
    return db.query(models.Ticker).filter(models.Ticker.ticker==ticker).first()

def update_ticker(db: Session, ticker: schemas.TickerCreate):
    existing_ticker = get_ticker(db, ticker.ticker)
    if not existing_ticker:
        db_ticker = models.Ticker(ticker=ticker.ticker, closed_price=ticker.closed_price, fetched_date=datetime.today().date())
        db.add(db_ticker)
        db.commit()
        db.refresh(db_ticker)
        return db_ticker 
    else: # update if  existing
        existing_ticker.closed_price = ticker.closed_price
        existing_ticker.fetched_date = datetime.today().date()
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

    return schemas.Ticker(ticker=existing_ticker.ticker, closed_price= existing_ticker.closed_price, fetched_date=existing_ticker.fetched_date)

def get_historical_price(ticker: str, start_date: datetime, end_date: datetime, frequency: str):
    # download historical price data 
    data = yf.download(ticker, start_date, end_date)["Adj Close"].round(2)
    # resample data to the specified frequency
    weekstarts = data.resample(frequency).last()
    weekends = weekstarts.shift(-1)
    # compute weekly returns
    weekly_ret_diff = (weekends - weekstarts)
    weekly_ret_change = weekly_ret_diff / weekstarts
    # prep data format 
    df = pd.DataFrame(weekends)
    df["prev"] = weekstarts
    df["diff"] = weekly_ret_diff.round(2)
    df["percentage"] = (weekly_ret_change * 100).round(2)
    df.reset_index(inplace=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df = df.sort_values(by='Date', ascending=False) 
    df.dropna(inplace=True)
    return df.to_dict(orient='records') # return in dict/json form 

def get_metrics(ticker: str): 
    data = yf.Ticker(ticker).info
    market_cap = format_market_cap(data.get('marketCap'))
    ex_dividend_date = data.get('exDividendDate') # Ex-Dividend Date (in UNIX timestamp)
    if ex_dividend_date:
        # Convert UNIX timestamp to a human-readable format
        ex_dividend_date = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
    else: 
        ex_dividend_date = ''
    upcoming_earnings_date = data.get('earningsDate')
    if upcoming_earnings_date:
        # Extract the date if it's in a list format
        if isinstance(upcoming_earnings_date, list):
            upcoming_earnings_date = upcoming_earnings_date[0]  # Get the first date if it's a list
        # Convert UNIX timestamp to a human-readable format
        upcoming_earnings_date = datetime.fromtimestamp(upcoming_earnings_date).strftime('%Y-%m-%d')
    else: 
        upcoming_earnings_date = '' 
    metrics = {
        'symbol': data.get('symbol'),
        'volume': data.get('volume'),
        'beta': data.get('beta'),
        'pe': data.get('trailingPE'),
        'eps': data.get('trailingEps'),
        'marketCap': market_cap,
        'dividendYield': data.get('dividendYield'),
        'averageVolume': data.get('averageVolume'),
        'dividend': data.get('dividendRate'),
        'exDividendDate':  ex_dividend_date,
        'upcomingEarningsDate': upcoming_earnings_date
    }
    return metrics

def format_market_cap(value):
    if value >= 1e12:
        return f"{value / 1e12:.2f}T"  # Trillions
    elif value >= 1e9:
        return f"{value / 1e9:.2f}B"   # Billions
    elif value >= 1e6:
        return f"{value / 1e6:.2f}M"   # Millions
    else:
        return str(value) 


def get_option_by_id(db: Session, option_id: str):
    return db.query(models.Option).filter(models.Option.id == option_id).first()

def get_option(db: Session, option:schemas.Option):
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
            raise error 
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
                    ticker.fetched_date = datetime.today().date()
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