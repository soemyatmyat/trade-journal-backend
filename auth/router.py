from fastapi import APIRouter, Response, Depends, HTTPException, status, Cookie, Header 
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import settings
from database import get_db 
from sqlalchemy.orm import Session 
from . import jwt, service, schema

router = APIRouter() # need to import this to main.py
refresh_tokens_store = {}  # {refresh_token: user_id} -- in-memory store for refresh tokens, but it should be cached in redis

def set_csrf_token_cookie(response: Response):
  csrf_token = jwt.create_token()  # Generate a new CSRF token
  response.set_cookie(
    key="csrf_token",
    value=csrf_token,
    max_age=7 * 24 * 60 * 60,  # 7 days
    path="/",  # Set the path to root so it is sent with every request
    domain=settings.COOKIE_DOMAIN,  # Set the domain to the same as the app
    secure=settings.COOKIE_SECURE,
    httponly=False,
    samesite="None"
  )

def set_refresh_token_cookie(user, response: Response, refresh_token: str):
  refresh_token = jwt.create_token()
  refresh_tokens_store[refresh_token] = user.id  # Store the refresh token in memory (or use a more persistent store like Redis)
  response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    max_age=7 * 24 * 60 * 60,  # 7 days
    path="/",  # Set the path to root so it is sent with every request
    secure=settings.COOKIE_SECURE,
    httponly=True,
    samesite="None"
  )

@router.post("/register", tags=["users"], include_in_schema=False)
async def register_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session=Depends(get_db)):  
  try:
    service.create_user(db, form_data.username, form_data.password)
    return {"message": "User registered successfully."}
  except service.EmailAlreadyRegisteredError:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, 
      detail="Email already registered."
    )

@router.post("/token", response_model=schema.Token, tags=["users"], include_in_schema=True) # return bearer token
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response, db: Session=Depends(get_db)) -> schema.Token:
  '''
  this function will be called for authentication, when the user login with username and password
  the username and password will be passed to the form_data
  the form_data will be validated by FastAPI
  if the username and password are correct, return the access token
  if the username and password are incorrect, raise an exception
  '''
  user = service.authenticate_user(db, form_data.username, form_data.password)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect username or password",
      headers={"WWW-Authenticate": "Bearer"},
    )
  
  # create access token with sub as user email and expire in 15 mins
  access_token = jwt.create_access_token(data={"sub": user.email})

  # Set the new csrf token as a NonHttpOnly, Secure cookie in the response
  set_csrf_token_cookie(response)
  # Set the new refresh token as an HttpOnly, Secure cookie in the response
  set_refresh_token_cookie(user, response, "")
  # return access token and token type
  return schema.Token(access_token=access_token, token_type="bearer") # return token

@router.post("/refresh", response_model=schema.Token, tags=["users"], include_in_schema=True) # return bearer token
# refresh_token = request.cookies.get("refresh_token")  # Get the refresh token from the cookie
async def refresh_token(
  response: Response, 
  db: Session=Depends(get_db),
  refresh_token: str = Cookie(None),
  csrf_cookie: str = Cookie(None, alias="csrf_token"),
  csrf_header: str = Header(None, alias="X-CSRF-TOKEN")
  ) -> schema.Token:

  # print(f"csrf_cookie: {csrf_cookie}, csrf_header: {csrf_header}, refresh_token: {refresh_token}")
  if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="CSRF token mismatch"
    )
  
  # in-memory store for refresh tokens, but it should be cached in redis
  user_id = refresh_tokens_store.get(refresh_token)
  if not user_id:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid refresh token."
    )
  
  user = service.get_user(db, user_id)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="User not found with the provided refresh token."
    )
  
  #scopes = ["read", "write", "admin"] if user.role == "super_admin" else ["read"]
  access_token = jwt.create_access_token(data={"sub": user.email}) 

  # Set the new csrf token as a NonHttpOnly, Secure cookie
  set_csrf_token_cookie(response)
  # Set the new refresh token as an HttpOnly, Secure cookie
  del refresh_tokens_store[refresh_token]
  set_refresh_token_cookie(user, response, refresh_token)
  # return access token and token type
  return schema.Token(access_token=access_token, token_type="bearer") 

@router.post("/logout", include_in_schema=False) 
async def logout(token: str = Depends(service.oauth2_scheme)):
  # revoke the token access (it will expire by default in 15 mins anyway)
  token_data=jwt.decode_access_token(token)
  if token_data is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )
  jwt.revoke_token(token)

'''
token validaition is taken care of by oauth2_scheme for invalid token or expired token. otherwise, would need to do this 
GET /protected HTTP/1.1
Host: example.com
Authorization: Bearer <token>
  credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
  if credentials:
    if not credentials.scheme == "Bearer":
      raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
    if not self.verify_jwt(credentials.credentials):
      raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return credentials.credentials
  else:
    raise HTTPException(status_code=403, detail="Invalid authorization code.")
'''
# this function will be called for authorization, similar to @app.get("/protected")
# but this is faciliated with FastAPI, Depends(get_current_user)
@router.post("/get_user_id", response_model=schema.UserId, tags=["users"], include_in_schema=False)
async def get_current_user(token: Annotated[str, Depends(service.oauth2_scheme)], db: Session=Depends(get_db)):
  # print(f"Token received for get_current_user: {token}")
  try:
    token_data=jwt.decode_access_token(token)
    if token_data is None:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
      )
    
    # get the client_id from the token sub data if authorization is successful
    user = service.get_user_by_email(db, email=token_data.username)
    if user is None:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
      )
    return user 
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

