from flask import render_template, make_response, request, Response
from flask_restx import Namespace, Resource
from apis.auth import check_token
from services.db_services import get_all_tasks

api=Namespace("ui",path="/ui",description="UI")

@api.route('/index')
class index(Resource):
    def get(self):
        check = check_token()

        if check is True or (isinstance(check, Response) and check.status_code == 200):
            order_by = request.args.get('order_by', 'created_at_desc')
            filters = request.args.getlist('filters[]')
            tasks = get_all_tasks(order_by, filters)
            
            response = make_response(
                render_template('index.html', tasks = tasks, user=True),
                200,
                {'Content-Type': 'text/html'}
                )
            if isinstance(check, Response):
                for cookie_name, cookie_value in check.headers.items():
                    if 'Set-Cookie' in cookie_name:
                        response.headers.add(cookie_name, cookie_value)
            return response
        else :
            return make_response(
                render_template('index.html', tasks = None, user=None),
                200,
                {'Content-Type': 'text/html'}
            )