"""
Date: Feb 17th, 2020

Dev: franco@systemagency.com

Class to avoid  the code line's replication.
"""

import re
from time import strftime, gmtime

from utils.s3_client import S3Client

class utils(object):

    def __init__(self):
        pass

    def date_formating(self):
        date = strftime("%Y-%m-%d", gmtime())
        t_date = date.split("-")
        month = {
            "01": "Jan",
            "02": "Feb",
            "03": "Mar",
            "04": "Apr",
            "05": "May",
            "06": "Jun",
            "07": "Jul",
            "08": "Aug",
            "09": "Sep",
            "10": "Oct",
            "11": "Nov",
            "12": "Dec"
        }

        return '%s-%s-%s' %(t_date[2], month[t_date[1]], t_date[0]) 

    def check_ig_format(self, ig:str) -> str:
        if '.com' in ig:
            ig = ig.rsplit('.com', 2)[-1]
        if '?' in ig:
            ig = ig.split('?')[0]
        return re.sub(r'[@+/]', r'', ig)


    def signature_maker(self, data:dict, output:bool=False) -> dict:
        """
        Method that will convert the dict. with data into a .html file (the
            signature), and upload a file (the .html) into a public
            aws S3 Bucket.

        @data dictionary, data container who will have data to fill the 
            template.
        


        @param output boolean, if it is True, then the output
            will be a list of dicts., each element will look like this:

            {pkurl: name@systemagency.com, s3_file: https://...}


        After the signature was maked, generate the  .html and will be need 
        it to add a new attr. into the owner entity, 's3_file' with the 
        route of him file in aws S3 bucket.

        output: list of dict, each element will be a tuple k-v:
            - Key: pkurl or the email of the signature owner.
            - Value: route of the S3 bucket of the signature
        """
        out = {}
        try:
            with open('static/html_templates/SA_signature.html', 'r') as f:
                _html = f.read()
                f.close()
                    
            _t_keys = data.keys()
            
            _t_sing = _html.replace('title_worker_name', data['worker_name'])

            _t_sign = _t_sing.replace('{{image}}', data['image']).\
                replace('{{name}}', data['worker_name'].upper()).\
                replace('RCPT', data['pkurl'])

            if 'position' in _t_keys:
                data['position'] = data['position'].upper()
                _t_sign = _t_sign.replace('<!-- position -->', data['position'])
            
            if 'phone' in _t_keys:
                _t_sign = _t_sign.replace('<!-- phone -->', data['phone'])

            if 'phone_two' in _t_keys:
                _t_sign = _t_sign.replace('<!-- phone_two -->', data['phone_two'])
            
            if data['signature_name'] == 'Long Term':
                try:
                    with open('static/html_templates/SA_long_terms.html', 'r') as f:
                        long_terms = f.read()
                        f.close()
                    _t_sign = _t_sign.replace('<!-- long-terms -->', long_terms)

                except FileNotFoundError as err:
                    print(err)
                
            out_file = 'static/html_templates/{}.html'.format(
                data['pkurl'].split('@')[0])

            # Creating a .html file with the signature required.
            with open(out_file, 'w') as f:
                f.write(_t_sign)
                f.close()

            # s3.sendfile
            s3 = S3Client()
            s3.upload_file(
                file_name=out_file,
                bucket='systemagency.com'
            )

            out = {'s3_file': 
                    'https://s3.us-east-2.amazonaws.com/systemagency.com/' + out_file}
            
            # Outside of the class, please add into the item
            # a new attr. 's3_file' string
            if output:
                out.update({'pkurl': data['pkurl']})
            
            # return out

        except FileNotFoundError as err:
            print(err)

        return out
