from sqlalchemy.orm import sessionmaker
from .db_engine import engine
from .models.Task import Task

Session = sessionmaker(bind=engine)
session = Session()

with Session() as session:
    username = 'gross'  # Assurez-vous que cette valeur est bien définie
    tasks = (
        session.query(Task)
        .filter(Task.user == username)
        .order_by(Task.created_at.desc())
        .all()
    )
