import json
import os

data = {}
data['bytes'] = 419430400*25
data['frequency'] = 0.0
data['verbose'] = False
data['on'] = True
data['hash_function'] = 'xxhash'
data['check_arguments'] = False
data['check_mutation'] = False

with open(os.environ['JSONFILE'], 'w') as outfile:
    json.dump(data, outfile)
