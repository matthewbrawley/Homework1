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

def Engineer_Ckt(rf,data,componentdict):
    x = 1.5
    xn = 1.05
    for itr in componentdict.keys():
        ymax = data[itr]['parameters'][0]['value']
        ymin = data[itr]['parameters'][1]['value']
        ymaxnew = round(ymax*x,3)
        yminnew = round(ymin/x,3)
        off_threshold = data[itr]['variables'][0]['off_threshold']
        on_threshold = data[itr]['variables'][0]['on_threshold']
        k = data[itr]['parameters'][2]['value']
        n = data[itr]['parameters'][3]['value']
        nnew = n*xn
        off_thresholdnew = k*((ymaxnew-ymaxnew/2)/(ymaxnew/2-yminnew))**(1./nnew)
        on_thresholdnew = k*((ymaxnew-yminnew*2)/(yminnew*2-yminnew))**(1./nnew)
        off_thresholdnew = round(off_thresholdnew,9)
        on_thresholdnew = round(on_thresholdnew, 9)
        data[itr]['parameters'][0]['value'] = ymaxnew
        data[itr]['parameters'][1]['value'] = yminnew
        data[itr]['variables'][0]['on_threshold'] = on_thresholdnew
        data[itr]['variables'][0]['off_threshold'] = off_thresholdnew
        data[itr]['parameters'][3]['value'] = nnew
    return data


def find_last_gates(lines, num_gates, select_num, rf, data):
    gates_to_edit = {}
    for line in lines:
        if line.count('NO') ==1:
            components = line.split()
            for ind in rf:
                for gate_name in data[ind]:
                    if data[ind][gate_name] == components[2]:
                        gates_to_edit[ind] = ('NOT/NOR',components[2])
    return gates_to_edit


def find_last_gate_lines(lines, num_gates, select_num, rf, data):
    k = num_gates
    for i in range(len(lines)):
        if lines[i].count('NO') == 1:
            k = k-1
            if k == select_num:
                gates_to_edit = find_last_gates(lines[i+1:],num_gates,select_num, rf, data)
                return gates_to_edit
            else:
                pass


def main():
    vfile = sys.argv[1]
    ucf = sys.argv[2]
    select_num = int(sys.argv[3])

    '''Import standard UCF JSON file'''
    with open(ucf) as data_file:
        data = json.load(data_file)

    '''Find the location of all response functions in the JSON file'''
    tftable = [li['collection'] == 'response_functions' for li in data]

    '''Create table of all locations of response functions'''
    rf = []
    for i in range(len(tftable)):
        if tftable[i]:
            rf.append(i)

    '''Change to how you want to call python, where cello_client.py is located, and which Verilog file you want to use'''
    pyexec = 'python2.7'
    callcello = './cello_client.py'
    verilog = './'+vfile
    
    ''' submit job'''

    subprocess.call([pyexec,callcello,'submit','--jobid','job_id','--verilog',verilog,'--inputs','./Inputs.txt','--outputs','./Outputs.txt'])
    
    '''get logic circuit file'''

    with open('logic_circuit.txt', 'w') as f:
        subprocess.call([pyexec,callcello,'get_results','--jobid','job_id','--filename','job_id_A000_logic_circuit.txt'],stdout = f)
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
        if line.count('NOT') ==1:
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
    num_gates = len(componentdict)

    '''print score'''

    score_original = lines[end].split()[2]

    print('The original score is: {}'.format(score_original))

    '''check if number of gates in ckt = number of gates we can edit, save ourselves combinations computation'''

    if num_gates == select_num:
        data = Engineer_Ckt(rf,data,componentdict)
    if num_gates > select_num:
        gates_to_edit = find_last_gate_lines(lines[start:end], num_gates, select_num, rf, data)
        data = Engineer_Ckt(rf,data,gates_to_edit)
    if num_gates < select_num:
        print('n must be equal to or less than the number of gates in the circuit!')
        exit(1)

    '''re-write the JSON'''

    with open('Eco1C1G1T1_MOD.UCF.json', 'w') as f:
        f.write(json.dumps(data, indent=2))

    '''upload the json and run a new test with new json file'''

    subprocess.call([pyexec,'./exclude_cytometry_data.py','./Eco1C1G1T1_MOD.UCF.json'],stdout = open('Eco1C1G1T1_MOD_EX.UCF.json','wb'))
    subprocess.call([pyexec, callcello, 'post_ucf', '--name', 'MOD_EX.UCF.json', '--filepath', './Eco1C1G1T1_MOD_EX.UCF.json'])
    subprocess.call([pyexec, callcello, 'validate_ucf', '--name', 'MOD_EX.UCF.json'])
    
    '''Wait for server to be ready with posted UCF'''

    time.sleep(120)
    subprocess.call([pyexec, callcello, 'submit', '--jobid', 'Modified_job', '--verilog', verilog, '--inputs', './Inputs.txt', '--outputs', './Outputs.txt', '--options=-UCF MOD_EX.UCF.json -plasmid false -eugene false'])

    '''download resultant logic circuit file to get score'''

    with open('logic_circuit2.txt', 'w') as f:
        subprocess.call([pyexec, callcello, 'get_results', '--jobid','Modified_job', '--filename', 'Modified_job_A000_logic_circuit.txt'],stdout = f) 
    with open('logic_circuit2.txt','r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].count("Circuit_score") == 1:
            end = i
    score = lines[end].split()[2]
    print('The final score is: {}'.format(score))

    percentgain = 100*np.log10(float(score))/np.log10(float(score_original))-100
    print('the percentage gain in the score is: {}%'.format(percentgain))


    if num_gates == select_num:
        print('Protein engineering methods of stretch and increase curve slope were applied to:')
        for key in componentdict:
            print(componentdict[key][1])
    if num_gates > select_num:
        print('Protein engineering methods of stretch and increase curve slope were applied to:')
        for key in gates_to_edit:
            print(gates_to_edit[key][1])

    print('See modified UCF file in current directory.')


if __name__ == "__main__":
    main()


