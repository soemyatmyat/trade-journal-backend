from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from database import get_db 
from sqlalchemy.orm import Session 
from . import service, schema, utils

router = APIRouter() # need to import this to main.py

@router.post("/register", tags=["users"], include_in_schema=False)
async def register_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session=Depends(get_db)):
    username, password = form_data.username, form_data.password 
    existing_user = service.get_user_by_email(db, email=username)
    if existing_user: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    new_user = schema.UserCreate(email=username, password=password)
    service.create_user(db, user=new_user)    

@router.post("/token", response_model=schema.Token, tags=["users"], include_in_schema=False) # return bearer token
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session=Depends(get_db)) -> schema.Token:
    user = service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = utils.create_access_token(data={"sub": user.email})
    return schema.Token(access_token=access_token, token_type="bearer") # return token

@router.post("/logout", include_in_schema=False) 
async def logout(token: str = Depends(service.oauth2_scheme)):
    # revoke the token access (it will expire by default in 15 mins anyway)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data=utils.decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    utils.revoke_token(token)

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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data=utils.decode_access_token(token)
        if token_data is None:
            raise credentials_exception
        user = service.get_user_by_email(db, email=token_data.username)
        if user is None:
            raise credentials_exception
        return user 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

