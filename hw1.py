#!/usr/bin/env python
# AUTHOR MatthewBrawley mbrawley@bu.edu
import sys
import itertools
import subprocess
import cello_client
'''
Run Instructions: 

python2.7 hw1.py verilogfilename UCFfilename n

where n is the number of repressors for which protein or DNA engineering can be applied.
This should be less than or equal to the number of repressors in the UCF file.

Ensure cello_client.py is in repository as well as verilog and UCF file.
'''
def read_verilog(vfile):
    f = open(vfile,'r')
    vcontent = f.read()
    f.close
    print vcontent
    ans = vcontent.find('begin')
    print ans
def main():

    vfile = sys.argv[1]
    ucf = sys.argv[2]
    n = sys.argv[3]
    read_verilog(vfile)
    pyexec = "python2.7"
    callcello = "./cello_client.py"
    subprocess.call([pyexec,callcello,"get_inputs"])



if __name__ == "__main__":
    main()
