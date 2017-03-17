import json
import io
from pprint import pprint

with open('main.json') as data_file:
    data = json.load(data_file)

rf = []

#Find the location of all response functions in the JSON file
tftable = [li['collection'] == 'response_functions' for li in data]

for i in range(len(tftable)):
    if tftable[i]:
        rf.append(i)

print(rf)

for i in range(len(rf)):
    print(data[rf[i]])

with open('data.json', 'w') as f:
    #str = json.dumps(data, indent=4)
    #f.write(to_unicode(str))
    f.write(json.dumps(data, indent=2))

#pprint(data)

