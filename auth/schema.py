# Pydantic models for serialization/deserialization, schema documentation and  data validation (need to do once only)

import email
from pydantic import BaseModel, Field 
from positions import schemas 

class UserBase(BaseModel): # for both read and write 
  pass 

class UserCreate(UserBase): # create
  email: str 
  password: str 

class UserId(UserBase): # only id, email and is_active
  id: int
  email: str
  is_active: bool
  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models

class User(UserBase): # read (internal)
  id: int 
  email: str
  is_active: bool
  positions: list[schemas.Position] = []

  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models

class UserInDB(User): # internal read 
  hashed_password: str
  
  model_config = {
    "from_attributes": True
  }  # Enable ORM mode to work with SQLAlchemy models

class Token(BaseModel): # create and read 
  access_token: str 
  token_type: str 

class TokenData(BaseModel):
  username: str | None = None 