#-*- coding: utf-8 -*-
"""
Collection of funtions and classes for analysis of electrophisiological traces

Vincenzo Marra: enzomarra@gmail.com
"""

#imports
from os import getcwd, listdir
import h5py
import numpy as np
import pylab as pl
import scipy.signal as sig
import scipy.sparse as sparse

"""def baseline_als(y, lam, p, niter=10):
  L = len(y)
  D = sparse.csc_matrix(np.diff(np.eye(L), 2))
  w = np.ones(L)
  for i in xrange(niter):
    W = sparse.spdiags(w, 0, L, L)
    Z = W + lam * D.dot(D.transpose())
    z = sparse.linalg.spsolve(Z, w*y)
    w = p * (y > z) + (1-p) * (y < z)
  return z"""


def find_nearest(array,value):
    """finds index of nearest value in a array"""
    ind = (np.abs(array-value)).argmin()
    return ind

def val_dist(a,b):
    """fids the distance between two values regardless of their sign"""
    return abs(a-b)



def find_incipit(trace): return np.argmax(np.abs(np.diff(trace)))+1

def abf2h5(abf_file):
    """Requires stfio module, part of StimFit software.
    It converts pClamp abf 2.0 files to the open standard h5.
    Not all types of abf files are supported. Episodic stimulation is supported."""
    try: #check if the module stfio is present
        import stfio 
        #expceptionally, the module is imported in the function as it is only used to deal with ABF files 
        #NB still pretty quick as the module is only imported once even using batch_abf2h5
    except ImportError: #exception
        print("Moudle stfio missing, install StimFit")
    rec = stfio.read(abf_file)#reads abf recording
    rec.write(abf_file[:-3]+'h5') #saves opened recording as h5
    
def batch_abf2h5(path=getcwd()):
    """It converts all pClamp abf 2.0 files in the specified folder to the open standard h5.
    If no argument is provided the current working directory is used."""
    filedir=listdir(path) #gets the name of all files in the folder
    n_converted=0 #counter for converted files
    for files in filedir: #goes through all the files
        if files.find(".abf")!=-1: #check if the file is an abf
            abf2h5(files) #converts abf files to h5
            n_converted+=1 #adds one to the counter
    print("{} files converted".format(n_converted)) #prints the number of converted files

def h52traces(h5_file):
    """Converts h5 file into a numpy array with the following structure:
    
    """
    
def find_events(trace, event=''):
    """finds events in trace and returns index of the event max amplitude (peak or trough)."""
    event_inds=[]
    
    event_types=['ap','epsc','epsp']
    peak=np.greater #set the search for positive events
    trough=np.less  #set the search for negative events
    try: #checks the event type is supported
        event_types.index(event.lower())
    except ValueError:
        print("This type of event is not supported. Events currently supported are:\n")
        print("event_types")
    reject=[]#testing only
    #assign polarity (direction of event) and number of points describing the event based on common sampling rates
    if event.lower()=='ap':
        event_points=4 #number of points describing the event, high numbers will reduce false positive but increase false negatives
        polarity= peak #search for a max or a min
        #find all possible peaks 
        event_inds=(sig.argrelextrema(trace,polarity, axis=0, order=(event_points), mode='clip'))
        event_inds=event_inds[0]
        #threshold filter
        event_inds=event_inds[trace[event_inds]>(np.mean(trace)+np.std(trace))]#event_inds[trace[event_inds]>(np.mean(trace)+np.std(trace))]
        
    elif event.lower()=='epsc':
        event_points=20 #number of points describing the event, high numbers will reduce false positive but increase false negatives
        polarity= trough #search for a max or a min
        #find all possible peaks 
        event_inds=(sig.argrelextrema(trace,polarity, axis=0, order=(event_points), mode='clip'))
        event_inds=event_inds[0]
        #threshold filter
        #event_inds=event_inds[trace[event_inds]<(np.mean(trace)-(1*np.std(trace)))]
        x=np.arange(1000)
        trise=20.0;tdecay=200.0
        y=-1.0*(1-np.exp(-x/trise))*np.exp(-x/tdecay)#the argmin is 48
        reject=[]
        for i in event_inds:
            if abs(trace[i]-trace[i-int(event_points*0.4)])<=abs(trace[i]-trace[i+int(event_points*0.4)]): #find_perc(trace,i,0.5, onset='onset')
                reject.append(i)
        return event_inds, reject
       
    elif event.lower()=='epsp':
        event_points=80 #number of points describing the event, high numbers will reduce false positive but increase false negatives
        polarity= peak #search for a max or a min
        #find all possible peaks 
        event_inds=(sig.argrelextrema(trace,polarity, axis=0, order=(event_points), mode='wrap'))
        event_inds=event_inds[0]
        #threshold filter
    return event_inds

