# -*- coding: utf-8 -*-
"""
Created on Wed May 15 17:15:14 2019

@author: localadmin1
"""
from tkinter.filedialog import askopenfilename, askdirectory
from os import listdir
from tkinter import Tk
import neo
from math import floor
import scipy.signal as sig
from quantities import Hz, s
import numpy as np
import matplotlib.pyplot as plt
from plexon_an import *
from sklearn.preprocessing import normalize
Tk().withdraw()
    
fname=askopenfilename()
reader= neo.io.PlexonIO(filename=fname)
rec = reader.read_segment()

selcan=input("What channel? (type number or ALL and press enter)")

showspikes=0

if selcan.upper()!="ALL":
    channel=rec.analogsignals[int(selcan)-1]
    channel=remove_large_spikes(channel, 7) #change number to change visualised
    if showspikes==1: plot_spikes(channel,find_peaks(channel))
    else: plt.plot(channel.times,channel, 'k')
else:
    maxlist=[]
    minlist=[]
    arrchan=[]
    t=[]
    for i in rec.analogsignals:
        i=remove_large_spikes(i, 7) #change number to change visualised
        arrchan.append(i.as_array())
        t.append(i.times)
        maxlist.append(max(i.as_array()))
        minlist.append(min(i.as_array()))

    fig, axs = plt.subplots(16, 1)
    for s,c in enumerate(arrchan):
        axs[s].plot(t[s],c, 'k')
        axs[s].set_ylim(min(minlist), max(maxlist))
        axs[s].set_xlabel('time')
        axs[s].set_ylabel('uV')

    plt.show()
    plt.savefig(fname[:-3]+'svg')

twodplots=0
if twodplots==1:
    #No artifact removal!
    RECM=np.empty([len(rec.analogsignals),len(rec.analogsignals[0])])
    for c,v in enumerate(rec.analogsignals):
        RECM[c]=v.as_array()[:,0]
    
    print("Fig1:voltages,Fig2:Attempt at CSD, \n Figs 3--6 correlation coefficient at differnt times")
    plt.matshow(downsample_matrix_to(RECM,300))
    plt.colorbar()
    CSD=np.diff(np.diff(RECM,axis=0),axis=0)
    plt.matshow(downsample_matrix_to(CSD,300))
    plt.colorbar()
    for k in [1000,100000,200000,29000]:
        plt.matshow(np.corrcoef(RECM[:,k:k+1000]))
        plt.colorbar()

