"""
Date: Mar 23th, 2020
Dev: franco@sustemaggency.com

bot_actions/views/sa_signature.py
"""

import json
import datetime
from time import gmtime, strftime

import jwt
from flask_cors import CORS, cross_origin
from flask import session, request, jsonify, make_response
from flask import Blueprint, render_template, redirect, url_for

from utils.auth import auth
from views.errors import errors
from utils.utilities import utils
from utils.dynamo_client import dynamoInterface


sa_signature = Blueprint('sa_signature', __name__)

# Grant access on CORS
CORS(sa_signature)

# Init the class container for methods to use
utils = utils()

# Init the decorator for authentication
auth = auth() 

# Starting the DynamoDB interface
dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()


@sa_signature.route('/sa_signature', methods=['GET'])
@auth.restricted(dynamo)
def sa_signature_entry(arg):
    """ Endpoint that show the content avaliable for the ig Accounts
    under track for Following member changes.

    If some authentication problems are detected under the request,
    the error handler will render the Error template.
    """

    template = 'sa_signature/sa_signature.html'
    
    username = arg['pkurl'].split('@')[0]. \
                replace('sa_', '').capitalize()
    initial_greeting = '{}'.format(username.split('.')[0])

    data_container = {
        'initial_greeting': initial_greeting
    }

    return render_template(template, data=data_container), 200
