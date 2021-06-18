# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This is the main server file for a gcp REST API. It contains all 
# the handlers required for a user to login and authenticate. In
# order to use the API, the user must first login at the index page.
# Once they log in, they'll receive a JWT, which they can use inside
# Postman as their bearer token.
# ================================================================
from google.cloud import datastore
from flask import Flask, request, jsonify, _request_ctx_stack
from flask import redirect, render_template, session, url_for
import requests
from functools import wraps
import json
from six.moves.urllib.request import urlopen
from flask_cors import cross_origin
from jose import jwt
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import constants
import auth0 as auth
import user
import boat_controller
import load_controller


# Create the flask instance and set up the secret key for sessions.
# Register the blueprints for the endpoints outside of logging in.
# Also create the datastore instance and set up auth0 for authentication.
app = Flask(__name__)
app.secret_key = constants.SECRET_KEY
app.register_blueprint(user.bp)
app.register_blueprint(boat_controller.bp)
app.register_blueprint(load_controller.bp)
client = datastore.Client()
oauth = OAuth(app)
auth0 = auth.register_auth0(oauth)


@app.route('/')
def index():
    """ 
    Handler for home ui page. 
    """
    return render_template("home.html")


@app.route('/ui_login')
def ui_login():
    """
    Redirects user to the auth0 login page.
    """
    return auth0.authorize_redirect(redirect_uri=constants.CALLBACK_URL)


@app.route('/callback')
def callback_handling():
    """
    Handles response from auth0 once user logs in. Stores the user info
    in a flask session. Also creates a user entity in the datastore if
    it's the user's first time logging in.
    """
    id_token = auth0.authorize_access_token()["id_token"]
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    session['jwt_payload'] = userinfo

    # check if the user already exists in datastore
    query = client.query(kind=constants.USERS)
    results = list(query.fetch())
    user_exists = False

    for e in results:
        workable = json.dumps(e)
        workable = json.loads(workable)
        if workable["unique_id"] == userinfo["sub"]:
            user_exists = True
            break
    
    if user_exists:
        return render_template('dashboard.html', jwt=id_token, unique_id=userinfo["sub"])
    else:
        # create the new user entity if first time logging in
        new_user = datastore.entity.Entity(key=client.key(constants.USERS))
        new_user.update({"unique_id":userinfo["sub"], "nickname": userinfo["nickname"], "boats": []})
        client.put(new_user)
        return render_template('dashboard.html', jwt=id_token, unique_id=userinfo["sub"])
        

@app.route('/dashboard')
def dashboard():
    """
    Page that user gets redirected to once they've logged in. 
    Displays a JWT used for authentication with the API.
    """
    return render_template('dashboard.html', userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))    


if __name__ == '__main__':
    app.run(host='https://hw4-intermediate-marcusz.wn.r.appspot.com', debug=True)