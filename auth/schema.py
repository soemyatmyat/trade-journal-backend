# Pydantic models for serialization/deserialization, schema documentation and  data validation (need to do once only)

from pydantic import BaseModel, Field 
from positions import schemas 

class UserBase(BaseModel): # for both read and write 
    pass 

class UserCreate(UserBase): # create
    email: str 
    password: str 

class UserId(UserBase): # only id 
    id: int

class UserStatus(UserBase): 
    is_active: bool

class User(UserBase): # read (internal)
    id: int 
    is_active: bool
    positions: list[schemas.Position] = []

    class Config:
        orm_mode = True 

class UserInDB(User): # internal read 
    hashed_password: str

class Token(BaseModel): # create and read 
    access_token: str 
    token_type: str 

class TokenData(BaseModel):
    username: str | None = None 