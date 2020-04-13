"""dev: franco@systemagency.com

For execute this python script:
$ python3 app.py

This script will active a web server to response the
requests from 'botactions.systemagency.com'.

The main web page will contain a list of the web pages
that the Mother Agencie bot are reading for send
notificationes on the emails avaliable like destiny,

> lsof -i :8000

> kill -9 xxx

"""

import os

import jwt
from flask import Flask
from flask_cors import CORS, cross_origin
from flask import render_template, redirect, url_for
from flask import session, request, jsonify, make_response
from jwt.exceptions import ExpiredSignature

from utils.auth import auth
from views.data import data
from views.errors import errors
from views.ig_bio import ig_bio
from views.sessions import sessions
from views.sa_signature import sa_signature
from views.ig_following import ig_following
from views.web_scouting import web_scouting
from views.country_scouts import country_scouts

from utils.dynamo_client import dynamoInterface

import decimal
import flask.json

app = Flask(__name__)

# Init the decorator for authentication
auth = auth()
app.config['SECRET_KEY'] = auth.get_secret_key()
    
# Grant access on CORS
CORS(app)

# Registration of the set of endpoints.
app.register_blueprint(data)
app.register_blueprint(ig_bio)
app.register_blueprint(sessions)
app.register_blueprint(ig_following)
app.register_blueprint(web_scouting)
app.register_blueprint(sa_signature)
app.register_blueprint(country_scouts)
# app.register_blueprint(errors)

# Starting the DynamoDB interface
dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()


@app.route('/', methods=['GET'])
def main_login():
    template = 'main/main_login.html'
    token = None
    data = {}
    if 'token' in list(session.keys()) and session['token']:
        token = session['token']
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            args = {
                "gsidataportion": "sa_user", # SystemUser
                "publicKey" : data["publicKey"]        
            }
            output = dynamo.query_items(arguments=args, debug_query=True)
            if output['Count'] > 0:
                # User exist
                template = 'main/main.html'
                username = output['Items'][0]['pkurl'].split('@')[0]. \
                    replace('sa_', '').capitalize()
                data['initial_greeting'] = 'Welcome {}'.format(username.split('.')[0])
        except ExpiredSignature as exp:
            print("Expired session: ")
            print(exp)

    return render_template(template, data=data), 200


@app.route('/main_no_auth', methods=['GET'])
def data_template():
    """ Importing the dynamo class interface for query
    just the agency names.
    """
    initial_greeting = 'Welcome'
    template = 'motheragencies.no.auth.dev.html'
    token = None
    if 'token' in list(session.keys()) and session['token']:
        token = session['token']
        data = jwt.decode(token, app.config['SECRET_KEY'])
        args = {
            "gsidataportion": "sa_user", # SystemUser
            "publicKey" : data["publicKey"]        
        }
        output = dynamo.query_items(arguments=args, debug_query=True)
        if output['Count'] > 0:
            # User exist
            template = 'motheragencies.dev.html'
            username = output['Items'][0]['pkurl'].split('@')[0].capitalize()
            initial_greeting = 'Welcome {}'.format(username.split('.')[0])

    args = {'gsidataportion':'agency'}
    attr_target = ['url_name']
    data_container = {'country': {}}

    output = dynamo.query_items(
        arguments=args, attr_exist=attr_target, debug_query=True)

    for item in output['Items']:
        if item['country'] not in data_container.keys():
            data_container['country'][ item["country"] ] = []
        data_container['country'][ item['country'] ]\
            .append((item['url_name'], item['pkurl']))

    data_container['initial_greeting'] = initial_greeting

    c_lower, data_sorted = {}, {}
    for key in list(data_container['country'].keys()):
        c_lower[key.lower()] = key

    for key in sorted(c_lower):
        data_sorted[ c_lower[key] ] = data_container['country'][c_lower[key]]

    data_container['country'] = data_sorted
    
    return render_template(template, data=data_container), 200


if __name__ == '__main__':
    app.run(port=8000)
    # app.run(host='0.0.0.0', port='80')
