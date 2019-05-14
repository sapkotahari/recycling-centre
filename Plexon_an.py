# -*- coding: utf-8 -*-
"""
Created on Tue May  7 09:08:54 2019

@author: Vincenzo Marra
"""

from tkinter.filedialog import askopenfilename, askdirectory
from os import listdir
from tkinter import Tk
import pylab as pl
import neo
from math import floor
import scipy.signal as sig
from quantities import Hz, s
#To do:
#Funtion to remove artefacts
#Standardise filtering

def downsample(channel, factor,is_analog=1):
    """ downsample of a certain factor a 100 samples array undersampled by 2
    will be a 50 samples array
    """
    out=[]
    out_size=int(len(channel)/factor)    
    sample_size= float(len(channel))/out_size
    for i in range(out_size):
        out.append(channel[int(floor(i*sample_size))])
    if is_analog==1: out=neo.AnalogSignal(signal=pl.array(out),units=channel.units, sampling_rate=channel.sampling_rate/factor)
    return out

def downsample_to(channel, out_size):
    """keeps the shape of the signal but squeezes it into a fixed-size array"""
    return undersample(channel, int(floor(len(channel)/out_size)))


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
    
def running_mean(x, N):
    cumsum = pl.array(pl.cumsum(pl.insert(x, 0, 0)))
    return (cumsum[N:] - cumsum[:-N]) / float(N)
    
def get_threshold(channel,sdmult=4):
    """gets the threshold as 4*SD"""
    try:
        chan_ar=channel.as_array()
    except:
        chan_ar=channel
    #Is the mean == channel baseline?
    threshold= chan_ar.mean()+(sdmult*chan_ar.std())
    return threshold

def remove_large_spikes(channel):
    large_spikes_ind=a=pl.where(channel.as_array()>get_threshold(channel,8))[0]
    channel_no_large_spikes= channel.duplicate_with_new_data(
            pl.delete(channel,large_spikes_ind))
    return channel_no_large_spikes

def find_peaks(channel,  event_points=10, positive_only=0,threshold=None):
    """find peaks above a threshold, if positive_only==1 it only thaks positive peaks.
    event_points gives number of points describing the event, 
    high numbers will reduce false positive but increase false negatives """ 
    if threshold==None: threshold=get_threshold(channel)
     
    #gets all the positive first
    supra_thres=pl.where((channel.as_array())>get_threshold(channel),channel,0)
    polarity=pl.greater
    #find all possible peaks above positive threshold
    event_inds=(sig.argrelextrema(supra_thres,polarity, axis=0, order=(event_points), mode='clip'))
    event_inds=event_inds[0]
     #if you also want the negatives
    if positive_only!=1:#need to change polarity
        print("Both positive and negative events will be analysed")
        neg_supra_thres=pl.where((channel.as_array())<-get_threshold(channel),channel,0)
        neg_event_inds=(sig.argrelextrema(neg_supra_thres,pl.less, axis=0, order=(event_points), mode='clip'))
        neg_event_inds=neg_event_inds[0]
        event_inds=list(event_inds)+list(neg_event_inds)
    else: print("Only positive events will be analysed")
    print("with a "+str(event_points)+"points time window")
    return list(event_inds)

def plot_spikes(channel,spk_ind):
    """plots spikes as red dots on the black trace"""
    ch_ar=channel.as_array()
    pl.figure;
    pl.plot(channel.times,channel,'k')
    pl.plot(channel.times[spk_ind],ch_ar[spk_ind],'ro')
 
def coastline(channel):
    """returns the coastline using the formula in Niknazar et al.2013  
    concatenate needs to be used for neo analog signals as eacy point is a separate array"""
    return pl.sum(pl.absolute(pl.diff(pl.concatenate(channel.as_array()))))

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
            file.writelines("Channel \t Mean mV \t StDev \t N.Spikes \t Mean Spike Freq Hz \t CV(ISI) \t Coastline \n")
            for  chan in rec.analogsignals:
                if remove_big==1:
                    print("REMOVES BIG SPIKES ABOVE 8x SD")
                    old_chan_t_stop=chan.t_stop
                    chan=remove_large_spikes(chan)
                    print("From channel "+str(chan.annotations['channel_id'])+ " it removed "+
                          str(old_chan_t_stop-chan.t_stop))
                else:
                    spk_ind=find_peaks(chan,event_points, positive_only,threshold)
                    isi=pl.diff(chan.times[spk_ind].magnitude)
                    file.writelines("Channel "+str(chan.annotations['channel_id'])+"\t"+
                                    str(chan.mean().magnitude) + "\t" + str(chan.std().magnitude) + "\t"+
                                    str(len(spk_ind))+ "\t" + str(len(spk_ind)/chan.t_stop.magnitude)+ "\t"+
                                    str(isi.std()/isi.mean())+"\t"+str(coastline(chan)) +"\n")
                
def batch_open(folder_name):
    all_files=listdir(folder_name)
    rec_list=[]
    for file in all_files:
        if file.find(".plx")!=-1:
            rec_list.append(file)
    print(rec_list)
    return rec_list


if __name__=='__main__':
    """if not imported as a module it batch analyses a folder with .plx files
    the files must all have a single sampling frequency"""
    Tk().withdraw()
    folder=askdirectory()
    
    for fname in batch_open(folder):
        print(fname)
        reader= neo.io.PlexonIO(filename=folder+"/"+fname)
        rec = reader.read_segment()
        print(fname+' loading')
        save_table(folder+"/"+ fname,rec)

