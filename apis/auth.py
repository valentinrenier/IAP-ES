from flask import Flask, redirect, render_template, request, url_for, session, make_response, jsonify, flash
from flask_restx import Namespace,Resource,fields
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import requests
import jwt
import time
from secret import COGNITO_LINK, CLIENT_ID, RESPONSE_TYPE, SCOPE, CALLBACK_URI, REDIRECT_URI, JWKS_URL

api=Namespace("auth",path="/auth",description="Authentication operations")

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
        return True
    return False

def check_token():
    access_token = request.cookies.get('access_token')

    if not access_token:
        return False

    kid = jwt.get_unverified_header(access_token)['kid']
    jwks = requests.get(JWKS_URL).json()
    key = next((key for key in jwks['keys'] if key['kid'] == kid), None)

    if not key:
        return False

    public_key = get_public_key(key)

    try:
        jwt.decode(access_token, public_key, algorithms=['RS256'])
        if is_token_expired(access_token):
            if refresh_access_token(): 
                return True
            return False

        else : 
            return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    
def refresh_access_token():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return {'error': 'No refresh token found'}, 400
    if is_token_expired(refresh_token):
        return False

    token_url = f"{COGNITO_LINK}/oauth2/token"
    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'refresh_token': refresh_token,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code != 200:
        return False

    tokens = response.json()
    access_token = tokens.get('access_token')
    if not access_token:
        return {'error': 'No access token found in refresh response'}, 400
    
    response.set_cookie("access_token", access_token, max_age=timedelta(hours=1), httponly=True, secure=True)

    return True 

@api.route("/login")
class Login(Resource):
    def get(self):
        return redirect(f"{COGNITO_LINK}/login?client_id={CLIENT_ID}&response_type={RESPONSE_TYPE}&scope={SCOPE}&redirect_uri={CALLBACK_URI}")


@api.route('/callback')
class Callback(Resource):
    def get(self):
        code = request.args.get('code')
        
        token_url = f"{COGNITO_LINK}/oauth2/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'code': code,
            'redirect_uri': CALLBACK_URI,
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return {'error': 'Failed to retrieve tokens from Cognito'}, response.status_code

        tokens = response.json()
        
        session['access_token'] = tokens.get('access_token')
        access_token = tokens.get('access_token')
        if access_token is None:
            return {'message': 'Access token not found in response!'}, 400
        
        refresh_token = tokens.get('refresh_token')
        if refresh_token is None :
            return {'message': 'Refresh token not found in response!'}, 400

        id_token = tokens['id_token']
        if id_token is None:
            return {'error': 'ID token not found in response'}, 400
        
        #TODO Secure this
        user_info = jwt.decode(id_token, options={"verify_signature": False})

        session['preferred_username'] = user_info.get("preferred_username", None)
        session['cognito:username'] = user_info.get("cognito:username", None)
        

        response = make_response(redirect(url_for('ui_index')), 302, {'Content-Type': 'text/html'})
        response.set_cookie("access_token", access_token, max_age=timedelta(seconds=1), httponly=True, secure=True)
        response.set_cookie("refresh_token", refresh_token, max_age=timedelta(days=30), httponly=True, secure=True)
        flash("Successfully logged in", 'info')

        return response

@api.route('/logout')
class Logout(Resource):
    def get(self):
        session.clear()
        response = make_response(redirect(f"{COGNITO_LINK}/logout?client_id={CLIENT_ID}&logout_uri={REDIRECT_URI}"))
        response.set_cookie('access_token', '', expires=0)
        response.set_cookie('refresh_token', '', expires=0)
        response.set_cookie('session', '', expires=0)
        flash("Successfully logged out", 'info')
        return response
