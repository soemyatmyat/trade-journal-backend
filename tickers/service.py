from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session 
from . import schemas, models, repository 
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import yfinance as yf
import pandas as pd
import redis 
import json
import settings

def update_ticker(db: Session, ticker: schemas.TickerCreate) -> schemas.Ticker:
  """
  Update or insert a ticker into the database.
  Args:
    db: SQLAlchemy database session.
    ticker: Ticker data to be inserted or updated.
  """
  existing_ticker = repository.get_ticker(db, ticker.ticker)
  if not existing_ticker:
    db_ticker = models.Ticker(ticker=ticker.ticker, closed_price=ticker.closed_price, fetched_date=datetime.now(ZoneInfo("UTC")))
    db_ticker = repository.create_ticker(db, db_ticker)
    return schemas.Ticker.model_validate(db_ticker)
  else: # update if existing
    existing_ticker.closed_price = ticker.closed_price
    existing_ticker.fetched_date = datetime.now(ZoneInfo("UTC"))
    db_ticker = repository.update_ticker(db, existing_ticker)
    return schemas.Ticker.model_validate(db_ticker)

def get_closed_price(db: Session, ticker: str) -> schemas.Ticker | None:
  """
  Retrieve the latest closing price for a given ticker symbol. If the ticker data is not up to date, fetches the latest price using yfinance
  Args: 
    db (session): SQLAlchemy database session used for querying and updating the ticker.
    ticker (str): The stock ticker symbol (e.g. "AAPL", "TSLA", etc.).
  """
  # check if existing in database 
  existing_ticker = repository.get_ticker(db, ticker)
  today_utc= datetime.now(ZoneInfo("UTC")).date()
  if not existing_ticker or existing_ticker.fetched_date.date() != today_utc: 
    data = yf.Ticker(ticker)
    closed_price = data.history(period='1d')['Close'] # returns the data in UTC
    if closed_price.shape[0] == 0:
      return None
    else:
      existing_ticker = update_ticker(db, schemas.TickerCreate(ticker=ticker, closed_price=closed_price.iloc[-1]))   
  return schemas.Ticker.model_validate(existing_ticker)

def get_historical_price(ticker: str, start_date: datetime, end_date: datetime, frequency: str, redis_client: redis.Redis) -> list[dict]:
  """
  Get historical price data for a given ticker symbol between start_date and end_date.
  Args:
    ticker: Stock ticker symbol (e.g., 'AAPL')
    start_date: Start date for historical data (YYYY-MM-DD) in UTC
    end_date: End date for historical data (YYYY-MM-DD) in UTC
    frequency: 'W' for weekly, 'M' for monthly
  Returns:
    A list of dictionaries containing historical price data with keys: Date, close, prev, diff, percentage
  """
  end_date_plus_one = end_date + timedelta(days=1)
  # redis cache check
  try:
    if (redis_client.ping()):
      redis_cache_key = f"price_history:{ticker}:{start_date}:{end_date_plus_one}:{frequency}"
      cached_data = redis_client.get(redis_cache_key)
      if cached_data is not None: 
        return json.loads(cached_data)
  except redis.exceptions.ConnectionError as e: # this needs to be logged. 
    print("error: Could not connect to Redis: ", e)

  # download historical price data 
  data = yf.download(ticker, start_date, end_date_plus_one)["Close"].round(2)
  data = data.rename(columns={ticker.upper(): "close"})
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

  try:
    if (redis_client.ping()):
      # convert dataframe to json
      json_data = json.dumps(df.to_dict(orient='records'), indent=4)
      # cache the data in Redis
      redis_client.set(redis_cache_key, json_data, ex=settings.REDIS_EX, nx=True) # nx to avoid overwriting existing cache
  except redis.exceptions.ConnectionError as e: 
    print("error: Could not connect to Redis: ", e)

  return df.to_dict(orient='records') # return in dict/json form 

def get_chain(data, exp) -> yf.Ticker.option_chain:
  return data.option_chain(exp)

