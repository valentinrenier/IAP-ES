from flask import render_template, request, make_response, flash, redirect, url_for
from flask import session as flask_session
from flask_restx import Namespace,Resource,fields
from data.models.Task import Task
from sqlalchemy.orm import Session
from data.db_engine import engine
from services.db_services import delete_task, modify_task, add_task

api=Namespace("api",path="/api",description="Api operations")

@api.route('/add')
class Add(Resource):
    def post(self):
        data = request.get_json()  # Ou request.form si vous utilisez form-urlencoded
        title = data.get('title')
        description = data.get('description')
        deadline = data.get('deadline')
        priority = data.get('priority')

        if add_task(title, description, priority, deadline) == True :
            flash("Task successfully added", 'info')
            return {'message': 'Task added'}, 200
        else :
            flash("No task to delete", 'error')
            return {'error': 'Task not deleted'}, 404

@api.route('/delete/<int:task_id>')
class Delete(Resource):
    def post(self, task_id):
        if delete_task(task_id) == True :
            flash("Task successfully deleted", 'info')
            with Session(engine) as session :
                tasks = session.query(Task).filter(Task.user == flask_session['cognito:username']).order_by(Task.created_at.desc()).all()
                return make_response(
                    render_template('index.html', tasks = tasks, user=True),
                    200,
                    {'Content-Type': 'text/html'}
                )
        else :
            flash("Task not deleted", 'error')
            with Session(engine) as session :
                tasks = session.query(Task).filter(Task.user == flask_session['cognito:username']).order_by(Task.created_at.desc()).all()
                return make_response(
                    render_template('index.html', tasks = tasks, user=True),
                    400,
                    {'Content-Type': 'text/html'}
                )
            return {'error': 'Task not deleted'}, 400


@api.route('/modify/<int:task_id>', methods=['POST'])
class Modify(Resource):
    def post(self, task_id):
        data = request.json
        if modify_task(task_id, data) == True :
            flash("Task successfully modified", 'info')
            return {'message': 'Task updated successfully'}, 200  # Rediriger vers la page principale
        else : 
            flash("Task not modified", 'error')
            return {'error': 'Task not modified'}, 404
