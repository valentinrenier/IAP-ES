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
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        deadline = data.get('deadline')
        priority = data.get('priority')

        if add_task(title, description, priority, deadline) == True :
            flash("Task successfully added", 'info')
            return make_response(
                redirect(url_for('ui_index')), 
                302, 
                {'Content-Type': 'text/html'}
                )
        else :
            flash("No task to delete", 'error')
            return make_response(
                redirect(url_for('ui_index')), 
                302, 
                {'Content-Type': 'text/html'}
                )

@api.route('/delete/<int:task_id>')
class Delete(Resource):
    def post(self, task_id):
        if delete_task(task_id) is True :
            flash("Task successfully deleted", 'info')
            return make_response(
                redirect(url_for('ui_index')), 
                302, 
                {'Content-Type': 'text/html'}
                )
        else :
            flash("Task not deleted", 'error')
            return make_response(
                    redirect(url_for('ui_index')), 
                    302, 
                    {'Content-Type': 'text/html'}
                    )


@api.route('/modify/<int:task_id>')
class Modify(Resource):
    def post(self, task_id):
        data = request.json
        if modify_task(task_id, data) is True :
            flash("Task successfully modified", 'info')
            return make_response(
                redirect(url_for('ui_index')), 
                302, 
                {'Content-Type': 'text/html'}
                )
        else : 
            flash("Task not modified", 'error')
            return make_response(
                redirect(url_for('ui_index')), 
                302, 
                {'Content-Type': 'text/html'}
                )
