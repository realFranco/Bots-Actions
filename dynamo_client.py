"""September 23th, 2019
dev: franco@systemagency.com
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


    def insert(self, item):
        response = self.table.put_item(Item=item)
        return response["ResponseMetadata"]


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


    def query_items(self, arguments:dict, attr_exits=[], equal={}, debug_query=False):
        """ Method that quiery elements on the dynamo table.

        arguments:dict. Will contain the arguments for the insertion.

        attr_exits:list. Container of the arguments to check for existence
        ussefull for check updates on the following members and make the
        notifications.

            ['attr', 'attr2', ..., ]

        debug_query:bool Determine if the query can print some atributes.
        By defaul is False

        {
            'gsidataportion':'agency', * NOT OPTIONAL
            'key':'value', ..., 'keyn':'valuen'
        }

        equal: Dict, all the key located in this dictionary will be compared
        using the relacional operator '=' (equal). This is useful for
        when the atributes need to be the same at the stored inside of the item.

        return:list of items and the size.
        """
        # TODO: Add the 'has next_key?' section, in case when the query fetch much data.

        keys, values = list(arguments.keys()), list(arguments.values())
        n = len(values)

        keys_ce = [":v"+k for k in list(arguments.keys())]
        ea = dict(zip(keys_ce, arguments.values()))
        key_ce = '%s=%s' %(keys[0], keys_ce[0]) # GSI
        fe = '' # FilterExpression
        
        for i in range(1, n):  # Is not need it the GSI again
            fe += 'contains(%s, %s)' % (keys[i], keys_ce[i])
            if i < n-1: fe += ' and '
        
        m = len(attr_exits)
        if m:
            if fe != '': fe += ' and ' # divide contains from attr_exits
            for i in range(m):
                fe += 'attribute_exists(%s)' % (attr_exits[i])
                if i < m-1: fe += ' and '
        
        if equal:
            keys_eq,values_eq = list(equal.keys()), list(equal.values())
            keys_eq_modf = [':v'+k for k in list(keys_eq)]
            n = len(keys_eq_modf)
            eq_dict = dict(zip(keys_eq_modf, values_eq))
            ea.update(eq_dict)
            if fe != '': fe += ' and '
            for i in range(n):
                fe += '%s = %s' %( keys_eq[i], keys_eq_modf[i]) 
                if i < n-1: fe += ' and '

        if debug_query:
            print("Expression Atribute: %s\n" % (ea))
            print("Key Condition Expression: %s\n" % (key_ce))
            print("Filter Expression: %s\n" % (fe))

        if fe != '':
            response = self.table.query( 
                        IndexName='gsidataportion-index',
                        ExpressionAttributeValues=ea,
                        KeyConditionExpression=key_ce,
                        FilterExpression=fe
            )  
        else:
            response = self.table.query( 
                        IndexName='gsidataportion-index',
                        ExpressionAttributeValues=ea,
                        KeyConditionExpression=key_ce
            )
        return {
            "Items": response["Items"],
            "Count": response["Count"]
        }


    def update(self, args:dict, key:dict, debug=False):

        args_keys = list(args.keys())
        keys_ea = [":v"+k for k in args_keys]
        values = list(args.values())
        eav = dict(zip(keys_ea, values))

        # key_alter = [":v"+k for k in list(key.keys())]
        #key = dict(zip(key_alter, list(key.values())))

        ue = 'SET '
        n = len(values)
        for i in range(n):
            ue += "{} = {}".format(args_keys[i], keys_ea[i])
            if i < n-1: ue += ', '
        
        if debug:
            print("Expression Attributes"); print(eav); print('\n')
            print("Key"); print(key); print('\n')
            print("Update Expression"); print(ue); print('\n')


        
        response = self.table.update_item(
            ExpressionAttributeValues=eav,
            Key=key, 
            UpdateExpression=ue,
            ReturnValues='UPDATED_NEW'
        )
        
        return response
        

    
    def delete(self, key):
        """ For delete it is need just the primary key of the item.

        key:dict, 
        {
            "pk_name": "pk_value"
        }
        """
        response = self.table.delete_item(Key=key)
        return response["ResponseMetadata"]
