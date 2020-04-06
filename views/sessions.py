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

SECRET_KEY \
    = "f95b6589a033d93ac16e665ac4b7c112e55db60920146ac8776e36e0527743c6"

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
    auth = {
        'pkurl': request.headers.get('Email'),
        'password': request.headers.get('Password')
    }

    args = {
        'gsidataportion': 'SystemUser',
        'pkurl': auth['pkurl'],
        'publicKey': auth['password']
    }

    if not auth or not auth['pkurl'] or not auth['password']:
        return jsonify({"message": "Could not verify the values sended."}), 401
    else:
        user = dynamo.query_items(arguments=args, debug_query=True)
        if user["Count"]:
            # The user exist, got the unique item
            user = user["Items"][0]
            token = jwt.encode(
                    {
                        'publicKey': user['publicKey'], 
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=18000)
                    },
                    key=SECRET_KEY)
            session['token'] = token.decode('utf-8')
            # Creating a session: 201
            return redirect(url_for('data_template')), 201
        else:
            # User not exist
            return jsonify({"Message": "Not element(s) returned."}), 401


@sessions.route('/logout', methods=['GET'])
@auth.restricted(dynamo, SECRET_KEY)
def log_out(actual_user):
    # session['token'] = ''
    session.pop('token')
    return redirect(url_for('data_template')), 200


@sessions.route('/registerUser', methods=['PUT'])
def register():
    item = {}
    password = request.headers.get('Password')

    item = {
        "gsidataportion": "SystemUser",
        "pkurl": request.headers.get('Email'),
        "publicKey": password,
        "date_in": utils.date_formating()
    }

    return dynamo.insert(item=item)


@sessions.route('/restore', methods=['GET'])
@auth.restricted(dynamo, SECRET_KEY)
def in_update_pass(actual_user):
    return render_template('sessions/restore.html'), 200


@sessions.route('/singIn')
def singin():
    # Do some stuff
    return render_template('sessions/registerUser.html'), 200


@sessions.route('/updatePass', methods=['PUT'])
@auth.restricted(dynamo, SECRET_KEY)
def update_pass(actual_user):
    args = {
        "gsidataportion": "SystemUser",
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
