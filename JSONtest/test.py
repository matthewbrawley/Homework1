import json
import io

# Import standard UCF JSON file
with open('Eco1C1G1T1.UCF.json') as data_file:
    data = json.load(data_file)

# Find the location of all response functions in the JSON file
tftable = [li['collection'] == 'response_functions' for li in data]

# Create table of all locations of response functions

rf = []
for i in range(len(tftable)):
    if tftable[i]:
        rf.append(i)

print(rf)

for i in range(len(rf)):
    print(data[rf[i]])

with open('Eco1C1G1T1_MOD.UCF.json', 'w') as f:
    f.write(json.dumps(data, indent=2))
