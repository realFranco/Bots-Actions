"""
Date: Mar 11th, 2020
Dev: franco@sustemaggency.com

bot_actions/views/web_scouting.py
"""

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


SECRET_KEY \
    = "f95b6589a033d93ac16e665ac4b7c112e55db60920146ac8776e36e0527743c6"

web_scouting = Blueprint('web_scouting', __name__)

# Grant access on CORS
CORS(web_scouting)

# Init the class container for methods to use
utils = utils()

# Init the decorator for authentication
auth = auth() 

# Starting the DynamoDB interface
dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()


@web_scouting.route('/web_scouting', methods=['GET'])
@auth.restricted(dynamo, SECRET_KEY)
def web_scouting_entry(arg):
    """ 
    This endpoint will render the endpoint for manage the Web Scouting
    sites.

    param arg dictionary, argument sended from the decorator, will contain
        irrelevant data from this endpoint.
            {publickey, pkurl, data_in, gsidataportion}

        It is catched in any case.
    """

    template, token = '', None
    initial_greeting = 'Welcome'
    
    if 'token' in list(session.keys()) and session['token']:
        token = session['token']
        data = jwt.decode(token, SECRET_KEY) # app.config['SECRET_KEY']
        args = {
            "gsidataportion": "SystemUser",
            "publicKey" : data["publicKey"]        
        }
        output = dynamo.query_items(arguments=args, debug_query=True)

        if output['Count'] > 0:
            # User exist
            template = 'web_scouting/web_scouting.html'
            username = output['Items'][0]['pkurl'].split('@')[0].capitalize()
            initial_greeting = 'Welcome {}'.format(username.split('.')[0])

            args = {'gsidataportion':'agency'}
            attr_target = ['url_name']
            data_container = {
                'country': {},
                'initial_greeting': initial_greeting,
                'gsidataportion': 'agency' # usefull to the query selector
            }

            output = dynamo.query_items(
                arguments=args, attr_exist=attr_target, debug_query=True)

            for item in output['Items']:
                if item['country'] not in data_container.keys():
                    data_container['country'][ item["country"] ] = []
                data_container['country'][ item['country'] ]\
                    .append((item['url_name'], item['pkurl']))

            c_lower, data_sorted = {}, {}
            for key in list(data_container['country'].keys()):
                c_lower[key.lower()] = key

            for key in sorted(c_lower):
                data_sorted[ c_lower[key] ] = data_container['country'][c_lower[key]]

            data_container['country'] = data_sorted

    return render_template(template, data=data_container), 200


@web_scouting.route('/dev_web_scouting')
def web_scouting_entry_dev():
    return jsonify({'Message': 'Dev Web Scouting Endpoint'}), 200
