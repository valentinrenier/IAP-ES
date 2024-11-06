from flask import render_template, make_response, request
from flask_restx import Namespace, Resource
from apis.auth import check_token
from services.db_services import get_all_tasks

api=Namespace("ui",path="/ui",description="UI")

@api.route('/')
class index(Resource):
    def get(self):
        if check_token():
            order_by = request.args.get('order_by', 'created_at_desc')
            filters = request.args.getlist('filters[]')
            tasks = get_all_tasks(order_by, filters)
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