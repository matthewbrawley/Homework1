# Homework 1

## Setup

### REQUIRED

*This tool is built as a Python script that interacts with the Cello API to run tests of genetic circuits.*

#### Cello API:

```
cello_client.py
exclude_cytometry_data.py
setup.py
```
	
#### Cello API Extension Tool - Response Optimization:

```
ResOpt.py [NAME HERE]
```

#### Files Required:

```	
User Constraint File/Library: 	*.UCF.json
Verilog design file:		*.v
Inputs:				*.txt
Outputs:			*.txt
```

*The python tool requires that all needed files are in the directory from which you run the tool*

### Installation 

*This tool has been tested on both Linux and Unix environments*

#### For MacOS:

~~~~
	In terminal:
	Install brew on MacOS: 			/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	If brew installed before:		brew update
	Install Python through brew:		brew install python	
	Install pip through brew:		brew install pip
	Install cello trough pip:		pip install cello
	Other python packages needed:		sudo pip install requests
						sudo pip install urllib3
						sudo pip install Biopython
~~~~

#### For Linux:

```
The commands will be the same in the terminal except the commands will be “apt-get install” or “sudo apt-get install”

Must also install Tkinter: sudo apt-get install python-tk
```

### Using the Tool

#### Caveats:

Before continuing, make sure the “cello_client.py” file has the following line set at the end:

		~~~~~~~~~~~~~~~~~~~~~~~~~~
		if __name__ == '__main__':
			cli()
		~~~~~~~~~~~~~~~~~~~~~~~~~~
		
Without the above call to cli(), there will be problems running Cello in the Python script tool.

#### Setup in cello_client.py:

Replace as follows with your credentials:

		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#self.username = os.environ.get('CELLOUSER')
		#self.password = os.environ.get('CELLOPASS')

		self.username = "FILL ME"
		self.password = "FILL ME"
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		
If you want to use a local instance of Cello, replace as follows:

		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#self.url_root = "http://cellocad.org:8080"
		self.url_root = "http://127.0.0.1:8080"
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		
You can now easily switch between using Cello in the command line and also whether it runs online or locally.

#### Setup in ResOpt.py:

Update the settings below in the script for your system (how you call Python 2.7 - for example python2.7 or python) and the location of your cello_client.py.

	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    	'''Change to how you want to call python, where cello_client.py is located, and which Verilog file you want to use'''
    	pyexec = 'python2.7'
    	callcello = './cello_client.py'
    	verilog = './'+vfile
    	options = '--options=-UCF '+ucf+' -plasmid false -eugene false'
    	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#### Run the tool:

```
For MacOS:
	python ResOpt.py [Verilog] [UCF.json] [N]
For Linux:
	python gui.py
```

*N defines the maximum number of gates to alter*

## Command Help

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
