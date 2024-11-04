from flask import render_template, session, make_response
from flask_restx import Namespace, Resource
from data.models import Task
from apis.auth import check_token
from data.db_session import Session
from data.db_engine import engine

api=Namespace("ui",path="/ui",description="UI")

@api.route('/')
class index(Resource):
    def get(self):
        if check_token():
            tasks = Task.query.filter(Task.user.ilike(f"%{session['cognito:username']}%")).order_by(Task.created_at.desc()).all()
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