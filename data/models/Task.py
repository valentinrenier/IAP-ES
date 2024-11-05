from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from . import Base

class Task(Base):
    __tablename__ = 'tasks' 

    id = Column(Integer, primary_key=True) 
    user = Column(String(100), primary_key=False, nullable=False)
    title = Column(String(1000), nullable=False) 
    description = Column(Text, nullable=False) 
    deadline = Column(DateTime, nullable=True)  
    priority = Column(Text, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
