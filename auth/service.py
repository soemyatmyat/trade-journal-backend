from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schema, repository # get sql models, Pydantic schema, Repository functions
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # password-hash before storing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # tell FastAPI where to get the token

class EmailAlreadyRegisteredError(Exception):
  pass

def get_user(db: Session, user_id: int) -> schema.UserId | None:
  existing_user = repository.get_user(db, user_id)
  if not existing_user:
    return None
  return schema.UserId.model_validate(existing_user)

def get_user_by_email(db: Session, email: str) -> schema.UserId | None:
  existing_user = repository.get_user_by_email(db, email)
  if not existing_user:
    return None 
  return schema.UserId.model_validate(existing_user) # Build Pydantic object with ORM model

def create_user(db: Session, username: str, password: str) -> schema.UserId | None:
  try:
    existing_user = get_user_by_email(db, email=username)
    if existing_user:
      raise EmailAlreadyRegisteredError(f"Email {username} is already registered.")
    hashed_pwd = pwd_context.hash(password)
    new_user = schema.UserCreate(email=username, password=password) # Pydantic model
    db_user = models.User(email=new_user.email, hashed_password=hashed_pwd)   # convert to ORM model 
    user = repository.create_user(db, db_user) 
    return schema.UserId.model_validate(user) # back to Pydantic model without hashed password
  except Exception as e:
    print(f"Error creating user: {e}")
    return None

def verify_password(plain_password, hashed_password) -> bool:
  return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str) -> schema.UserId | None:
  existing_user = get_user_by_email(db, username)
  if not existing_user:
    return None
  db_user = repository.get_user(db, existing_user.id)  # get full user with hashed password
  if db_user:
    validate_user = schema.UserInDB.model_validate(db_user) # internal only 
    if not verify_password(password, validate_user.hashed_password):
      return None
    return schema.UserId.model_validate(existing_user) # take the user without the hashed password and return user
  return None

