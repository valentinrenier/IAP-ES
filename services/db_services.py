from decimal import Decimal
from data.models.Task import Task
from sqlalchemy.orm import Session
from data.db_engine import engine
from flask import session as flask_session
    
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from flask import flash

def add_task(title, description, priority, deadline):
    with Session(engine) as session :
        try :
            new_task = Task(
                user = flask_session['cognito:username'],
                title = title,
                description = description,
                priority= priority,
                deadline = deadline,
                created_at = datetime.now()
            )
            session.add(new_task)
            session.commit()
            return True
        except :
            return False 


def delete_task(task_id):
    try :
        with Session(engine) as session :
            task = session.query(Task).filter(Task.id == task_id).one()
            if task is None:
                return False
            session.delete(task)
            session.commit()

            return True
    except :
        return False
    
def modify_task(task_id, data):
    try :
        with Session(engine) as session :
            task = session.query(Task).filter(Task.id == task_id).one()
            if task :
                task.title = data.get('title', task.title)
                task.description = data.get('description', task.description)
                task.deadline = data.get('deadline', task.deadline)
                task.priority = data.get('priority', task.priority)
                task.completed = data.get('completed', task.completed)
                
                session.commit() 
                flash("Task successfully modified", 'info')
                return True 
    except :
        return False