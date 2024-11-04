from sqlalchemy.orm import sessionmaker
from .db_engine import engine

Session = sessionmaker(bind=engine)
session = Session()