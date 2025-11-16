from sqlalchemy.orm import Session 
from . import models # database models

# read
def get_user(db: Session, user_id: int) -> models.User | None:
  return db.query(models.User).filter(models.User.id == user_id).first()

# read
def get_user_by_email(db: Session, email: str) -> models.User | None:
  return db.query(models.User).filter(models.User.email == email).first()

# read
def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
  return db.query(models.User).offset(skip).limit(limit).all()

# create
def create_user(db: Session, user: models.User) -> models.User:
  db.add(user)
  db.commit()
  db.refresh(user)
  return user

# update
def update_user(db: Session, user: models.User) -> models.User:
  db.merge(user) # merge is used to update an existing record
  db.commit()
  db.refresh(user)
  return user

# delete
def delete_user(db: Session, user: models.User) -> None:
  db.delete(user)
  db.commit()

