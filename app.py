"""dev: franco@systemagency.com

For execute this python script:
$ python3 app.py

This script will active a web server to response the
request on 'botactions.systemagency.com'.

The main web page will contain a list of the web pages
that the Mother Agencie bot are reading for send
notificationes on the emails avaliable like destiny,
"""

import os

from flask import Flask
from flask import render_template

from createTable import dynamoInterface

app = Flask(__name__)

# Trigger the func. defined after this line
# Using a converter type and Rendering templates
@app.route('/')
def data_template():
    """ Importing the dynamo class interface for query
    just the agency names.
    """

    dynamo = dynamoInterface(table_name="ma_bot_actions"); dynamo.connect()

    arguments = {"gsi":"agency"}
    output, data_container = dynamo.query_items(arguments), {}

    for item in output["Items"]:
        if "url_name" in item.keys():
            if item["country"] in data_container.keys():
                data_container[ item["country"] ].append( 
                    ( item["url_name"], item["pkurl"] ) )
            else:
                data_container[ item["country"] ] = []

    return render_template('motheragencies.dev.html', data=data_container)

if __name__ == '__main__':
    app.run(debug=True)
