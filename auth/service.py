from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session 

from . import schema, model # get sql models and Pydantic schema
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # what does this line doe?


def get_user(db: Session, user_id: int):
    return db.query(model.User).filter(model.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> schema.UserId: 
    user = db.query(model.User).filter(model.User.email == email).first() 
    if user:
        return schema.UserId(id = user.id)
    return None     

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.User).offset(skip).limit(limit).all() 

def create_user(db: Session, user: schema.UserCreate):
    hashed_pwd = pwd_context.hash(user.password)
    # convert to ORM model 
    db_user = model.User(email=user.email, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user # what does it return??

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_email(db, username)
    if not user:
        return False
    user = get_user(db, user.id)
    if not verify_password(password, user.hashed_password):
        return False
    return user