def get_put_call_vol_ratio(ticker: str) -> float: 
  """
  Calculate the put/call volume ratio for a given ticker symbol.
  Args:
    ticker: Stock ticker symbol (e.g., 'AAPL')
  """
  data = yf.Ticker(ticker)  # download ticker information
  options = data.options # list of expiration dates expected in 'YYYY-MM-DD' format, ex: ['2023-10-20', '2023-10-27', ...]

  with ThreadPoolExecutor() as executor: # use ThreadPoolExecutor for concurrent fetching
    futures = [executor.submit(get_chain, data, exp) for exp in options]
    chains = [f.result() for f in futures]
    # chains = list(executor.map(get_chain, options)) # fetch all option chains concurrently
  
  total_put_volume = sum(chain.puts["volume"].sum() for chain in chains)
  total_call_volume = sum(chain.calls["volume"].sum() for chain in chains)
  # Initialize total put and call volumes
  # total_put_volume = 0
  # total_call_volume = 0

  # for expiration in options:
  #   option_chain = data.option_chain(expiration)
  #   # Sum up the volumes for this expiration
  #   total_put_volume += option_chain.puts['volume'].sum()
  #   total_call_volume += option_chain.calls['volume'].sum()

  put_call_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else 0 # compute put/call ratio

  return round(put_call_ratio, 2) # round to 2 decimal places

