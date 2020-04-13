"""
Date: Feb 17th, 2020

Dev: franco@systemagency.com


"""

import json
from functools import wraps
from time import strftime, gmtime

import jwt
from flask import render_template, session

class auth(object):

    def __init__(self):
        """
        Attrs. description:

        
        @token, the token need it to access into the protected endpoints.
        """
        f = open('utils/vars.json', 'r'); self.secret_k = json.loads( f.read()  ) 
        f.close()


    def get_secret_key(self):
        return self.secret_k['SECRET_KEY']
    

    def restricted(self, dynamo, secret_key=""):
        """
        :dynamo, interface for dynamoDB.
        :secret_key, secret pass to encode/decode the token successfully
        """
        
        def auth_required(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                actual_user = None
                msg = {}
                
                # print(request.headers)
                if 'token' in list(session.keys()) and session['token']:
                    token = session['token']
                    try:
                        # unique secret key
                        secret_key = self.secret_k['SECRET_KEY']
                        data = jwt.decode(token, secret_key)
                        args = {
                            "gsidataportion": "sa_user", # SystemUser
                            "publicKey" : data["publicKey"]        
                        }
                        output = dynamo.query_items(arguments=args, debug_query=True)
                        actual_user = output["Items"][0]
                    except:
                        msg = {'code': '401', 'msg': 'The current token is invalid.'}
                        session['token'] = ''
                else:
                    msg = {'code': '401', 'msg': 'Could not verify the token sended.'}

                if msg: 
                    # return render_template('errors/error.html', data=msg), 401
                    return render_template('main/main_login.html', data=msg), 300
                else:
                    return func(actual_user)

            return decorated
        return auth_required
