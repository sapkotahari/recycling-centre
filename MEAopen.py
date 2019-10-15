# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 09:56:37 2018

@author: Vincenzo Marra

Class to handle MEA recordings converted to excel CSV with Panasonic MED64


"""

from tkinter.filedialog import askopenfilename, Tk
import pandas as pd
import re
import pylab as pl

class MEA_rec(object):
    def __init__(self, file_name):
        with open(file_name,'r') as rec_file:
            self.rec_info=rec_file.readline()
            self.channels=rec_file.readline()
            rec_file.seek(0)
            content=rec_file.readlines()
            self.sweep_rows= [x for x in range(len(content)) if "/" in content[x]]
            self.sweep_n=len(self.sweep_rows)-1                 
            print(self.sweep_rows)
            rec_file.seek(0)
            self.rec_data=pd.read_csv(rec_file, skiprows= self.sweep_rows[1:],header=1)
            print(self.rec_info)#do stuff
            print(self.channels[self.channels.find(',')+1:])
            if self.sweep_n>1:
                self.rec_data['Sweep']= sorted(list(range(1,self.sweep_n+1))*(self.sweep_rows[2]-self.sweep_rows[1]-1))
                self.rec_data.set_index('Sweep', inplace=True)
        
    def get_chan(self, channel=None,sweep=None):  #TO DO turn it into a *args so it can be used a as tuple
        """Help"""
        if channel==None: 
            chan_val=self.rec_data
        else:
            if type(channel) is str:
                if 'T' in channel.upper():
                    chan_val=self.rec_data["T(ms)"]
                else:
                    chan_id= int(re.search(r'\d+', channel).group())
            elif type(channel) is int:
                chan_id= channel
                chan_val= self.rec_data["CH"+str(chan_id)+"(mV)"]
        if type(sweep) == int:
            chan_val=chan_val.loc[sweep]
        return chan_val
    
    def get_time(self,sweep=None):
        return self.get_chan("T(ms)",sweep)
    
    def plot_chan(self, channel,sweep=None):
        
        pl.plot(self.get_time(sweep),self.get_chan(channel, sweep))
        pl.title("Channel " + str(channel)+" Sweep " + str(sweep))
        pl.xlabel("ms")
        pl.ylabel("mV")



if __name__ == "__main__":
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearin
    file_name = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    rec1=MEA_rec(file_name)