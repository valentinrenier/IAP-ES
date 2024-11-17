from sqlalchemy.orm import sessionmaker
from .db_engine import engine
from .models.Task import Task

Session = sessionmaker(bind=engine)
session = Session()

