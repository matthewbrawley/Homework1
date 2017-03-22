#!/usr/bin/env python
# AUTHOR Matthew Brawley mbrawley@bu.edu
# AUTHOR Michael Webster mzw@bu.edu

import sys
import itertools
import subprocess
import cello_client
import numpy as np
import json
from pprint import pprint
import io
import time

'''
Run Instructions: 
python2.7 hw1.py verilogfilename UCFfilename n
where n is the number of repressors for which protein or DNA engineering can be applied.
This should be less than or equal to the number of repressors in the UCF file.
Ensure cello_client.py is in repository as well as verilog and UCF file.
'''

def main():
    # vfile = sys.argv[1]
    # ucf = sys.argv[2]
    # select_num = sys.argv[3]

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

	# Change to how you want to call python, where cello_client.py is located, and which Verilog file you want to use
    pyexec = 'python2.7'
    callcello = './cello_client.py'
    verilog = './AND.v'
    
    ''' submit job'''
    subprocess.call([pyexec,callcello,'submit','--jobid','pythonTest','--verilog',verilog,'--inputs','./Inputs.txt','--outputs','./Outputs.txt'])
    
    '''get logic circuit file'''
    with open('logic_circuit.txt', 'w') as f:
        subprocess.call([pyexec,callcello,'get_results','--jobid','pythonTest','--filename','pythonTest_A000_logic_circuit.txt'],stdout = f)
    sys.stdout = sys.__stdout__
    
    '''read logic circuit file, get components used in componentdict dictionary'''
    with open('logic_circuit.txt','r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].count("Logic Circuit") == 1:
            start = i
        if lines[i].count("Circuit_score") == 1:
            end = i
    componentdict = {}
    for line in lines[start:end]:
        if line.count('NOT') == 1:
            components = line.split()
            for ind in rf:
                for gate_name in data[ind]:
                    if data[ind][gate_name] == components[2]:
                        componentdict[ind] = ('NOT',components[2])
        if line.count('NOR') == 1:
            components = line.split()
            for ind in rf:
                for gate_name in data[ind]:
                    if data[ind][gate_name] == components[2]:
                        componentdict[ind] = ('NOR',components[2])
    print(componentdict)
    '''print score'''
    score = lines[end].split()[2]
    print('The original score is: {}'.format(score))

    '''try stretching x = 1.5'''
    x=1.5
    '''itr is which item in component dict, here itr = 0,1,2, each component in the circuit is modified'''
    for itr in range(3):
        ymax = data[componentdict.keys()[itr]]['parameters'][0]['value']
        ymin = data[componentdict.keys()[itr]]['parameters'][1]['value']
        ymaxnew = ymax*x
        yminnew = ymin/x
        ymaxnew = round(ymaxnew,3)
        yminnew = round(yminnew,3)
        
        off_threshold = data[componentdict.keys()[itr]]['variables'][0]['on_threshold']
        on_threshold = data[componentdict.keys()[itr]]['variables'][0]['off_threshold']
        k = data[componentdict.keys()[itr]]['parameters'][2]['value']
        n = data[componentdict.keys()[itr]]['parameters'][3]['value']
        off_thresholdnew = k*((ymaxnew-ymaxnew/2)/(ymaxnew/2-yminnew))**(1./n)
        on_thresholdnew = k*((ymaxnew-yminnew*2)/(yminnew*2-yminnew))**(1./n)
        off_thresholdnew = round(off_thresholdnew,9)
        on_thresholdnew = round(on_thresholdnew, 9)

        # Print and store
        print('Current gate: {}'.format(componentdict.keys()[itr]))
        print('YMax is: {}'.format(ymaxnew))
        print('YMin is: {}'.format(yminnew))
        print('On_Threshold is: {}'.format(on_thresholdnew))
        print('Off_Threshold is: {}\n'.format(off_thresholdnew))

        data[componentdict.keys()[itr]]['parameters'][0]['value'] = ymaxnew
        data[componentdict.keys()[itr]]['parameters'][1]['value'] = yminnew
        data[componentdict.keys()[itr]]['variables'][0]['on_threshold'] = on_thresholdnew
        data[componentdict.keys()[itr]]['variables'][0]['off_threshold'] = off_thresholdnew
        
    '''re-write the JSON'''
    with open('Eco1C1G1T1_MOD.UCF.json', 'w') as f:
        f.write(json.dumps(data, indent=2))
    '''upload the json and run a new test with new json file'''
    subprocess.call([pyexec,'./exclude_cytometry_data.py','./Eco1C1G1T1_MOD.UCF.json'],stdout = open('Eco1C1G1T1_MOD_EX.UCF.json','wb'))
    subprocess.call([pyexec, callcello, 'post_ucf', '--name', 'MOD_EX.UCF.json', '--filepath', './Eco1C1G1T1_MOD_EX.UCF.json'])
    subprocess.call([pyexec, callcello, 'validate_ucf', '--name', 'MOD_EX.UCF.json'])
    
    #Wait for server to be ready with posted UCF
    time.sleep(100)
    subprocess.call([pyexec, callcello, 'submit', '--jobid', 'ModifyTest', '--verilog', verilog, '--inputs', './Inputs.txt', '--outputs', './Outputs.txt', '--options=-UCF MOD_EX.UCF.json -plasmid false -eugene false'])

    '''download resultant logic circuit file to get score'''
    with open('logic_circuit2.txt', 'w') as f:
        subprocess.call([pyexec, callcello, 'get_results', '--jobid','ModifyTest', '--filename', 'ModifyTest_A000_logic_circuit.txt'],stdout = f) 
    with open('logic_circuit2.txt','r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].count("Circuit_score") == 1:
            end = i
    score = lines[end].split()[2]
    print('The final score is: {}'.format(score))
    
if __name__ == "__main__":
    main()

def extract_dict(data):
    


