## Homework1

### Matches for response

~~~~
tftable = [li['collection'] == 'response_functions' for li in data]
~~~~

### Find very first match

~~~~
match = next((l for l in data if l['collection'] == 'response_functions'), None)
~~~~

### Variables to access

#### Assuming JSON loaded to 'data' variable
	
##### Name of Gate

`data[index]['gate_name']`

##### On Threshold

`data[index]['variables'][0]['on_threshold']`

##### Off Threshold

`data[index]['variables'][0]['off_threshold']`

##### Y Max

`data[index]['parameters'][0]['value']`	

##### Y Min

`data[index]['parameters'][1]['value']`

##### K

`data[index]['parameters'][2]['value']`

##### n

`data[index]['parameters'][3]['value']`

### Commands After UCF JSON Modificiation

~~~~
python exclude_cytometry_data.py ./Eco1C1G1T1_MOD.UCF.json > ./Eco1C1G1T1_MOD_EX.UCF.json
~~~~

~~~~
cello post_ucf --name MOD_EX.UCF.json --filepath ./Eco1C1G1T1_MOD_EX.UCF.json
~~~~

~~~~	
cello submit --jobid ModifyTest --verilog ./test/AND.v --inputs ./test/Inputs.txt --outputs ./test/Outputs.txt --options="-UCF MOD_EX.UCF.json -plasmid false -eugene false"
~~~~
