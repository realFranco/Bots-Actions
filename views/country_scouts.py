"""
Date: Feb 17th, 2020
Dev: franco@sustemaggency.com

bot_actions/views/country_scouts.py
"""

import datetime
from time import gmtime, strftime

from flask_cors import CORS, cross_origin
from flask import session, request, jsonify, make_response
from flask import Blueprint, render_template, redirect, url_for

from utils.auth import auth
from utils.utilities import utils
from utils.dynamo_client import dynamoInterface


SECRET_KEY \
    = "f95b6589a033d93ac16e665ac4b7c112e55db60920146ac8776e36e0527743c6"

country_scouts = Blueprint('country_scouts', __name__)

# Grant access on CORS
CORS(country_scouts)

# Init the class container for methods to use
utils = utils()

# Init the decorator for authentication
auth = auth() 

# Starting the DynamoDB interface
dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()

@country_scouts.route('/deleteCountry', methods=['DELETE'])
@auth.restricted(dynamo, SECRET_KEY)
def delete_country(actual_user):
    status_code = 200
    args ={
        "gsidataportion": "agency",
        "country": request.args.get('country')
    }
    eq = {
        'country': request.args.get('country')
    }
    q = dynamo.query_items(arguments=args, equal=eq, debug_query=True)
    if q['Count'] > 0:
        for item in q['Items']:
            dynamo.delete(key={
                'pkurl': item['pkurl']
            })
    else:
        # No content: 204
        status_code = 204
    return jsonify({'Action': 'Delete'}), status_code
    