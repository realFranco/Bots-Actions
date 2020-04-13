"""
Date: Feb 17th, 2020
Dev: franco@sustemaggency.com

bot_actions/views/sesion.py
"""

import time
import datetime
from functools import wraps
from time import gmtime, strftime

import jwt
from flask_cors import CORS, cross_origin
from flask import session, request, jsonify, make_response
from flask import Blueprint, render_template, redirect, url_for

from utils.auth import auth
from utils.utilities import utils
from utils.dynamo_client import dynamoInterface


sessions = Blueprint('sessions', __name__)

# Grant access on CORS
CORS(sessions)

# Init the class container for methods to use
utils = utils()

# Init the decorator for authentication
auth = auth() 

# Starting the DynamoDB interface
dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()


@sessions.route('/login', methods=['POST'])
def _in():
    intern_auth = {
        'pkurl': request.headers.get('Email'),
        'password': request.headers.get('Password')
    }

    args = {
        'gsidataportion': 'sa_user', # SystemUser
        'pkurl': intern_auth['pkurl'],
        'publicKey': intern_auth['password']
    }

    if not intern_auth or not intern_auth['pkurl'] or not intern_auth['password']:
        return jsonify({"message": "Could not verify the values sended."}), 401
    else:
        user = dynamo.query_items(arguments=args, debug_query=True)
        print('user', user)
        if user["Count"]:
            secret_key = auth.get_secret_key()

            # The user exist, got the unique item
            user = user["Items"][0]
            
            token = jwt.encode(
                    {
                        'publicKey': user['publicKey'], 
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=18000)
                    },
                    key=secret_key)
            session['token'] = token.decode('utf-8')
            # Creating a session: 201
            return redirect(url_for('data_template')), 201
        else:
            # User not exist
            return jsonify({"Message": "Not element(s) returned."}), 401


@sessions.route('/logout', methods=['GET'])
@auth.restricted(dynamo)
def log_out(actual_user):
    # session['token'] = ''
    session.pop('token')
    return redirect(url_for('data_template')), 200


@sessions.route('/registerUser', methods=['PUT'])
def register():
    item = {}
    password = request.headers.get('Password')

    item = {
        "gsidataportion": "sa_user", # SystemUser
        "pkurl": request.headers.get('Email'),
        "publicKey": password,
        "date_in": utils.date_formating()
    }

    return dynamo.insert(item=item)


@sessions.route('/restore', methods=['GET'])
@auth.restricted(dynamo)
def in_update_pass(actual_user):
    return render_template('sessions/restore.html'), 200


@sessions.route('/singIn')
def singin():
    # Do some stuff
    return render_template('sessions/registerUser.html'), 200


@sessions.route('/updatePass', methods=['PUT'])
@auth.restricted(dynamo)
def update_pass(actual_user):
    args = {
        "gsidataportion": "sa_user", # SystemUser
        'pkurl': request.args.get('email')
    }

    q = dynamo.query_items(arguments=args, debug_query=True)
    if q['Count'] > 0: 
        args['publicKey'] = request.args.get('password')
        key = {
            'pkurl': args.pop('pkurl')
        }

        dynamo.update(args, key, debug=True)
        return jsonify({"Message": "Updated."}), 200

    return jsonify({"Message": "Not updated."}), 401
