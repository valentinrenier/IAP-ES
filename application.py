from flask import Flask, redirect, render_template, request, url_for, session, make_response, jsonify, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import requests
import jwt
import pymysql
import time


COGNITO_LINK = "https://todolistiap.auth.us-east-1.amazoncognito.com"
CLIENT_ID = "7sf2h4tqn4cgpoiuhcj1fa740h"
RESPONSE_TYPE = "code"
SCOPE = "email+openid+profile"
CALLBACK_URI = "http://localhost:5000/callback"
REDIRECT_URI = "http://localhost:5000/"

DATABASE_USER = 'admin'
DATABASE_PW = 'fCH9vRhZA54$d&V'
DATABASE_IP = 'database-1.crymgyucgybh.us-east-1.rds.amazonaws.com'
DATABASE_PORT = 3306
DATABASE_DIALECT = 'mysql'
DATABASE_DRIVER = ''
DATABASE_NAME = 'todolist'

JWKS_URL = 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_8XJmsn1aX/.well-known/jwks.json'

application = Flask(__name__)
application.secret_key = 'q[3rycB)I0tA,8bJRF78t.B4*($2+5Gc'
application.config['SQLALCHEMY_DATABASE_URI'] = f'{DATABASE_DIALECT}:{DATABASE_DRIVER}//{DATABASE_USER}:{DATABASE_PW}@{DATABASE_IP}:{DATABASE_PORT}/{DATABASE_NAME}'
db = SQLAlchemy(application)

def get_public_key(jwk):
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
    return public_key

def is_token_expired(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        if 'exp' in decoded_token:
            return decoded_token['exp'] < time.time()
    except jwt.ExpiredSignatureError:
        return True  
    except Exception as e:
        return True  # Considérer comme expiré en cas d'erreur
    return False  # Token valide

def check_token():
    token = request.cookies.get('auth_token')

    if not token:
        return False

    kid = jwt.get_unverified_header(token)['kid']
    jwks = requests.get(JWKS_URL).json()
    key = next((key for key in jwks['keys'] if key['kid'] == kid), None)

    if not key:
        return False

    public_key = get_public_key(key)

    try:
        # Décoder et valider le token avec la clé
        jwt.decode(token, public_key, algorithms=['RS256'])
        return not is_token_expired(token)
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def createDB():
    connection = pymysql.connect(host=DATABASE_IP, user=DATABASE_USER, password=DATABASE_PW)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
    finally:
        connection.close()

class Task(db.Model):
    __tablename__ = 'tasks' 

    id = db.Column(db.Integer, primary_key=True) 
    user = db.Column(db.String(100), primary_key=False, nullable=False)
    title = db.Column(db.String(1000), nullable=False) 
    description = db.Column(db.Text, nullable=False) 
    deadline = db.Column(db.Date, nullable=True)  
    priority = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False)

createDB()
with application.app_context():
    db.create_all()



@application.route('/', methods=['GET', 'POST'])
def index():
    if check_token():
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            deadline = request.form.get('deadline')
            priority = request.form.get('priority')
            
            new_task = Task(title=title,
                            user=session['cognito:username'],
                            description=description,
                            priority = priority,
                            deadline = deadline,
                            completed = False,
                            created_at = datetime.now())

            # Ajoute la tâche et enregistre dans la base de données
            db.session.add(new_task)
            db.session.commit()
            # tasks = Task.query.filter(Task.user.ilike(f"%{session['cognito:username']}%")).all()
            flash("Task successfully added", 'info')
            return redirect(url_for('index')) 
        
        tasks = Task.query.filter(Task.user.ilike(f"%{session['cognito:username']}%")).order_by(Task.created_at.desc()).all()
        formatted_tasks = []
        for task in tasks:
            if task.deadline :
                task.deadline = task.deadline.strftime('%d.%m.%Y')
            formatted_tasks.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'deadline': task.deadline,  # Formatage pour l'affichage
                'user': task.user,
                'completed': task.completed
            })
        return render_template('index.html', tasks = formatted_tasks, user=session['preferred_username'])

    return render_template('index.html', tasks = None, user=None)

@application.route("/login")
def login():
    return redirect(f"{COGNITO_LINK}/login?client_id={CLIENT_ID}&response_type={RESPONSE_TYPE}&scope={SCOPE}&redirect_uri={CALLBACK_URI}")


@application.route('/callback')
def callback():
    code = request.args.get('code')
    
    token_url = f"{COGNITO_LINK}/oauth2/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': CALLBACK_URI,
    }
    
    response = requests.post(token_url, data=data)
    tokens = response.json()
    
    session['access_token'] = tokens.get('access_token')
    access_token = tokens.get('access_token')
    if access_token is None:
        return jsonify({'message': 'Access token not found in response!'}), 400
    
    id_token = tokens['id_token']
    user_info = jwt.decode(id_token, options={"verify_signature": False})
    
    session['preferred_username'] = user_info.get("preferred_username", None)
    session['cognito:username'] = user_info.get("cognito:username", None)
    

    response = make_response(redirect(url_for('index')))
    response.set_cookie("auth_token", access_token, max_age=timedelta(hours=1), httponly=True)
    flash("Successfully logged in", 'info')

    return response

@application.route('/logout')
def logout():
    session.pop('access_token', None)
    session.pop('preferred_username', None)
    session.pop('username', None)
    response = make_response(redirect(f"{COGNITO_LINK}/logout?client_id={CLIENT_ID}&logout_uri={REDIRECT_URI}"))
    response.set_cookie('auth_token', '', expires=0)
    flash("Successfully logged out", 'info')
    return response


@application.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        flash("No task to delete", 'error')
        return redirect(url_for('index')) 
    db.session.delete(task)
    db.session.commit()

    flash("Task successfully deleted", 'info')
    return redirect(url_for('index'))


@application.route('/modify_task/<int:task_id>', methods=['POST'])
def modify_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        flash("Task not modified", 'error')
        return jsonify({'error': 'Task not found'}), 404
    if task :
        data = request.json
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.deadline = data.get('deadline', task.deadline)
        task.priority = data.get('priority', task.priority)
        task.completed = data.get('completed', task.completed)

        db.session.commit()  # Valider les changements dans la base de données
        flash("Task successfully modified", 'info')
        return jsonify({'message': 'Task updated successfully'}), 200  # Rediriger vers la page principale

if __name__ == '__main__' :
    application.run(host='127.0.0.1', port='5000', debug=True)