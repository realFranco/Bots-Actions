"""September 23th, 2019
dev: franco@systemagency.com

using boto3 for creation and management examples
"""
import time
import json
import argparse

import boto3
from boto3.dynamodb.conditions import Key, Attr

from sqlclient import dbMaker

class dynamoInterface(object):

    def __init__(self, table_name):
        self.table_name = table_name

    def connect(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    def create(self):
        table = self.dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'pkurl',
                    'AttributeType': 'S'
                }
            ],
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': 'pkurl',
                    'KeyType': 'HASH'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)

        # Print out some data about the table
        print(table)

    def insert_many(self, partition_key:str):
        """ Inserting a few elements for test the batch syntax
        """
        with self.table.batch_writer() as batch:
            db = dbMaker(name="Scouting.db")
            db.connect(); db.makeCursor()
            elements = db.selectAll('SELECT * FROM AgencyBank;')
            db.close()
            # list of tuples (url, country, date)
            for content in elements:
                if content[1] == 'Ukraniain': country = 'Ukraine'
                else: country = content[1]
                    
                batch.put_item(
                    Item={
                        'gsidataportion' : partition_key,
                        'pkurl': content[0],
                        'country': country,
                        'date_in' : content[2]
                    }
                )

    def query_items(self, arguments:dict):
        """ Testing the query syntax

        arguments:dict. Will contain:
            keys, like the name of arguments
            and values, for that keys like values for the arguments.
        """

        response = self.table.query( 
                    IndexName='gsidataportion-index',
                    ExpressionAttributeValues={
                        ':vgsi': arguments['gsi']
                    },
                    KeyConditionExpression='gsidataportion = :vgsi'
                    # ProjectionExpression="#url, url_name, country"
        )  
        
        arguments["Items"] = response["Items"]
        arguments["Count"] = response["Count"]

        return arguments

    def update(self, container:dict):
        print(container)
        response = self.table.update_item(
            ExpressionAttributeValues={
                ':vurl_name': container['url_name']
            },
            Key={
                'pkurl': container['url']
            }, 
            UpdateExpression='SET url_name = :vurl_name',
            ReturnValues='UPDATED_NEW'
        )
        print(response)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='Flag mode for executions.'
            )

    parser.add_argument('--section', dest='start_finish', 
                        help="""\
                            Define the life cicle of a DB.\
                            
                            If section is equal to 'Create', the cicle of the\
                            DB is starting, means create two tables.""", 
                        type=str,
                        default="")

    parser.add_argument('--url', dest='url', type=str, default='')
    parser.add_argument('--url_name', dest='url_name', type=str, default='')

    args = parser.parse_args()
    arguments = args.__dict__

    dynamo = dynamoInterface(table_name="ma_bot_actions")
    dynamo.connect()

    if arguments['start_finish'] == 'C':
        dynamo.create()
    elif arguments['start_finish'] == 'I': # insert
        dynamo.insert_many(partition_key='agency')
    elif arguments['start_finish'] == 'Q':
        arguments = {"gsi":"agency"}
        output, data_container = dynamo.query_items(arguments), {}
        for item in output["Items"]:
            if "url_name" in item.keys():
                if item["country"] in data_container.keys():
                    data_container[ item["country"] ].append( 
                        ( item["url_name"], item["pkurl"] ) )
                else:
                    data_container[ item["country"] ] = []
