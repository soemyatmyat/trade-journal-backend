from . import schemas, models 
from sqlalchemy.orm import Session 

def create_position(db: Session, position: schemas.Position_Create):
    db_position = models.Position( # convert from schemas pydametic to orm model 
        ticker=position.ticker,
        category=position.category,
        qty=position.qty,
        option_price=position.option_price,
        trade_price=position.trade_price,
        open_date=position.open_date,
        close_date=position.close_date if position.close_date != "" else None,
        owner_id=position.owner_id,
        remark=position.remark
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position) # need it to get position_id 
    return db_position # give back orm

def get_position_by_id(db: Session, id: int):
    return db.query(models.Position).filter(models.Position.id == id).first()

def retrieve_positions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Position).filter(models.Position.owner_id == user_id).offset(skip).limit(limit).all()

def update_position_by_id(db: Session, position_id: int, position: schemas.Position):
    existing_position = get_position_by_id(db, position_id)
    if existing_position:
        for attr, value in position.model_dump(exclude_unset=True).items():
            if value and getattr(existing_position, attr) != value: # check if new value is not empty and not the same as existing ones 
                setattr(existing_position, attr, value)
        db.commit()
        return existing_position
    else: 
        return None 

def remove_position_by_id(db: Session, position_id: int):
    existing_position = get_position_by_id(db, position_id)
    if existing_position:
        db.delete(existing_position)
        db.commit()
        return existing_position
    return None

def orm_to_pydantic(position) -> schemas.Position_Details:
    return schemas.Position_Details(
        id=position.id,
        ticker=position.ticker,
        category=position.category,
        qty=position.qty,
        option_price=position.option_price,
        trade_price=position.trade_price,
        open_date=position.open_date,
        close_date=position.close_date,
        close_price=position.closed_price,
        remark=position.remark,
        is_active=position.is_active
    )
