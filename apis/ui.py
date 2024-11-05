from flask import render_template, make_response
from flask import session as sess
from flask_restx import Namespace, Resource
from data.models.Task import Task
from apis.auth import check_token
from sqlalchemy.orm import Session
from data.db_engine import engine

api=Namespace("ui",path="/ui",description="UI")

@api.route('/')
class index(Resource):
    def get(self):
        if check_token():
            username = sess['cognito:username']
            with Session(engine) as session :
                tasks = session.query(Task).filter(Task.user == username).order_by(Task.created_at.desc()).all()
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
