# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:07:18 2019

@author: localadmin1
"""

#Collection of useful functions to analyse traces

def find_nearest(array,value):
    """finds index of nearest value in a array"""
    ind = (np.abs(array-value)).argmin()
    return ind

def val_dist(a,b):
    """fids the distance between two values regardless of their sign"""
    if (a<0 and b<0):
        dist=abs(float(a))-abs(b)
    else:
        dist=float(a)-b
    return abs(dist)


def find_incipit(trace): return np.argmax(np.abs(np.diff(trace)))+1