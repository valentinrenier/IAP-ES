from flask import redirect, request, url_for, session, make_response, flash
from flask_restx import Namespace,Resource
from datetime import timedelta
import requests
import jwt
import time
from secret import COGNITO_LINK, CLIENT_ID, RESPONSE_TYPE, SCOPE, CALLBACK_URI, REDIRECT_URI, JWKS_URL
from services.logging_service import logger

api=Namespace("auth",path="/auth",description="Authentication operations")

def get_public_key(jwk):
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
    return public_key

def is_token_expired(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        if 'exp' in decoded_token:
            logger.info(f"Expiration of token : {decoded_token['exp']}, time : {time.time()}")
            return decoded_token['exp'] < time.time()
        else :
            logger.info("No expiration found")
            return False
    except jwt.ExpiredSignatureError:
        return True  
    except Exception as e:
        return True
    return False

def check_token():
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')

    if not access_token and not refresh_token:
        logger.info("No access_token nor refresh_token")
        return False
    elif not access_token and refresh_token :
        return refresh_access_token()

    kid = jwt.get_unverified_header(access_token)['kid']
    jwks = requests.get(JWKS_URL).json()
    key = next((key for key in jwks['keys'] if key['kid'] == kid), None)

    if not key:
        logger.info("No key found")
        return False

    public_key = get_public_key(key)

    try:
        jwt.decode(access_token, public_key, algorithms=['RS256'])
        if is_token_expired(access_token):
            logger.info("Token expired")
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
        logger.info('Refresh token not set')
        return False
    if is_token_expired(refresh_token):
        logger.info("Refresh token is expired")
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
        logger.info(f"The response code isn't 200, error : {response.status_code}")
        return False

    tokens = response.json()
    access_token = tokens.get('access_token')
    if not access_token:
        logger.info("Cognito didn't send the access token in the response")
        return False
    
    response = make_response("Token refreshed")
    response.set_cookie("access_token", access_token, max_age=timedelta(seconds=10).total_seconds(), httponly=True, secure=True)
    logger.info("Token successfully refreshed")
    return response 

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
        response.set_cookie("access_token", access_token, max_age=timedelta(seconds=10).total_seconds(), httponly=True, secure=True)
        response.set_cookie("refresh_token", refresh_token, max_age=timedelta(days=30).total_seconds(), httponly=True, secure=True)
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
