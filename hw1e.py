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
def calculate_score_nor(ymin,ymax,k,n,in1,in2):
    score = ymin+float(ymax - ymin)/(1+((in1+in2)/float(k))**float(n))
    return score

def calculate_score_not(ymin,ymax,k,n,in1):
    score = ymin+float(ymax - ymin)/(1+((in1)/float(k))**float(n))
    return score

def stronger_promoter(x,ymin,ymax):
    yminnew = ymin*x
    ymaxnew = ymax*x
    return [yminnew, ymaxnew]

def weaker_promoter(x,ymin,ymax):
    yminnew = ymin/float(x)
    ymaxnew = ymax/float(x)
    return [yminnew, ymaxnew]

def stronger_rbs(k,x):
    return k/float(x)

def weaker_rbs(k,x):
    return k*x

def calculate_ckt_score(rf,data,componentdict,inputdict):
    for inputt in inputdict:
        for key in componentdict:
            if inputt == componentdict[key]['Inputs']:
                print('made it!')
                ymin = data[key]['parameters'][0]['value']
                ymax = data[key]['parameters'][1]['value']
                k = data[key]['parameters'][2]['value']
                n = data[key]['parameters'][3]['value']
                in1min = inputdict[inputt]['min']
                in1max = inputdict[inputt]['max']
                out1min = calculate_score_not(ymin,ymax,k,n,in1min)
                out1max = calculate_score_not(ymin,ymax,k,n,in1max)
                print(componentdict[key])
                print(out1max/out1min)
                print(out1min)
                print(out1max)
    x = itertools.permutations(inputdict.keys(),2)
    for comb in x:
        for key in componentdict:
            
            if comb == componentdict[key]['Inputs']:
                print('made it to NOR!')
                ymin = data[key]['parameters'][0]['value']
                ymax = data[key]['parameters'][1]['value']
                k = data[key]['parameters'][2]['value']
                n = data[key]['parameters'][3]['value']
                in1min = inputdict[comb[0]]['min']
                in1max = inputdict[comb[0]]['max']
                in2min = inputdict[comb[1]]['min']
                in2max = inputdict[comb[1]]['max']
                out1min = calculate_score_nor(ymin,ymax,k,n,in1min,in2min)
                out1max = calculate_score_nor(ymin,ymax,k,n,in1max,in2max)
                print(componentdict[key])
                print(out1max/out1min)
                print(out1min)
                print(out1max)
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
    options = '--options=-UCF '+ucf+' -plasmid false -eugene false'

    ''' submit job'''
    #subprocess.call([pyexec,callcello,'submit','--jobid','jobid','--verilog',verilog,'--inputs','./Inputs.txt','--outputs','./Outputs.txt',options])
    
    '''get logic circuit file'''
    with open('logic_circuit.txt', 'w') as f:
        subprocess.call([pyexec,callcello,'get_results','--jobid','pythonTest','--filename','pythonTest_A000_logic_circuit.txt'],stdout = f)

    '''read logic circuit file, get components used in componentdict dictionary'''
    with open('logic_circuit.txt','r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].count("Logic Circuit") == 1:
            start = i
        if lines[i].count("Circuit_score") == 1:
            end = i
    componentdict = {}
    inputdict={}
    '''Attempt to make a dict of circuit elements calling out the gate number, input and output'''
    innss=[]
    for line in lines[start:end]:
        if line.count('NOT') == 1:
            components = line.split()
            for ind in rf:
                for gate_name in data[ind]:
                    if data[ind][gate_name] == components[2]:
                        componentdict[ind] = {'Gate':components[2],'GateType':'NOT','GateNumber':components[3],'Inputs':components[4][1]}
        if line.count('NOR') == 1:
            components = line.split()
            for ind in rf:
                for gate_name in data[ind]:
                   if data[ind][gate_name] == components[2]:
                        componentdict[ind] = {'Gate':components[2],'GateType':'NOR','GateNumber':components[3],'Inputs':(components[4][1],components[4][3])}
        # INPUT READING WORKS FOR AND GATE
        if line.count('INPUT') == 1:
            a = line.split()[2]
            b = line.split()[3]
            for i in range(len(lines)):
                try:
                    if lines[i].split()[0] == a:
                        minn = 100
                        maxx= 0
                        for k in range(1,5):
                            if lines[i+k].split()[5]=='0':
                                if float(minn) > float(lines[i+k].split()[7]):
                                    minn = lines[i+k].split()[7]
                            if lines[i+k].split()[5]=='1':
                                if float(maxx) < float(lines[i+k].split()[7]):
                                    maxx = lines[i+k].split()[7]
                            inputdict[b] = {'inputName':a,'min':float(minn),'max':float(maxx)}
                except IndexError:
                    pass
    calculate_ckt_score(rf,data,componentdict,inputdict)
    # for k in range(1,2):
    #     print(lines[i+k])
    #     if lines[i+k][30] =='0':
    #         minn.append(float(lines[i+k][57:62]))
    #     if lines[i+k][30] =='1':
    #         maxx.append(float(lines[i+k][57:62]))
    # inputdict[b] = {'min':min(minn),'max':max(maxx)}

    print(componentdict)
    print(inputdict)


    num_components = len(componentdict.keys())
    '''print score'''
    score_original = lines[end].split()[2]
    print('The original score is: {}'.format(score_original))
    '''check if number of gates in ckt = number of gates we can edit, save ourselves combinations computation'''
    if len(componentdict)==select_num:
        UCF_list = []
        for stronger_p in range(1,2):
            data_result = no_combinations(rf,data,componentdict,stronger_p)
            UCF_name = 'Eco1C1G1T1'+'_SP_'+str(stronger_p)+'.UCF.json'
            UCF_name_path = './'+UCF_name
            with open(UCF_name, 'w') as f:
                f.write(json.dumps(data_result, indent=2))
            time.sleep(5)
            subprocess.call([pyexec,'./exclude_cytometry_data.py',UCF_name_path],stdout = open(UCF_name,'wb'))
            subprocess.call([pyexec, callcello, 'post_ucf', '--name', UCF_name, '--filepath', UCF_name_path])
            subprocess.call([pyexec, callcello, 'validate_ucf', '--name',UCF_name])
            UCF_list.append(UCF_name)


    '''Wait for server to be ready with posted UCF'''

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


