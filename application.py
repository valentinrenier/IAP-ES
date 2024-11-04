from flask import Flask, redirect, render_template, request, url_for, session, make_response, jsonify, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import requests
import jwt
import pymysql
import time
from secret import COGNITO_LINK, CLIENT_ID, RESPONSE_TYPE, SCOPE, CALLBACK_URI, REDIRECT_URI, JWKS_URL, FLASK_SECRET
from data.db_secrets import DATABASE_USER, DATABASE_PW, DATABASE_IP, DATABASE_PORT, DATABASE_NAME, DATABASE_DIALECT, DATABASE_DRIVER
from data.models import Task
from apis.auth import check_token

application = Flask(__name__)
application.secret_key = FLASK_SECRET

if __name__ == '__main__' :
    application.run(host='0.0.0.0', port='80', debug=True)