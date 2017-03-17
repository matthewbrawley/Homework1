#!/usr/bin/env python
# AUTHOR MatthewBrawley mbrawley@bu.edu
import sys
import itertools
import subprocess
import cello_client
import numpy as np
import json
from pprint import pprint
import io
'''
Run Instructions: 

python2.7 hw1.py verilogfilename UCFfilename n

where n is the number of repressors for which protein or DNA engineering can be applied.
This should be less than or equal to the number of repressors in the UCF file.

Ensure cello_client.py is in repository as well as verilog and UCF file.
'''


def main():
    vfile = sys.argv[1]
    ucf = sys.argv[2]
    n = sys.argv[3]



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


    with open('Eco1C1G1T1_MOD.UCF.json', 'w') as f:
        f.write(json.dumps(data, indent=2))

    pyexec = "python2.7"
    callcello = "./cello_client.py"
    subprocess.call(['python2.7', 'cello_client.py', 'submit', '--jobid', 'pythonTest', '--verilog', 'AND.v', '--inputs', 'Inputs.txt', '--outputs', 'Outputs.txt'])
    with open('logic_circuit.txt', 'w') as f:
        subprocess.call(['python2.7', 'cello_client.py', 'get_results', '--jobid','pythonTest', '--filename', 'pythonTest_A000_logic_circuit.txt'],stdout = f) 
    sys.stdout = sys.__stdout__
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
    score = lines[end].split()[2]
    print(score)


    x=1.5
    itr = 2
    ymax = data[componentdict.keys()[itr]]['parameters'][0]['value']
    ymin = data[componentdict.keys()[itr]]['parameters'][1]['value']
    ymaxnew = ymax*x
    yminnew = ymin/x
    off_threshold = data[componentdict.keys()[itr]]['variables'][0]['on_threshold']
    on_threshold = data[componentdict.keys()[itr]]['variables'][0]['off_threshold']

    k = data[componentdict.keys()[itr]]['parameters'][2]['value']
    n = data[componentdict.keys()[itr]]['parameters'][3]['value']

    off_thresholdnew = k*((ymaxnew-ymaxnew/2)/(ymaxnew/2-yminnew))**(1./n)
    on_thresholdnew = k*((ymaxnew-yminnew*2)/(yminnew*2-yminnew))**(1./n)

    data[componentdict.keys()[itr]]['parameters'][0]['value'] = ymaxnew
    data[componentdict.keys()[itr]]['parameters'][1]['value'] = yminnew
    data[componentdict.keys()[itr]]['variables'][0]['on_threshold'] = on_thresholdnew
    data[componentdict.keys()[itr]]['variables'][0]['off_threshold'] = off_thresholdnew


    with open('Eco1C1G1T1_MOD.UCF.json', 'w') as f:
        f.write(json.dumps(data, indent=2))

    #subprocess.call(['python2.7','exclude_cytometry_data.py','./Eco1C1G1T1_MOD.UCF.json','>','./Eco1C1G1T1_MOD_EX.UCF.json'],stdout = open())
    subprocess.call(['python2.7','exclude_cytometry_data.py','./Eco1C1G1T1_MOD.UCF.json'],stdout = open('Eco1C1G1T1_MOD_EX.UCF.json','wb'))
    subprocess.call(['python2.7', 'cello_client.py', 'post_ucf', '--name', 'MOD_EX.UCF.json', '--filepath', './Eco1C1G1T1_MOD_EX.UCF.json'])
    subprocess.call(['python2.7', 'cello_client.py', 'submit', '--jobid', 'ModifyTest', '--verilog', 'AND.v', '--inputs', 'Inputs.txt', '--outputs', 'Outputs.txt', '--options="-UCF MOD_EX.UCF.json -plasmid false -eugene false"'])


if __name__ == "__main__":
    main()


