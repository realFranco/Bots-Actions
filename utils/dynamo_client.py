"""September 23th, 2019
dev: franco@systemagency.com
"""
import time
import json
import argparse
from time import strftime, gmtime

import boto3
from boto3.dynamodb.conditions import Key, Attr


class dynamoInterface(object):

    def __init__(self, table_name:str, gsi:str=''):
        self.table_name = table_name
        self.gsi = gsi


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


    # def insert(self, item):
    #     response = self.table.put_item(Item=item)
    #     return response["ResponseMetadata"]
    
    def insert(self, item, time=True):
        """ item: Dict. Elements to insert.

        Example:
        {
            'gsidataportion' : self.gsi,
            'pkid': 'key',
            'attr1': 'v_attr1',
            'attr_n': 'v_attr_n',
        }

        This method do not check if an element exists.

        @param time: bool, if True add a timestamp to the item,
        in other hand do not add those arguments.
        """
        
        response = None
        if item:
            if time:
                timestamp = {
                    # 'gsidataportion' : self.gsi,
                    'date': strftime("%d-%b-%Y", gmtime()),
                    'time': strftime('%H:%M:%S', gmtime())
                }
                item.update(timestamp)

            if not 'gsidataportion' in item.keys():
                _item = {'gsidataportion': self.gsi}
                _item.update(item)
                item = _item

            print('item')
            print(item)
            response = self.table.put_item(Item=item)
            response = response['ResponseMetadata']

        return response


    def query_items(self, arguments:dict, attr_exist=[], equal={}, debug_query=False):
        """ Method that quiery elements on the dynamo table.

        arguments:dict. Will contain the arguments for the insertion.

        attr_exist:list. Container of the arguments to check for existence
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
        n, m = len(values), len(attr_exist)

        # Conditition Expr.
        keys_ce = [":v"+k for k in list(arguments.keys())]

        # Expression Attrs. & Filter Expr.
        ea, fe = dict(zip(keys_ce, arguments.values())), ''

        # GSI
        key_ce = '%s=%s' %(keys[0], keys_ce[0]) # GSI
        
        for i in range(1, n):  # Is not need it the GSI again
            fe += 'contains(%s, %s)' % (keys[i], keys_ce[i])
            if i < n-1: fe += ' and '
        
        if m:
            if fe != '': fe += ' and ' # divide contains from attr_exist
            for i in range(m):
                fe += 'attribute_exists(%s)' % (attr_exist[i])
                if i < m-1: fe += ' and '
                    
       """
       if m:
           if fe != '': fe += ' and ' # divide contains from attr_exist
           last = attr_exist[-1]
           x = set( map( lambda el: 
               'attr %s and' %str(el) if el != last else 'attr %s' %str(el), 
                   attr_exist) )
           fe += ' '.join( list(x) ) 
       """
        
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

        keys_eav = [":v"+k for k in args_keys]
        keys_ean = ["#n_"+k for k in args_keys]

        values = list(args.values())

        eav = dict(zip(keys_eav, values))
        ean = dict(zip(keys_ean, args_keys))

        ue = 'SET '
        n = len(values)
        for i in range(n):
            # ue += "{} = {}".format(args_keys[i], keys_eav[i])
            ue += "{} = {}".format(keys_ean[i], keys_eav[i])
            if i < n-1: ue += ', '
        
        if debug:
            print("Key"); print(key); print('\n')
            print("Expression Attributes Names"); print(ean); print('\n')
            print("Expression Attributes Values"); print(eav); print('\n')
            print("Update Expression"); print(ue); print('\n')


        
        response = self.table.update_item(
            ExpressionAttributeNames=ean,
            ExpressionAttributeValues=eav,
            Key=key, 
            UpdateExpression=ue,
            ReturnValues='UPDATED_NEW'
        )
        
        return response


    def update_big(self, arguments:dict, debug_query=False):
        """
        This method can add, update new atributes and delete attributes,
        the example of the dictionary of arguments is the next.

        arguments = {
            'pkurl': '', or the Primary Key related
            'updates': {}, OPTIONAL
            'deletes': [] OPTIONAL
        }

        The 'deletes' list contain many strigns that represent the
        atributes of the row.

        The 'updates' dictionary contain a keys like new/existant arguments
        and values (of that keys) like the new values.

        The name of this method represent more the updates actiones than the
        delete actions.
        """

        out, eav, ean = {}, {}, {}
        if 'updates' in arguments.keys():
            action = arguments.pop('updates')
            ue_expr = [':v'+k for k in list(action.keys())]
            eav = dict(zip(ue_expr, action.values()))

            ue = ['%s=%s' %(key.replace(':v', ''), key) for key in list(eav.keys())]
            ue = 'SET ' + ', '.join(ue)

        if 'deletes' in arguments.keys():
            action = arguments.pop('deletes')
            if len(action):
                ue = 'REMOVE '
                for i in range(len(action)):
                    _attr_new_name = '#n_{}'.format(action[i]) # Changing the name
                    ean[ _attr_new_name ] = action[i]
                    ue += _attr_new_name
                    if i < len(action) - 1:  ue += ','

        key = arguments
        
        if debug_query:
            print("Expression Atribute Name: %s\n" % (ean))
            print("Expression Atribute: %s\n" % (eav))
            print("Key: %s\n" % (key))
            print("Update Expression: %s\n" % (ue))
        
        if ean and eav:
            out = self.table.update_item(
                Key=key,
                ExpressionAttributeNames=ean, #TODO: Check this
                ExpressionAttributeValues=eav,
                UpdateExpression=ue
            )
        
        elif ean and not eav:
            out = self.table.update_item(
                ExpressionAttributeNames=ean,
                Key=key,
                UpdateExpression=ue
            )

        elif eav and not ean:
            out = self.table.update_item(
                ExpressionAttributeValues=eav,
                Key=key,
                UpdateExpression=ue
            )

        return out


    def set_gsi(self, gsi):
        """ Global Secundary Index, setter method.
        """
        self.gsi = gsi

    
    def delete(self, key):
        """ For delete it is need just the primary key of the item.

        key:dict, 
        {
            "pk_name": "pk_value"
        }
        """
        response = self.table.delete_item(Key=key)
        return response["ResponseMetadata"]
