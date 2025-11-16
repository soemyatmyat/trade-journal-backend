from . import schemas, models, repository
from sqlalchemy.orm import Session 
from datetime import datetime

def create_position(db: Session, position: schemas.Position) -> schemas.Position | None:
  position = repository.create_position(db, models.Position(**position.model_dump())) # create in db
  return schemas.Position.model_validate(position) # convert back to pydantic model

def get_position(db: Session, id: int):
  try:
    existing_position = repository.get_position_by_id(db, id)
    if existing_position:
      return schemas.Position.model_validate(existing_position)
    else:
      return None
  except Exception as e:
    print(f"Error retrieving position by id: {e}")
    return None
  
def retrieve_positions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[schemas.Position]:  
  db_positions = repository.retrieve_positions_by_owner_id(db, user_id, skip, limit)
  positions = [schemas.Position.model_validate(position) for position in db_positions]
  return positions

def update_position(db: Session, position_id: int, position: schemas.Position) -> schemas.Position | None:
  try:
    existing_position = repository.get_position_by_id(db, position_id) # check if exiting in database
    if existing_position:
      for attr, value in position.model_dump(exclude_unset=True).items(): # only returns fields the user sent
        if value and getattr(existing_position, attr) != value: # loop and check if new value is not empty and not the same as existing ones 
          setattr(existing_position, attr, value) # otherwise, set the new value
      
      position = repository.update_position(db, existing_position)
      return schemas.Position.model_validate(position)
    else: 
      return None
  except Exception as e:
    print(f"Error updating position by id: {e}")
    return None

def remove_position(db: Session, position_id: int):
  try:
    existing_position = repository.get_position_by_id(db, position_id) # check if exiting in database
    if existing_position:
      repository.remove_position(db, existing_position)
      return existing_position
    else:
      return None
  except Exception as e:
    print(f"Error removing position by id: {e}")

# todo: weekly cron job to auto-close positions on expiry date