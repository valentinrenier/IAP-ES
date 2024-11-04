from decimal import Decimal
from data.models.Task import Task
from sqlalchemy.orm import Session
from data.db_engine import engine
    
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from flask import flash

def delete_task(task_id):
    with Session(engine) as session :
        task = Task.query.get(task_id)
        if task is None:
            return flash("No task to delete", 'error')
        session.delete(task)
        session.commit()

        return flash("Task successfully deleted", 'info')
    
def modify_task(task_id, data):
    with Session(engine) as session :
        task = Task.query.get(task_id)
        if task is None:
            return False
        if task :
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            task.deadline = data.get('deadline', task.deadline)
            task.priority = data.get('priority', task.priority)
            task.completed = data.get('completed', task.completed)
            

            session.commit()  # Valider les changements dans la base de données
            flash("Task successfully modified", 'info')
            return flash("Task successfully modified", 'info')  # Rediriger vers la page principale