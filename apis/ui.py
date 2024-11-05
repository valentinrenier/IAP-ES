from flask import render_template, make_response, request
from flask import session as flask_session
from flask_restx import Namespace, Resource
from data.models.Task import Task
from apis.auth import check_token
from sqlalchemy.orm import Session
from data.db_engine import engine
from sqlalchemy import case

api=Namespace("ui",path="/ui",description="UI")

@api.route('/')
class index(Resource):
    def get(self):
        if check_token():

            with Session(engine) as session :
                priority_order = case(
                    (Task.priority == 'Low', 1),
                    (Task.priority == 'Medium', 2),
                    (Task.priority == 'High', 3),
                    else_=4  # Valeur par défaut si la priorité n'est pas définie
                )
                order_by = request.args.get('order_by', 'created_at_desc')  # Valeur par défaut
                query = session.query(Task).filter(Task.user == flask_session['cognito:username'])
                # Appliquer l'ordre de tri en fonction de la sélection
                if order_by == "created_at_asc":
                    query = query.order_by(Task.created_at.asc())
                elif order_by == "created_at_desc":
                    query = query.order_by(Task.created_at.desc())
                elif order_by == "priority_asc":
                    query = query.order_by(priority_order.asc())
                elif order_by == "priority_desc":
                    query = query.order_by(priority_order.desc())
                elif order_by == "deadline_asc":
                    query = query.order_by(Task.deadline.asc())
                elif order_by == "deadline_desc":
                    query = query.order_by(Task.deadline.desc())

                tasks = query.all()
                return make_response(
                    render_template('index.html', tasks = tasks, user=True),
                    200,
                    {'Content-Type': 'text/html'}
                )
        else :
            return make_response(
                render_template('index.html', tasks = None, user=None),
                200,
                {'Content-Type': 'text/html'}
            )