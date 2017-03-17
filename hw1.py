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

    print(rf)



    with open('Eco1C1G1T1_MOD.UCF.json', 'w') as f:
        f.write(json.dumps(data, indent=2))

    pyexec = "python2.7"
    callcello = "./cello_client.py"
    subprocess.call(['python2.7', 'cello_client.py', 'submit', '--jobid', 'pythonTest4', '--verilog', 'AND.v', '--inputs', 'Inputs.txt', '--outputs', 'Outputs.txt'])
    with open('logic_circuit.txt', 'w') as f:
        subprocess.call(['python2.7', 'cello_client.py', 'get_results', '--jobid','pythonTest4', '--filename', 'pythonTest4_A000_logic_circuit.txt'],stdout = f) 
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
    print(componentdict)
if __name__ == "__main__":
    main()


