# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:07:18 2019

@author: localadmin1
"""

#Collection of useful functions to analyse traces
import numpy as np
import scipy.signal as sig

def find_nearest(array,value):
    """finds index of nearest value in a array"""
    ind = (np.abs(array-value)).argmin()
    return ind

def val_dist(a,b):
    """fids the distance between two values regardless of their sign"""
    return abs(a-b)


def find_incipit(trace): return np.argmax(np.abs(np.diff(trace)))+1

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



def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = sig.butter(order, [low, high], btype='band')
    return b, a


def notch_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sig.lfilter(b, a, data)
    return y

"""
# time:   Time between samples
# band:   The bandwidth around the centerline freqency that you wish to filter
# freq:   The centerline frequency to be filtered
# ripple: The maximum passband ripple that is allowed in db
# order:  The filter order.  For FIR notch filters this is best set to 2 or 3,
#         IIR filters are best suited for high values of order.  This algorithm
#         is hard coded to FIR filters
# filter_type: 'butter', 'bessel', 'cheby1', 'cheby2', 'ellip'
# data:         the data to be filtered
def notch_filter( data,time=0.00005, band=4, freq=50, ripple=1, order=4, filter_type='bessel'):
    
    fs   = 1/time
    nyq  = fs/2.0
    low  = freq - band/2.0
    high = freq + band/2.0
    low  = low/nyq
    high = high/nyq
    b, a = sig.iirfilter(order, [low, high], rp=ripple, btype='bandstop',
                     analog=False, ftype=filter_type)
    filtered_data = sig.lfilter(b, a, data)
    return filtered_data

#there are issue with the current version of notch filter
def notch(f0=50,Q=30):
    b,a=sig.lfilter(sig.iirnotch(f0, Q))
    return b,a

def notch_filter(data,f0=50,Q=30):
    b,a=notch(f0,Q)
    y=sig.lfilter(b,a,data)
    return y
   """ 