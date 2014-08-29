import json
import os

data = {}
data['bytes'] = 419430400*25
data['frequency'] = 0.0
data['verbose'] = True
data['on'] = True
data['hash_function'] = 'xxhash'
data['check_arguments'] = True
data['check_mutation'] = True

with open(os.environ['JSONFILE'], 'w') as outfile:
    json.dump(data, outfile)
