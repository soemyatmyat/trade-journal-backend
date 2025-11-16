from sqlalchemy.orm import sessionmaker
from database import engine 
import json
from auth import schema, service 
from positions import service as positions_service
from positions import schemas as positions_schema

def load_json(filename):
  print("filename: ", filename)
  with open(filename, 'r') as f:
    data = json.load(f)
  return data 

def seed_demo_user():
  # get an instance of Session 
  Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  session = Session() 

  # import positions service and schema here to avoid circular imports
  try:
    email='guest-5291'
    existing = service.get_user_by_email(session, email)
    if existing:
      print("Demo user already exists.")
      return
    
    # create demo user object
    new_user = schema.UserCreate(email=email, password=']Jvx8BVDnB+{w')
    db_user = service.create_user(session, user=new_user)

    # create demo positions for the user
    positions = load_json('testing/fake_positions.json')
    for position in positions:
      db_position = positions_schema.Position_Create(
        ticker = position["ticker"],
        category = position["category"],
        qty = position["qty"],
        option_price = position["option_price"],
        trade_price = position["trade_price"],
        open_date = position["open_date"],
        close_date = position["close_date"],
        closed_price = position["closed_price"],
        owner_id = db_user.id
      )      
      db_position = positions_service.create_position(session, db_position)

    session.add(db_user)
    session.commit()
    print("Demo user created successfully.")
  finally:
    session.close() # close the instance 