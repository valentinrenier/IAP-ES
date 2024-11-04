from flask import Flask
from secret import FLASK_SECRET
from apis import api

application = Flask(__name__)
application.secret_key = FLASK_SECRET

def create_app():
    application = Flask(__name__)
    api.init_app(application)
    application.secret_key=FLASK_SECRET
    return application

if __name__ == '__main__' :
    application.run(host='0.0.0.0', port='80', debug=True)