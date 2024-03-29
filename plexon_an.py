# -*- coding: utf-8 -*-
"""
Created on Tue May  7 09:08:54 2019

@author: Vincenzo Marra
"""

from tkinter.filedialog import askopenfilename, askdirectory
from os import listdir
from tkinter import Tk
import matplotlib.pyplot as plt
import numpy as np
import neo
from math import floor
import scipy.signal as sig
from quantities import Hz, s
#from tracefunc import downsample,downsample_to,downsample_matrix_to,butter_lowpass,butter_lowpass_filter,bessel_lowpass,bessel_lowpass_filter
#To do:
#Funtion to remove artefacts
#Standardise filtering

def array2analog(array,channel):
    """Takes a numpy array and a neo analogsignal as channel and returns the array as a new 
    analog signal with the same units and sampling_rate of channel"""
    return neo.AnalogSignal(signal=np.array(array),units=channel.units, sampling_rate=channel.sampling_rate)

def running_mean(array,window):
    """Gets a moving average over a window of int points"""    
    avg_mask=np.ones(window) / window
    try:
        run_mean=np.convolve(array.as_array()[:,0], avg_mask, 'same')
    except:
        run_mean=np.convolve(array, avg_mask, 'same')
        pass
    return run_mean

def downsample(channel, factor):
    """ downsample of a certain factor a 100 samples array downsampled by 2
    will be a 50 samples array of the same time duration"""
    run_mean=running_mean(channel,factor)
    out=[]
    out_size=int(len(channel)/factor)    
    sample_size= float(len(channel))/out_size
    for i in range(out_size):
        out.append(channel[int(floor(i*sample_size))])
    try :
        out=neo.AnalogSignal(signal=np.array(out),units=channel.units, sampling_rate=channel.sampling_rate/factor)
    except: 
        pass
    return out

def downsample_to(channel, out_size):
    """keeps the shape of the signal but squeezes it into a fixed-size array"""
    return downsample(channel, int(floor(len(channel)/out_size)))

def downsample_matrix_to(MATRIX,out_size):
    """Takes a 2D matrix and cuts the second dimension to the required out_size"""
    OUT_MATRIX=np.empty((len(MATRIX),out_size))
    for c,v in enumerate(MATRIX):
        OUT_MATRIX[c]=downsample_to(v,out_size)
    return OUT_MATRIX

def butter_lowpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = sig.butter(order, normal_cutoff, btype='low', analog=True)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=4):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = sig.lfilter(b, a, data)
    return y

def bessel_lowpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = sig.bessel(order, normal_cutoff, btype='low', analog=True)
    return b, a

def bessel_lowpass_filter(data, cutoff, fs, order=4):
    b, a = bessel_lowpass(cutoff, fs, order=order)
    y = sig.lfilter(b, a, data)
    return y

def get_filenames():
    """returns a list of Plexon filenames in a folder"""
    Tk().withdraw() #this is to have a single window
    file_list=askopenfolder()#check correct code
    #cleanup flie_list for PLX only
    return file_list
    
def opener(file_name):
    """Returns a file a Neo Segment"""
    reader= neo.io.PlexonIO(filename=fname)
    rec = reader.read_segment()
    return rec
    
    
def get_threshold(channel,sdmult=4):
    """gets the threshold as 4*SD"""
    try:
        chan_ar=channel.as_array()
    except:
        chan_ar=channel
    #Is the mean == channel baseline?
    threshold= chan_ar.mean()+(sdmult*chan_ar.std())
    return threshold

def remove_large_spikes(channel, large_spk_mult=7):
    #find positive spikes
    large_pos_spikes_ind=np.where(channel.as_array()>get_threshold(channel,large_spk_mult))[0]
    #find negative spikes
    large_neg_spikes_ind=np.where(channel.as_array()<-get_threshold(channel,large_spk_mult))[0]
    #put them together 
    large_spikes_ind=list(large_pos_spikes_ind)+list(large_neg_spikes_ind)
    #remove them
    channel_no_large_spikes= channel.duplicate_with_new_data(
            np.delete(channel,large_spikes_ind))
    return channel_no_large_spikes

