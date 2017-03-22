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
import os

'''
Run Instructions: 
python2.7 hw1.py verilogfilename UCFfilename n
where n is the number of repressors for which protein or DNA engineering can be applied.
This should be less than or equal to the number of repressors in the UCF file.
Ensure cello_client.py is in repository as well as verilog and UCF file.
'''

def no_combinations(rf,data,componentdict,prom_inc):
    x = 1.5
    xn = 1.05
    for itr in componentdict.keys():
        ymax = data[itr]['parameters'][0]['value']
        ymin = data[itr]['parameters'][1]['value']
        off_threshold = data[itr]['variables'][0]['off_threshold']
        on_threshold = data[itr]['variables'][0]['on_threshold']
        k = data[itr]['parameters'][2]['value']
        n = data[itr]['parameters'][3]['value']
        ymaxnew = round(prom_inc*ymax*x,3)
        yminnew = round(prom_inc*ymin/x,3)
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
        #data[itr]['parameters'][2]['value'] = knew
    return data



def main():
    if not os.path.exists('./UCFs'):
        os.makedirs('./UCFs')
    if not os.path.exists('./logictxts'):
        os.makedirs('./logictxts')

    vfile = sys.argv[1]
    ucf = sys.argv[2]
    select_num = int(sys.argv[3])

    # Import standard UCF JSON file
    with open(ucf) as data_file:
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
    verilog = './'+vfile
    
    ''' submit job'''
    #subprocess.call([pyexec,callcello,'submit','--jobid','pythonTest','--verilog',verilog,'--inputs','./Inputs.txt','--outputs','./Outputs.txt'])
    
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
    score_original = lines[end].split()[2]
    print('The original score is: {}'.format(score_original))
    '''check if number of gates in ckt = number of gates we can edit, save ourselves combinations computation'''
    if len(componentdict)==select_num:
        UCF_list = []
        for stronger_p in range(1,5):
            data = no_combinations(rf,data,componentdict,stronger_p)
            UCF_name = 'Eco1C1G1T1'+'SP_'+str(stronger_p)+'_'+'.UCF.json'
            UCF_name_path = './UCFs/'+UCF_name
            with open(UCF_name_path, 'w') as f:
                f.write(json.dumps(data, indent=2))
            subprocess.call([pyexec,'./exclude_cytometry_data.py',UCF_name_path],stdout = open(UCF_name_path,'wb'))
            subprocess.call([pyexec, callcello, 'post_ucf', '--name', UCF_name, '--filepath', UCF_name_path])
            subprocess.call([pyexec, callcello, 'validate_ucf', '--name',UCF_name])
            UCF_list.append(UCF_name)

    # '''re-write the JSON'''
    # with open('Eco1C1G1T1_MOD.UCF.json', 'w') as f:
    #     f.write(json.dumps(data, indent=2))
    # '''upload the json and run a new test with new json file'''
    # subprocess.call([pyexec,'./exclude_cytometry_data.py','./Eco1C1G1T1_MOD.UCF.json'],stdout = open('Eco1C1G1T1_MOD_EX.UCF.json','wb'))
    # subprocess.call([pyexec, callcello, 'post_ucf', '--name', 'MOD_EX.UCF.json', '--filepath', './Eco1C1G1T1_MOD_EX.UCF.json'])
    # subprocess.call([pyexec, callcello, 'validate_ucf', '--name', 'MOD_EX.UCF.json'])
    
    #Wait for server to be ready with posted UCF
    print('waiting 2 minutes')
    time.sleep(120)
    for UCF_name in UCF_list:
        testname = 'test_'+UCF_name
        subprocess.call([pyexec, callcello, 'submit', '--jobid', testname, '--verilog', verilog, '--inputs', './Inputs.txt', '--outputs', './Outputs.txt', '--options=-UCF UCF_name -plasmid false -eugene false'])

        '''download resultant logic circuit file to get score'''
        logictextname = UCF_name+'.txt'
        logictextnamepath = './logictxts/'+UCF_name+'.txt'
        cello_file_name = testname+'_A000_logic_circuit.txt'
        with open(logictextnamepath, 'w') as f:
            subprocess.call([pyexec, callcello, 'get_results', '--jobid',testname, '--filename', cello_file_name],stdout = f) 
        with open(logictextnamepath,'r') as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].count("Circuit_score") == 1:
                end = i
        score = lines[end].split()[2]
        print('The final score is: {}'.format(score))

        
if __name__ == "__main__":
    main()


