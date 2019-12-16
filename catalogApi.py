import sqlite3
from flask import Flask, request, jsonify
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_marshmallow import Marshmallow
from dbsetup import User, Item, Category

# for creating foreign key relationship between the tables
from sqlalchemy.orm import relationship

# for configuration
from sqlalchemy import create_engine

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Initialize Marshmallow
ma = Marshmallow(app)


@app.route('/')
def home():
    return '''<h1>My API</h1>
<p>A prototype API </p>'''


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/AddUser.json')
def add_user():
    return '''Successfully Added'''


@app.route('/api/user/<id>', methods=['GET'])
def user_get(id):
    user = session.query(User).filter_by(id=id).one()
    return jsonify(User=[r.serialize for r in user])


@app.route('/api/catalog/', methods=['GET'])
def catalog_get():
    categories = session.query(Category).all()
    catalog = []
    for c in categories:
        items = session.query(Item).filter_by(category_id=c.id)
        c = c.serialize
        c['Item'] = [x.serialize for x in items]
        catalog.append(c)
    return jsonify(Catalog=catalog)


@app.route('/api/item/get/<id>', methods=['GET'])
def item_get(id):
    item = session.query(Item).filter_by(id=id).one()

    response = {}
    response['Item'] = item.serialize
    return jsonify(response)


@app.route('/api/item/create', methods=['POST'])
def item_create():
    new_item = Item(
        category_id=request.form.get('category_id'),
        name=request.form.get('name'),
        description=request.form.get('description'),
        user_id=request.form.get('user_id'))

    # session.rollback()
    session.add(new_item)
    session.commit()
    # return '''Successfully'''
    response = app.response_class(response='Successfully Created Item',
                                  status=200,
                                  mimetype='application/json')
    return response


if __name__ == '__main__':
    app.secret_key = '9KkwcTzRBEOjwhtWuqOByEDw'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
