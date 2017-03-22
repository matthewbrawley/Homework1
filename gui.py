#!/usr/bin/env python
# AUTHOR MatthewBrawley mbrawley@bu.edu
import sys
import subprocess
import Tkinter as tk

pyexec = 'python2.7'
filename = 'hw1c.py'

class CelloGui(tk.Frame):
    ''' An example application for TkInter.  Instantiate
        and call the run method to run. '''
    def __init__(self, master):
        # Initialize window using the parent's constructor
        tk.Frame.__init__(self,
                          master,
                          width=400,
                          height=100)
        # Set the title
        self.master.title('Cello and HW1!')
 
        self.pack_propagate(0)
 
        self.pack()
 
        # The recipient text entry control and its StringVar
        self.UCF_Name_var = tk.StringVar()
        self.recipient = tk.Entry(self, textvariable=self.UCF_Name_var)
        self.UCF_Name_var.set('Enter UCF file name')
        self.Verilog_File_name_var = tk.StringVar()
        self.recipient2 = tk.Entry(self, textvariable=self.Verilog_File_name_var)
        self.Verilog_File_name_var.set('Enter Verilog file name')
        self.n_var = tk.StringVar()
        self.recipient3 = tk.Entry(self, textvariable=self.n_var)
        self.n_var.set('Enter n')
        
        # The go button
        self.go_button = tk.Button(self,
                                   text='Send to Homework 1 and Cello',
                                   command=self.send_args)
 
        # Put the controls on the form
        self.go_button.pack(fill=tk.X, side=tk.BOTTOM)
        self.recipient.pack(fill=tk.X, side=tk.TOP)
        self.recipient2.pack(fill=tk.X, side=tk.TOP)
        self.recipient3.pack(fill=tk.X, side=tk.TOP)

    def send_args(self):
        subprocess.call([pyexec,filename,self.Verilog_File_name_var.get(),self.UCF_Name_var.get(),self.n_var.get()])
    def run(self):
        self.mainloop()
 
app = CelloGui(tk.Tk())
app.run()