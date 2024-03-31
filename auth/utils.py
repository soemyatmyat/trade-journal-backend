from datetime import datetime, timedelta, timezone 
from jose import JWTError, jwt
from . import schema

# to get a string like this run: # this goes into .env config
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# jwt is based64 encoded. anyone can decode the token and use its data. But only the server can verify it's authenticity using the JWT_SECRET
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy() # data={"sub": user.email}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15) # default 15 mins 
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_data = schema.TokenData(username=username)
    except JWTError: # when will this be triggered??
        return None
    return token_data 
