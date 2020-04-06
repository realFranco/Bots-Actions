"""
Date: Feb 17th, 2020

Dev: franco@systemagency.com

Class to avoid  the code line's replication.
"""

import re
from time import strftime, gmtime


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