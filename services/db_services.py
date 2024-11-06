from decimal import Decimal
from data.models.Task import Task
from sqlalchemy.orm import Session
from data.db_engine import engine
from flask import session as flask_session
    
from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

from flask import flash, request
from sqlalchemy import case

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
    
def get_all_tasks(order_by, filters):
    priority_order = case(
        (Task.priority == 'Low', 1),
        (Task.priority == 'Medium', 2),
        (Task.priority == 'High', 3),
        else_=4
    )
    
    order_by_options = {
        "created_at_asc": Task.created_at.asc(),
        "created_at_desc": Task.created_at.desc(),
        "priority_asc": priority_order.asc(),
        "priority_desc": priority_order.desc(),
        "deadline_asc": Task.deadline.asc(),
        "deadline_desc": Task.deadline.desc(),
        "completed_asc": Task.completed.asc(),
        "completed_desc": Task.completed.desc(),
    }

    order_by_method = order_by_options.get(order_by)
    
    show_completed = 'completed' in filters
    show_not_completed = 'not-completed' in filters
    show_priorities = [f.split('-')[0] for f in filters if 'priority' in f]

    with Session(engine) as session :
        query = session.query(Task).filter(Task.user == flask_session['cognito:username'])
        
        #Filtering
        if show_completed and show_not_completed :
            pass
        elif show_completed :
            query = query.filter(Task.completed == True)
        elif show_not_completed :
            query = query.filter(Task.completed == False)
        if show_priorities :
            query = query.filter(Task.priority.in_(show_priorities))
            
        if order_by_method:
            query = query.order_by(order_by_method)
        tasks = query.all()
        return tasks

