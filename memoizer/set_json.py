import json
import os

data = {}
data['bytes'] = 419430400
data['frequency'] = 0.0
data['verbose'] = False
data['on'] = True

with open(os.environ['JSONFILE'], 'w') as outfile:
    json.dump(data, outfile)