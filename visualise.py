# -*- coding: utf-8 -*-
"""
Created on Wed May 15 17:15:14 2019

@author: localadmin1
"""
from tkinter.filedialog import askopenfilename, askdirectory
from os import listdir
from tkinter import Tk
import pylab as pl
import neo
from math import floor
import scipy.signal as sig
from quantities import Hz, s
from plexon_an import *

Tk().withdraw()
    
fname=askopenfilename()
reader= neo.io.PlexonIO(filename=fname)
rec = reader.read_segment()
canale=1 #change number to change channel
channel=rec.analogsignals[canale-1]
channel=remove_large_spikes(channel, 7) #change number to change visualised
plot_spikes(channel,find_peaks(channel))