def get_metrics(ticker: str, redis_client: redis.Redis) -> dict: 
  # redis cache check - instead of querying from yfinance every time, check if data is cached in redis
  try:
    if (redis_client.ping()):
      redis_cache_key = f"metrics:{ticker}"
      cached_data = redis_client.get(redis_cache_key)
      if cached_data is not None: 
        return json.loads(cached_data)
  except redis.exceptions.ConnectionError as e: # this needs to be logged.
    print("error: Could not connect to Redis: ", e)

  # otherwise, download ticker information # todo: what is the difference between yf.Ticker(ticker) and yf.download(ticker) ## 
  data = yf.Ticker(ticker).info
  market_cap = format_market_cap(data.get('marketCap')) # 1. Market Cap
  ex_dividend_date = data.get('exDividendDate') # Ex-Dividend Date (in UNIX timestamp) # 2. Ex-Dividend Date
  if ex_dividend_date:
    # Convert UNIX timestamp to a human-readable format
    # ex_dividend_date = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
    # Convert from UNIX timestamp (seconds since epoch) to UTC date
    ex_dividend_date = datetime.fromtimestamp(ex_dividend_date, ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%S%z')
  else: 
    ex_dividend_date = ''
  earnings_hist = {} # dictionary placeholder for earnings history
  earnings_dates = yf.Ticker(ticker).get_earnings_dates() # this returns a dataframe
  upcoming_earnings_date = '' # 3. Upcoming Earnings Date
  if not earnings_dates.empty or earnings_dates.shape[0] != 0:
    last_earnings = earnings_dates.iloc[0] # this returns in UNIX timestamp
    last_earnings_date = last_earnings.name # index of the row, i.e., Timestamp('2025-10-30 16:00:00-0400', tz='America/New_York')
    last_earnings_date = last_earnings_date.to_pydatetime() # convert to datetime object with timezone info
    last_earnings_date_utc = last_earnings_date.astimezone(ZoneInfo("UTC")) # convert to UTC
    download_time = datetime.now()
    download_time_utc = download_time.astimezone(ZoneInfo("UTC")) # convert to UTC
    # Check if the last earnings date is in the past
    if last_earnings_date_utc > download_time_utc:
      upcoming_earnings_date = last_earnings_date_utc.isoformat() # convert to ISO 8601 format in UTC
      earnings_dates.drop(earnings_dates.index[0], inplace=True) # remove the upcoming earnings date from the history
    earnings_dates = earnings_dates.reset_index()  # move index to column
    earnings_dates = earnings_dates.dropna(subset=["EPS Estimate", "Reported EPS", "Surprise(%)"]) # drop rows with NaN values in any of the specified columns # todo: this is hardcoded, need to make it dynamic
    if not earnings_dates['Earnings Date'].empty: # we manipulate the 'Earnings Date' column to convert to UTC ISO 8601 format directly in the dataframe 
      earnings_dates['Earnings Date'] = earnings_dates['Earnings Date'].dt.tz_convert('UTC').dt.strftime('%Y-%m-%dT%H:%M:%S%z')
      earnings_dates['Earnings Date'] = earnings_dates['Earnings Date'].str.replace(r'(\d{2})(\d{2})$', r'\1:\2', regex=True) # add colon to timezone offset
    earnings_hist = earnings_dates.to_dict(orient="records") # Convert DataFrame to list of dicts # 4. Earnings History
  pe = data.get('trailingPE') # 5. PE Ratio
  pe_formatted = '' if pe is None else round(pe, 2) # some tickers will not have PE as they have yet to make a profit
  divided_yield = data.get('dividendYield') # 6. Dividend Yield
  dividend_yield_formatted = '' if divided_yield is None else round(divided_yield * 100, 2) # some tickers don't pay dividend
  beta = data.get('beta') # 7. Beta
  beta_formatted = '' if beta is None else round(data.get('beta'), 2)
  metrics = {
    'symbol': data.get('symbol'),
    'volume': data.get('volume'),
    'beta': beta_formatted,
    'IV': '',
    'annualDividend': data.get('dividendRate'),
    'VWAP': '',
    'averageVolume': data.get('averageVolume'),
    'PE': pe_formatted, 
    'HV': '',
    'dividendYield': dividend_yield_formatted,
    'marketMakerMove': '',
    'marketCap': market_cap,
    'EPS': data.get('trailingEps'),
    'PCR': get_put_call_vol_ratio(ticker),
    'exDividendDate':  ex_dividend_date,
    'upcomingEarningsDate': upcoming_earnings_date,
    'earningsHistory': earnings_hist,
  }
  try:
    if (redis_client.ping()):
      json_data = json.dumps(metrics)
      # cache the data in Redis with key: f"metrics:{ticker}", 600 seconds expiration, nx = True to avoid overwriting existing cache
      redis_client.set(redis_cache_key, json_data, ex=settings.REDIS_EX, nx=True)
  except redis.exceptions.ConnectionError as e:
    print("error: Could not connect to Redis: ", e)

  return metrics

def format_market_cap(value):
  if value is not None:
    if value >= 1e12: 
      return f"{value / 1e12:.2f}T"  # Trillions
    elif value >= 1e9:
      return f"{value / 1e9:.2f}B"   # Billions
    elif value >= 1e6:
      return f"{value / 1e6:.2f}M"   # Millions
    else:
      return str(value) 
  return ''

def update_option(db:Session, option: schemas.Option_Details) -> schemas.Option_Details:
  """
  Update or insert an option into the database.
  Args:
    db: SQLAlchemy database session.
    option: Option data to be inserted or updated.
  """
  existing_option = repository.get_option_by_id(db, option.id)   # check if existing in database 
  if not existing_option:
    db_option = models.Option(**option.model_dump(exclude_unset=True)) # create new option orm object
    db_option = repository.create_option(db, db_option)
    return schemas.Option_Details.model_validate(db_option) # validate the orm object
  else: # update if existing 
    for attr, value in option.model_dump(exclude_unset=True).items(): # loop through all attributes of the option
      if value and value != getattr(existing_option, attr): # check if the new value is not empty and not the same as existing ones 
        setattr(existing_option, attr, value)
    db_option = repository.update_option(db, existing_option)
    return schemas.Option_Details.model_validate(db_option)

def get_option_price(db: Session, option: schemas.Option) -> schemas.Option_Details | None:
  """
  Retrieve the latest option price for a given option. If the option data is not in the database, fetches the latest price using yfinance
  Args:
    db (session): SQLAlchemy database session used for querying and updating the option.
    option (schemas.Option): The option details including ticker, type, expire_date, and strike_price.
  """
  db_option = models.Option(
    ticker=option.ticker.upper(),
    type=option.type.value,
    expire_date=option.expire_date,
    strike_price=option.strike_price
  ) # 
  existing_option = repository.get_option(db, db_option) 
  if not existing_option: # doesn't exist in the database, fetch from yfinance
    data = yf.Ticker(option.ticker) 
    try: 
      option_chain_data = data.option_chain(str(option.expire_date.date()))
      if option.type == "Call":
        options_chain = option_chain_data.calls 
      else:
        options_chain = option_chain_data.puts 
      option_data = options_chain[options_chain['strike'] == option.strike_price] # get the exact one 
      if option_data.shape[0] != 0:
        db_option = models.Option(
                id=option_data['contractSymbol'].values[0],
                type=option.type.value, 
                ticker=option.ticker.upper(),
                expire_date=option.expire_date,
                strike_price=option_data['strike'].values[0],
                ask=option_data['ask'].values[0],
                bid=option_data['bid'].values[0],
                volume=option_data['volume'].values[0],
                iv=option_data['impliedVolatility'].values[0],
                itm=option_data['inTheMoney'].values[0]
            )
        db_option = repository.create_option(db, db_option)
        return schemas.Option_Details.model_validate(existing_option)
      else:
        return None # no data found for the given strike price
    except Exception as error:
      raise error 
  return schemas.Option_Details.model_validate(existing_option)

# todo
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