from datetime import datetime, timedelta, timezone 
from jose import JWTError, jwt
from . import schema
import settings
import secrets

BLACKLIST = set()

# jwt is based64 encoded. anyone can decode the token and use its data. But only the server can verify it's authenticity using the JWT_SECRET
def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy() # data={"sub": user.email}
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
  to_encode.update({"exp":expire}) # to_encode={"sub": user.email, "exp": expire}
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  return encoded_jwt

def revoke_token(token: str):
  BLACKLIST.add(token)

def decode_access_token(token: str):
  if (token not in BLACKLIST):
    try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
      username: str = payload.get("sub")
      token_data = schema.TokenData(username=username)
    except JWTError: # when will this be triggered??
      return None
    return token_data 
  return None

def create_token():
  ''' Return a random URL-safe text string, in Base64 encoding'''
  return secrets.token_urlsafe(32)  # Generate a random string as refresh token
