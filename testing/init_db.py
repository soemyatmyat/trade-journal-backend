from sqlalchemy.orm import sessionmaker
from database import engine 

from auth import schema, service 
from positions import service as positions_service
from positions import schemas as positions_schema
import json


def load_json(filename):
  print("filename: ", filename)
  with open(filename, 'r') as f:
    data = json.load(f)
  return data 
#  can't use Depends in your own functions, it has to be in FastAPI functions, mainly routes
def initialize_data():
  # get an instance of Sesson 
  Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  session = Session() 

  email='guest-5291'
  new_user = schema.UserCreate(email=email, password=']Jvx8BVDnB+{w')
  if (service.get_user_by_email(session, email)) is None:
    db_user = service.create_user(session, user=new_user)
  
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

  session.close() # close the instance 







  # # positions
  # positions = load_json('fake_positions.json')
  # for position in positions:
  #   db_position = position_model.Position(
  #     ticker = position.ticker,
  #     category = position.category,
  #     qty = position.qty,
  #     option_price = position.option_price,
  #     trade_price = position.trade_price,
  #     open_date = position.open_date,
  #     close_date = position.close_date,
  #     closed_price = position.closed_price,
  #     owner_id = db_user.id
  #   )
  #   db.add(db_position)
  # db.commit()
  # db.close()