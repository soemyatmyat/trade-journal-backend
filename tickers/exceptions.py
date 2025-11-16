from fastapi import HTTPException

# HTTP_404_NOT_FOUND
class TickerNotFoundException(HTTPException):
  def __init__(self, ticker_id: str):
    super().__init__(status_code=404, detail=f"Ticker '{ticker_id}' not found. It may be delisted.")

# HTTP_404_NOT_FOUND
class OptionNotFoundException(HTTPException):
  def __init__(self, ticker_id: str, strike_price: float):
    super().__init__(status_code=404, detail=f"Option with strike price '{strike_price}' for ticker '{ticker_id}' not found.")

class InvalidFrequencyException(HTTPException):
  def __init__(self, frequency: str):
    super().__init__(status_code=400, detail=f"Invalid frequency '{frequency}'. Allowed values are 'W', 'D', 'M'.")

class DateRangeException(HTTPException):
  def __init__(self):
    super().__init__(status_code=400, detail="from_date cannot be after to_date.")

class DataRetrievalException(HTTPException):
  def __init__(self, message: str):
    super().__init__(status_code=500, detail=f"Data retrieval error: {message}")

class CacheException(HTTPException):
  def __init__(self, message: str):
    super().__init__(status_code=500, detail=f"Cache error: {message}")

class ExternalAPIException(HTTPException):
  def __init__(self, message: str):
    super().__init__(status_code=502, detail=f"External API error: {message}")

class DatabaseException(HTTPException):
  def __init__(self, message: str):
    super().__init__(status_code=500, detail=f"Database error: {message}")

class ValidationException(HTTPException):
  def __init__(self, message: str):
    super().__init__(status_code=400, detail=f"Validation error: {message}")