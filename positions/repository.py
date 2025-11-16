from sqlalchemy.orm import Session 
from . import models # database models

# create
def create_position(db: Session, position: models.Position) -> models.Position:
  db.add(position)
  db.commit()
  db.refresh(position)
  return position

# read
def get_position_by_id(db: Session, position_id: int) -> models.Position | None:
  return db.query(models.Position).filter(models.Position.id == position_id).first()

# read all
def retrieve_positions_by_owner_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[models.Position]:
  return db.query(models.Position)\
            .filter(models.Position.owner_id == user_id)\
            .order_by(models.Position.open_date.desc(), models.Position.id.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

# update
def update_position(db: Session, position: models.Position) -> models.Position:
  db.merge(position) # merge is used to update an existing record
  db.commit()
  db.refresh(position)
  return position

# delete
def remove_position(db: Session, position: models.Position) -> models.Position | None:
  db.delete(position)
  db.commit()
  return None

