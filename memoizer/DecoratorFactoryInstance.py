'''
@author: Alexander Moreno
@summary: settings for factory object
'''
import json
import os
from DecoratorFactory import DecoratorFactory


factory = DecoratorFactory(209715200, 0, False, True)
try:
    with open(os.environ['JSONFILE'], "rb") as infile:
        data = json.load(infile)
        factory = DecoratorFactory(data['bytes'], data['frequency'], data["verbose"], data["on"], data['hash_function'], data['check_arguments'])
except:
    pass
