import os
import random
import string
from flask import Flask, render_template, request, url_for, redirect
from flask import session as login_session
from dbsetup import User, Item, Category
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import google_auth_oauthlib.flow
import googleapiclient.discovery
import httplib2
import json
from flask import make_response
import requests

# Fix for SSL error
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
DBSession = sessionmaker(bind=engine)
session = DBSession()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(PROJECT_DIR, 'client_secrets.json')
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


@app.route('/login', methods=['GET'])
def login_route():

    if 'user_name' in login_session:
        return "logged in"

    """
    Redirects user to Google auth link
    """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    login_session['state'] = state

    return redirect(authorization_url)


@app.route('/logout', methods=['GET'])
def logout_route():
    """
    Cleansup credentials from session and
    as result user logged out
    """
    if 'credentials' in login_session:
        del login_session['credentials']
        del login_session['state']
        del login_session['user_id']
        del login_session['user_name']
        del login_session['user_photo']
        del login_session['catalog_user_id']

        return redirect(url_for('index'))


@app.route('/oauth2callback')
def oauth2callback():
    """
    Handles callback call from google, and finished authorization,
    then retrieves user info and saves it into session till next login
    """
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = login_session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url

    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    login_session['credentials'] = credentials_to_dict(credentials)

    # requesting user info
    service = googleapiclient.discovery.build('people', 'v1',
                                              credentials=credentials)
    result = service.people().get(resourceName='people/me',
                                  personFields='names,photos').execute()

    user_id = result['resourceName']
    user_name = result['names'][0]['displayName']
    user_photo = url_for('static', filename='images/no-profile-photo.svg')

    if len(result['photos']) > 0:
        user_photo = result['photos'][0]['url']

    # saving user info to session so it remains persistent
    # this updates on login process
    login_session['user_id'] = user_id
    login_session['user_name'] = user_name
    login_session['user_photo'] = user_photo

    # check if existing user, if not then lets add them
    user = session.query(User).filter_by(googleid=user_id).first()
    if not user:
        user = User(name=user_name, googleid=user_id)
        session.add(user)
        session.commit()
        catalog_user = session.query(User).filter_by(googleid=user_id).first()
        login_session['user_id'] = user_id
        login_session['catalog_user_id'] = catalog_user.id
    elif user:
        login_session['catalog_user_id'] = user.id

    return redirect(url_for('index'))


@app.route("/")
def index():
    categories = session.query(Category).all()
    return_categories = []
    for c in categories:
        c = c.serialize
        return_categories.append(c)

    if 'user_name' in login_session:
        user = login_session['user_name']
    elif 'user_name' not in login_session:
        user = "Please Login"

    return render_template("index.html",
                           categories=return_categories,
                           user=user)


@app.route("/category/<int:id>/<string:name>")
def view_category(id, name):
    items = session.query(Item).filter_by(category_id=id)
    return_items = []
    for c in items:
        c = c.serialize
        return_items.append(c)

    return render_template("category.html",
                           items=return_items, name=name, id=id,
                           catalog_user_id=login_session['catalog_user_id'])


@app.route("/item/<int:id>/<string:name>")
def view_item(id, name):
    item = session.query(Item).filter_by(id=id).one()
    return render_template("item.html", item=item, name=name)


@app.route("/add/<int:id>/")
def add_item(id):
    if request.method == 'GET':
        categories = session.query(Category).all()
        return_categories = []
        for c in categories:
            c = c.serialize
            return_categories.append(c)

        return render_template("add.html", categories=return_categories, id=id)


@app.route("/addItem", methods=['POST'])
def add_new_item():
    if request.method == 'POST':
        newItem = Item(
            name=request.form['inputName'],
            description=request.form['inputDescription'],
            category_id=request.form['selectCategory'],
            user_id=login_session['catalog_user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('index'))


@app.route("/edit/<int:id>/")
def edit_item(id):
    if request.method == 'GET':
        item = session.query(Item).filter_by(id=id).first()
        if item.user_id == login_session['catalog_user_id']:
            categories = session.query(Category).all()
            return_categories = []
            for c in categories:
                c = c.serialize
                return_categories.append(c)
            return render_template("edit.html", item=item,
                                   categories=return_categories)
        elif item.user_id != login_session['catalog_user_id']:
            return render_template("accessDenied.html")


@app.route("/editItem/<int:id>", methods=['POST'])
def save_edit_item(id):
    if request.method == 'POST':
        item = session.query(Item).filter_by(id=id).first()
        if item.user_id == login_session['catalog_user_id']:
            item.name = request.form['inputName']
            item.description = request.form['inputDescription']
            item.category_id = request.form['selectCategory']
            item.user_id = login_session['catalog_user_id']
            session.commit()
            return redirect(url_for('index'))
        elif item.user_id != login_session['catalog_user_id']:
            return render_template("accessDenied.html")


@app.route("/deleteItem/<int:id>", methods=['GET'])
def delete_item(id):
    item = session.query(Item).filter_by(id=id).first()
    if item.user_id == login_session['catalog_user_id']:
        session.query(Item).filter_by(id=id).delete()
        session.commit()
        return redirect(url_for('index'))
    elif item.user_id != login_session['catalog_user_id']:
        return render_template("accessDenied.html")


if __name__ == '__main__':
    app.secret_key = '9KkwcTzRBEOjwhtWuqOByEDw'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
