import json
import sys

filepath = sys.argv[1]
filetext = open(filepath, 'r').read()
filejson = json.loads(filetext)

ucf = []

for obj in filejson:
    if obj['collection'] != 'gate_cytometry':
        ucf.append(obj)

print json.dumps(ucf, indent=2)

