# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 09:56:37 2018

@author: Vincenzo Marra

Class to handle MEA recordings converted to excel CSV with Panasonic MED64


"""

from tkinter.filedialog import askopenfilename, Tk
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
import tracefunc as trf

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
            self.chan_list=self.channels[self.channels.find(',')+1:-1].split(",")#creating a list with channel names
            self.sampling_freq=float(self.rec_info[self.rec_info.index('Fs=')+3:self.rec_info.index('kHz')])*1000
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
                    chan_val= self.rec_data[channel]
            elif type(channel) is int:
                chan_id= channel
                chan_val= self.rec_data["CH"+str(chan_id)+"(mV)"]
        if type(sweep) == int:
            chan_val=chan_val.loc[sweep]
        return chan_val
    
    def chan2matrix(self, channel,sweep=None):
        if sweep != None: 
            mat=self.get_chan(channel,sweep)
            
        else:
            chandata=self.get_chan(channel)
            mat=np.zeros((int(chandata.size/self.sweep_n),self.sweep_n))
            
            for i,j in enumerate(chandata.index.drop_duplicates()):
                mat[:,i]=chandata.loc[j]
        return mat
    
    def get_time(self):
        return self.get_chan("T(ms)",1)
    
    def plot_chan(self, channel):
        
        plt.plot(self.get_time(1),self.chan2matrix(channel))
        plt.title("Channel " + str(channel))
        plt.xlabel("ms")
        plt.ylabel("mV")
    
       
    def notch_filter_chan(self,channel,sweep=None):
        filt_chan=np.zeros(np.shape(self.get_chan(channel)))
        filt_can=trf.notch_filter(self.get_chan(channel),49,51,20000)
        return filt_chan
        
    def notch_filter_mat(self, channel, sweep=None):
        if sweep!= None:
            filt_chan=self.notch_filter_chan(channel,sweep)
        else:
            chan_mat = self.chan2matrix(channel)
            filt_chan=np.zeros(np.shape(chan_mat))
            for i,j in enumerate(chan_mat):
                filt_chan[i]=trf.notch_filter(j,49,51,self.sampling_freq)
        return filt_chan



def fepsp_slope(trace):
    """finds the 20-80% slope using a diff approach for a fEPSP"""
    bsl=np.mean(trace[0:3])
    peak=np.mean(trace[np.argmin(trace)-1:np.argmin(trace)+1]) 
    amp=trf.val_dist(bsl,peak)
    
    twenty=trf.find_nearest(trace[0:np.argmin(trace)+1],bsl-amp*0.2)
    eighty=trf.find_nearest(trace[0:np.argmin(trace)+1],bsl-amp*0.8)
    slope=np.mean(np.diff(trace[twenty:eighty]))
    return slope,trace[twenty],trace[eighty],trace[np.argmin(trace)]

def do_analysis(rec,first_sweep=1, save =0):
    """runs analysis of two slope resposenses"""
    chan=int(input("What channel do you want to analyse? "))
    #assuming less that 4 ms slope at 20KHz sampling rate
    epsp1start=int(20*float(input("Start time slope 1: "))) #index on trace
    epsp2start=int(20*float(input("Start time slope 2: ")))
    epsp1slopes=[]
    epsp2slopes=[]
    for i in range(first_sweep,rec.sweep_n+1):
        epsp1slopes.append(fepsp_slope(rec.get_chan(chan,i)[epsp1start:epsp1start+80].values)[0])
        epsp2slopes.append(fepsp_slope(rec.get_chan(chan,i)[epsp2start:epsp2start+80].values)[0])
    print(epsp1slopes)
    print(epsp2slopes)
    
if __name__ == "__main__":
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearin
    file_name = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    rec=MEA_rec(file_name)

#to plt a channel type: rec.plot_chan(CHAN_NUMBER)
#to run the analysis type: do_analisys(rec)


        