def find_responses(resp_trace,stim_inds,event='epsc'):
    """finds events in a respose trace based on the index of a stimulus
    and returns index of the event max amplitude (peak or trough)."""
    event_inds=[]
    event_types=['ap','epsc','epsp']
    peak=np.greater #set the search for positive events
    trough=np.less  #set the search for negative events
    try: #checks the event type is supported
        event_types.index(event.lower())
    except ValueError:
        print("This type of event is not supported. Events currently supported are:\n")
        print("event_types")    
    if event.lower()=='ap':
        event_points=4 #number of points describing the event, high numbers will reduce false positive but increase false negatives
        polarity= peak #search for a max or a min
        #TO DO
        
    elif event.lower()=='epsc':
        event_points=20 #number of points describing the event, high numbers will reduce false positive but increase false negatives
        polarity= trough #search for a max or a min
        #find all possible peaks 
        evok=[]
        for i in range(len(stim_inds)):
            if i == (len(stim_inds)-1):
                evok.append(stim_inds[i]+np.argmax(val_dist(resp_trace[stim_inds[i]],resp_trace[stim_inds[i]:len(resp_trace)])))#do something different for the last point
            else:
                evok.append(stim_inds[i]+np.argmax(val_dist(resp_trace[stim_inds[i]],resp_trace[stim_inds[i]:stim_inds[i+1]])))
        
       
    elif event.lower()=='epsp':
        event_points=80 #number of points describing the event, high numbers will reduce false positive but increase false negatives
        polarity= peak #search for a max or a min
        #TO DO
    return evok

def meas_amp(trace,ind):
    """takes peak index and returns events aplitude, the analysis is performed 
    on the revered array to make sure the peak comes before the baseline"""
    t_to_bsl= 50 #number of points between-baseline and peak, too large may interfere with previous points, must be greater than 5
    rev_event=trace[ind:ind-t_to_bsl:-1] #select the period before the peak but reversed
    incipit= find_incipit(rev_event) #incipit point to approximate baseline
    bsl=np.mean(rev_event[incipit+(t_to_bsl/10):]) #mean baseline
    return val_dist(trace[ind],bsl)
        
def find_perc(trace,ind,percentage, t_to_bsl= 30,onset='onset'):
    """finds a certain percentage of change for a given event, part_value 
    should be between 0 and 1. For example find_part(trace,70,0.2) 
    will find the index of the 20% value of the event in position 70 of trace. 
    The analysis is performed on the reversed array to make sure the peak comes 
    before the baseline. t_to_bsl is the max number of points between-baseline and peak, 
    too large may interfere with previous points, must be greater than 9"""
    
    if onset=='onset':event=trace[ind:ind-t_to_bsl:-1] #select the period before the peak but reversed limiting the search
    if onset=='offset':event=trace[ind-t_to_bsl:ind] #select the period after the peak 
    incipit= find_incipit(event) #incipit point to approximate baseline
    bsl=np.mean(event[incipit+int(t_to_bsl/5.):]) #mean baseline
    peak=trace[ind] #value of the peak for readability 
    if bsl>peak: perc_value=bsl+(val_dist(bsl,peak)*percentage) #calculate the value of the trace at the desired percentage
    if bsl<peak: perc_value=bsl-(val_dist(bsl,peak)*percentage)
    
    
    #SOMETHING HERE NEEDS FIXING
    if onset=='onset':near_ind=ind-find_nearest(event[0:incipit],perc_value) #finds the nearest sampled index in the trace
    #to do check offset option
    if onset=='offset':near_ind=ind+find_nearest(event[0:incipit],perc_value)#finds the nearest sampled index in the trace

    
    if (val_dist(perc_value,peak)>val_dist(trace[near_ind],peak)) and trace[near_ind] !=trace[near_ind-1]: #if the closest sampled value is lesser than the wanted percentage (undershot)
        #finds how far from the sampled number the percentage value is and adjusts
        perc_t=near_ind- (val_dist(trace[near_ind] , perc_value)/val_dist(trace[near_ind], trace[near_ind-1]))
        infl=near_ind-incipit
        
    elif (val_dist(perc_value,peak)<val_dist(trace[near_ind],peak))and trace[near_ind] !=trace[near_ind+1]: #if the closest sampled value is greater than the wanted percentage (overshot)
        #finds how far from the sampled number the percentage value is and adjusts 
        perc_t=near_ind+ (val_dist(trace[near_ind] , perc_value)/val_dist(trace[near_ind], trace[near_ind+1]))
        infl=near_ind+incipit
        
        
    else: 
    #this is in case the perc number is exactly identical to a sampled number or in the rare occasion two adjectent sampled numbers identical
        perc_t=near_ind
    
    return [perc_t,infl,perc_value,near_ind]
    