def find_peaks(channel,  event_points=10, positive_only=0,threshold=None):
    """find peaks above a threshold, if positive_only==1 it only thaks positive peaks.
    event_points gives number of points describing the event, 
    high numbers will reduce false positive but increase false negatives """ 
    if threshold==None: threshold=get_threshold(channel)
     
    #gets all the positive first
    supra_thres=np.where((channel.as_array())>get_threshold(channel),channel,0)
    polarity=np.greater
    #find all possible peaks above positive threshold
    event_inds=(sig.argrelextrema(supra_thres,polarity, axis=0, order=(event_points), mode='clip'))
    event_inds=event_inds[0]
     #if you also want the negatives
    if positive_only!=1:#need to change polarity
        print("Both positive and negative events will be analysed")
        neg_supra_thres=np.where((channel.as_array())<-get_threshold(channel),channel,0)
        neg_event_inds=(sig.argrelextrema(neg_supra_thres,np.less, axis=0, order=(event_points), mode='clip'))
        neg_event_inds=neg_event_inds[0]
        event_inds=list(event_inds)+list(neg_event_inds)
    else: print("Only positive events will be analysed")
    print("with a "+str(event_points)+" points time window")
    return list(event_inds)

def plot_spikes(channel,spk_ind=None):
    """plots spikes as red dots on the black trace"""
    if spk_ind==None: find_peaks(channel)
    ch_ar=channel.as_array()
    plt.figure;
    plt.plot(channel.times,channel,'k')
    plt.plot(channel.times[spk_ind],ch_ar[spk_ind],'ro')
 
def coastline(channel):
    """returns the coastline using the formula in Niknazar et al.2013  
    only the array part of the neo analog signals is used"""
    return np.sum(np.absolute(np.diff(channel.as_array()[:,0])))

def find_art(rec):
    """find large events that go above threshold on more than one channel at the time
    and returns their position. This only works with 16Channels array end files 
    exported with  16 channels""" 
    #pick channels to be used
    chs=[rec.analogsignals[0].as_array(),rec.analogsignals[15].as_array()]#for now limited to two channels
    art_threshold=0.8  #intended to be relative to the max value
    
    #take both positive and negative for both channels
    #for channel in chs:
    
    art_inds=list(set(supra_thres[0])&set(supra_thres[1]))
    
    
    return art_inds

def save_table(fname,rec,event_points=10, positive_only=0,threshold=None, remove_big=1):
    if fname[-4:].lower()=='.plx':
        with open(fname[:-4]+".txt",'w') as file:
            file.writelines("Channel \t Mean mV \t StDev \t N.Spikes \t Mean Spike Freq Hz \t CV(ISI) \t Total Coastline \t Duration (s) \t Norm Coastline \n")
            for  chan in rec.analogsignals:
                if remove_big==1:
                    SD_mult=7 #change the number here is you want to SD multiplier for rejections
                    print("REMOVES BIG SPIKES ABOVE "+ str(SD_mult)+"x SD")
                    old_chan_t_stop=chan.t_stop
                    chan=remove_large_spikes(chan, SD_mult)
                print("From channel "+str(chan.annotations['channel_id'])+ " it removed "+
                          str(old_chan_t_stop-chan.t_stop))
                spk_ind=find_peaks(chan,event_points, positive_only,threshold)
                isi=np.diff(chan.times[spk_ind].magnitude)
                file.writelines("Channel "+str(chan.annotations['channel_id'])+"\t"+
                                str(chan.mean().magnitude) + "\t" + str(chan.std().magnitude) + "\t"+
                                str(len(spk_ind))+ "\t" + str(len(spk_ind)/chan.t_stop.magnitude)+ "\t"+
                                str(isi.std()/isi.mean())+"\t"+str(coastline(chan)) +"\t"+ 
                                str(chan.t_stop.magnitude) +"\t"+str(coastline(chan)/chan.t_stop.magnitude)+"\n")
            
def batch_open(folder_name):
    all_files=listdir(folder_name)
    rec_list=[]
    for file in all_files:
        if file.find(".plx")!=-1:
            rec_list.append(file)
    print(rec_list)
    return rec_list

#def plot_all_channels(rec):
    #To DO!
    


if __name__=='__main__':
    """if not imported as a module it batch analyses a folder with .plx file the files must all have a single sampling frequency"""
    Tk().withdraw()
    folder=askdirectory()
    
    for fname in batch_open(folder):
        print(fname)
        reader= neo.io.PlexonIO(filename=folder+"/"+fname)
        rec = reader.read_segment()
        print(fname+' loading')
        save_table(folder+"/"+ fname,rec)

