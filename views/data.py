"""
Date: Feb 17th, 2020
Dev: franco@sustemaggency.com

bot_actions/views/data.py
"""

import json
import datetime
import urllib.parse
from time import gmtime, strftime

from flask_cors import CORS, cross_origin
from flask import session, request, jsonify, make_response
from flask import Blueprint, render_template, redirect, url_for

from utils.auth import auth
from utils.utilities import utils
from utils.dynamo_client import dynamoInterface


data = Blueprint('data', __name__)

# Grant access on CORS
CORS(data)

# Init the class container for methods to use
utils = utils()

# Init the decorator for authentication
auth = auth() 

# Starting the DynamoDB interface
dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()

@data.route('/createItem', methods=['POST'])
@auth.restricted(dynamo)
def create(actual_user):
    
    
    _item, item = request.args.to_dict(), {}
    item['gsidataportion'] = _item.pop('gsidataportion')
    item.update(_item)
    
    if item['gsidataportion'] in ['ig_bio', 'ig_followings']:        
        _ig = utils.check_ig_format(ig=item['pkurl'])
        item['pkurl'] = 'https://www.instagram.com/{}/'.format(_ig)

    elif item['gsidataportion'] == 'sa_signature':
        

        item['phone'] = '+' + item['phone'][1:]

        if item['phone_two']:
            item['phone_two'] = '+' + item['phone_two'][1:]
        
        if (type(item['select_for_msg']) == str ):
            item['select_for_msg'] = item['select_for_msg'] == 'true' # bool

        # TODO: Create the signature
        s3_info = utils.signature_maker(data=item, output=True)
        item['s3_file'] = s3_info['s3_file']

        print("Create signature member")
        print(item); print('\n\n')

    for _ in list(item.keys()):
        if item['gsidataportion'] == 'sa_signature' and item[_] == "":
            item.pop(_)
        elif item['gsidataportion'] != 'sa_signature' and not item[_]:
            item.pop(_)

    dynamo.insert(item=item)

    # Element inserted: 201
    return jsonify({'Message': 'Element created'}), 201


@data.route('/queryItems', methods=['GET'])
@auth.restricted(dynamo)
def query(actual_user):
    """The Read section for the CRUD.
    
    Will read the params from the url and converted into a dictionary.

    The first element of the dictionary will be GSI, it is a requirement
    hold the GSI at the first position of the dictionary.
    
    :param actual_user dict, will contain the elements returned by
    the autentication 

    :output dict, hold the results of the query.
    """
    
    _args, args, output = {}, {}, None
    _args = request.args.to_dict()
    # print('\n\n'); print('_args', _args)
    args['gsidataportion'] = _args.pop('gsidataportion')
    args.update(_args)

    if len(args.keys()) > 1:
        for _ in list(args.keys()):
            if not args[_]: args.pop(_)

    output = dynamo.query_items(arguments=args, debug_query=False)

    return jsonify(output["Items"]), 200


@data.route('/updateItem', methods=['PUT'])
@auth.restricted(dynamo)
def update(actual_user):
    del_attrs = ""
    gsi = ""

    key = {
        'pkurl': request.args.get('pkurl')
    }

    args = {
        'date_in': utils.date_formating(),
        'progress': request.args.get('progress')
    }
    
    if request.args.get('gsidataportion') == 'agency':
        args.update({
            'country': request.args.get('country'),
            'url_name': request.args.get('url_name')
        })

    elif request.args.get('gsidataportion') == 'sa_signature':
        args = request.args.to_dict()

        gsi = args.pop('gsidataportion')
        args.pop('pkurl')

        if (type(args['select_for_msg']) == str ):
            args['select_for_msg'] = (args['select_for_msg'] == 'true') # bool

        try:
            # Deleting not important attrs.
            del_attrs = args.pop('delete_item').split(',')
            dynamo.update_big(
                {'pkurl': key['pkurl'], 'deletes': del_attrs}, debug_query=False)
        except KeyError:
            pass

        args['phone'] = '+' + args['phone'][1:]
        try:
            if args['phone_two']:
                args['phone_two'] = '+' + args['phone_two'][1:]
        except KeyError:
            pass
    
    for _ in list(args.keys()):
        if gsi == 'sa_signature' and args[_] == "":
            args.pop(_)
        elif gsi != 'sa_signature' and not args[_]:
            args.pop(_)

    return dynamo.update(args, key, debug=True)
    

@data.route('/deleteItem', methods=['DELETE'])
@auth.restricted(dynamo)
def delete(actual_user):
    key = {
        "pkurl": request.args.get('pkurl')
    }
    
    return dynamo.delete(key=key)
