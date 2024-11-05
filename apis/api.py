from flask import Flask, redirect, render_template, request, url_for, make_response, jsonify, flash
from flask_restx import Namespace,Resource,fields
from data.models import Task
from data.db_session import Session
from data.db_engine import engine
from services.db_services import delete_task, modify_task

api=Namespace("api",path="/api",description="Api operations")

@api.route('/delete/<int:task_id>')
class Delete(Resource):
    def post(self, task_id):
        if delete_task(task_id) == True :
            flash("Task successfully deleted", 'info')
            return {'message': 'Task updated successfully'}, 200
        else :
            flash("No task to delete", 'error')
            return {'error': 'Task not deleted'}, 404


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
