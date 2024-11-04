from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from data.db_secrets import DATABASE_DRIVER, DATABASE_DIALECT, DATABASE_IP, DATABASE_NAME, DATABASE_PORT, DATABASE_PW, DATABASE_USER
from .models import Base, Task

DATABASE_URL=f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PW}@{DATABASE_IP}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)