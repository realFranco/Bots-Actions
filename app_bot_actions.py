"""dev: franco@systemagency.com

For execute this python script:
$ sudo python3 app_bot_actions.py

This script will active a web server to response the
request on 'botactions.systemagency.com' or the public ip that
serve this web-app.

The main web page will contain a list of the web pages
that the Mother Agencie bot are reading for send
notificationes on the emails avaliable like destiny,

For running the server with a console a live
$ nohup sudo python3 app_bot_actions.py &
"""

import os
from functools import wraps
import datetime
from time import gmtime, strftime

from flask_cors import CORS, cross_origin
from flask import render_template, redirect, url_for
from flask import session, request, jsonify
from flask import Flask
import jwt

from dynamo_client import dynamoInterface

app = Flask(__name__)
app.config['SECRET_KEY'] \
    = "f95b6589a033d93ac16e665ac4b7c112e55db60920146ac8776e36e0527743c6"
# Grant access on CORS
CORS(app)

dynamo = dynamoInterface(table_name='ma_bot_actions'); dynamo.connect()


def date_formating():
    date = strftime("%Y-%m-%d", gmtime())
    t_date = date.split("-")
    month = {
        "1": "Jan",
        "2": "Feb",
        "3": "Mar",
        "4": "Apr",
        "5": "May",
        "6": "Jun",
        "7": "Jul",
        "8": "Aug",
        "9": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }

    return '%s-%s-%s' %(t_date[2], month[t_date[1]], t_date[0])


def auth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):

        actual_user = None
        if 'token' in list(session.keys()) and session['token']:
            token = session['token']
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                args = {
                    "gsidataportion": "SystemUser",
                    "publicKey" : data["publicKey"]        
                }
                output = dynamo.query_items(arguments=args, debug_query=True)
                actual_user = output["Items"][0]
            except:
                return jsonify({"Message": "The current token is invalid."}), 401
        else:
            return jsonify({"Message": "Not exist token in headers."}), 401

        return func(actual_user)

    return decorated


# Trigger the func. defined after this line
# Using a converter type and Rendering templates
@app.route('/', methods=['GET'])
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
            "gsidataportion": "SystemUser",
            "publicKey" : data["publicKey"]        
        }
        output = dynamo.query_items(arguments=args, debug_query=True)
        if output['Count'] > 0:
            # User exist
            template = 'motheragencies.dev.html'
            username = output['Items'][0]['pkurl'].split('@')[0].capitalize()
            initial_greeting = 'Welcome {}'.format(username)

    args = {'gsidataportion':'agency'}; attr_target =['url_name']
    output, data_container = dynamo.query_items(
        arguments=args, attr_exits=attr_target, debug_query=True), {'country': {}}

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


@app.route('/createItem', methods=['POST'])
@auth_required
def create(actual_user):
    item = {
        "url_name": request.args.get("url_name"),
        "pkurl": request.args.get("pkurl"),
        "country": request.args.get("country"),
        "date_in": date_formating(),
        "gsidataportion": request.args.get("gsidataportion"),
        'progress': request.args.get('progress')
    }
    for key in list(item.keys()):
        if item[key] == "": item.pop(key)

    dynamo.insert(item=item)
    # Element inserted: 201
    return jsonify({'Message': 'Element created'}), 201


@app.route('/queryItems', methods=['GET'])
def query():
    """The Read section for the CRUD.
    
    Will read the params from the url and send the items from that
    query like a response.
    """

    output, exist = None, []
    q_exist = request.args.get('exist')

    if q_exist: exist = [_ for _ in q_exist.split(',') if len(_) > 0]
        
    args = {
        'gsidataportion':'agency',
        'url_name': request.args.get('url_name'),
        'pkurl': request.args.get('pkurl'),
        'status': request.args.get('status')
    }    
    eq = {
        'country': request.args.get('country')
    }

    for _ in list(args.keys()):
        if args[_] == None or len(args[_]) == 0: args.pop(_)
    
    output = dynamo.query_items(
                arguments=args, 
                attr_exits=exist,
                equal=eq,
                debug_query=True
            )

    return jsonify(output["Items"]), 200


@app.route('/updateItem', methods=['PUT'])
@auth_required
def update(actual_user):

    key = {
        'pkurl': request.args.get('pkurl')
    }

    args = {
        'image': request.args.get('image'),
        'url_name': request.args.get('url_name'),
        "date_in": date_formating(),
        'status': request.args.get('status'),
        'country': request.args.get('country'),
        'progress': request.args.get('progress')
    }
    
    for _ in list(args.keys()):
        if args[_] == None or len(args[_]) == 0: args.pop(_)

    return dynamo.update(args, key, debug=True)


@app.route('/deleteItem', methods=['DELETE'])
@auth_required
def delete(actual_user):
    key = {
        "pkurl": request.args.get('pkurl')
    }
    
    return dynamo.delete(key=key) 


@app.route('/deleteCountry', methods=['DELETE'])
@auth_required
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
    

@app.route('/login', methods=['POST'])
def login():
    
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
        return jsonify({"Message": "Could not verify the values sended."}), 401
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
                    key=app.config['SECRET_KEY'])
            session['token'] = token.decode('utf-8')
            # Creating a session: 201
            return redirect(url_for('data_template')), 201
        else:
            # User not exist
            return jsonify({"Message": "Not element(s) returned."}), 401


@app.route('/singIn')
def sing_in():
    return render_template('register.dev.html'), 200


@app.route('/registerUser', methods=['PUT'])
def register():
    
    item = {}
    password = request.headers.get('Password')

    item = {
        "gsidataportion": "SystemUser",
        "pkurl": request.headers.get('Email'),
        "publicKey": password,
        "date_in": date_formating()
    }

    return dynamo.insert(item=item)


@app.route('/restore', methods=['GET'])
@auth_required
def in_update_pass(actual_user):
    return render_template('updatePass.dev.html'), 200


@app.route('/updatePass', methods=['PUT'])
@auth_required
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


@app.route('/logout', methods=['GET'])
@auth_required
def log_out(actual_user):
    session['token'] = ''
    print('log_out')
    return redirect(url_for('data_template')), 200

if __name__ == '__main__':
    """ Use Port 80 for http transfert protocol
    for runing wih that port, you need 'sudo' privilegies
    """

    print('Running Bot-Actions on Flask server.\n')
    app.run(host='0.0.0.0') 

