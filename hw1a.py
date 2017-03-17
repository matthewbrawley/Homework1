#!/usr/bin/env python
# AUTHOR MatthewBrawley mbrawley@bu.edu
import sys
import itertools
import subprocess
import cello_client
import numpy as np
import json
from pprint import pprint
'''
Run Instructions: 

python2.7 hw1.py verilogfilename UCFfilename n

where n is the number of repressors for which protein or DNA engineering can be applied.
This should be less than or equal to the number of repressors in the UCF file.

Ensure cello_client.py is in repository as well as verilog and UCF file.
'''
def read_verilog(vfile):
    f = open(vfile,'r')
    lines = f.readlines()
    f.close

    line1 = lines[0]
    numoutputs = line1.count('out')-1
    outinds = line1.find(out)
    for i in range(numoutputs-1):
        line1(outinds(i+1))
    numinputs = line1.count('in')-1
    ins = np.zeros(numinputs)
    for k in range(numinputs+1):
        ins[k] = 'in'+str(k+1)
    print(ins)
    for i in range(len(lines)):
        if lines[i].count('begin')==1:
            caseline = lines[i+1]
            if caseline.count('in') != numinputs:
                numinputs_case = caseline.count('in')
            else:
                numinputs_case = numinputs
            # for k in range(len(numinputs_case)+1)
            #     inp(k)=('in%d',k+1)
    '''for line in lines:
        line = line.strip()
        print line'''

def parseucf(ucf):
    x = json.load(ucf)

def main():
    vfile = sys.argv[1]
    ucf = sys.argv[2]
    n = sys.argv[3]
    #read_verilog(vfile)
    #parseucf(ucf)
    pyexec = "python2.7"
    callcello = "./cello_client.py"
    subprocess.call(['python2.7', 'cello_client.py', 'submit', '--jobid', 'pythonTest4', '--verilog', 'AND.v', '--inputs', 'Inputs.txt', '--outputs', 'Outputs.txt'])
    with open("test_out.txt", 'w') as f:
        sys.stdout = f
        subprocess.call(['python2.7', 'cello_client.py', 'get_results', '--jobid','pythonTest4', '--filename', 'pythonTest4_dnacompiler_output.txt']) 
    sys.stdout = sys.__stdout__
    print('testreturnedstdout')
    # with open('Eco1C1G1T1.UCF.json') as data_file:
    #     data = json.load(data_file)
    # pprint(data[23])
if __name__ == "__main__":
    main()


