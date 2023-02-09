from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///arcade.db")
conn = engine.connect()
session = Session(bind=engine)
