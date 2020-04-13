"""
Date: Mar 12th, 2020
Dev: franco@sustemaggency.com

bot_actions/views/ig_bio.py
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


ig_bio = Blueprint('ig_bio', __name__)

# Grant access on CORS
CORS(ig_bio)

# Init the class container for methods to use
utils = utils()

# Init the decorator for authentication
auth = auth() 

# Starting the DynamoDB interface
dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()


@ig_bio.route('/ig_biography', methods=['GET'])
@auth.restricted(dynamo)
def ig_bio_entry(arg):
    """ Endpoint that show the content avaliable for the ig Accounts
    under track for Biography changes.

    If some authentication problems are detected under the request,
    the error handler will render the Error template.
    """

    template = 'ig_bio/ig_bio.html'

    username = arg['pkurl'].split('@')[0]. \
                replace('sa_', '').capitalize()
    initial_greeting = '{}'.format(username.split('.')[0])

    data_container = {
        'initial_greeting': initial_greeting
    }

    return render_template(template, data=data_container), 200
