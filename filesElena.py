#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 17:02:13 2020

@author: vincenzo
"""
import extracell_an as exa
import numpy as np
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename, Tk

ch1=[]
ch2=[]
winop=1 #se lo script non funziona cambia quel valore da 1 a 0 e vai a linea 20
if winop==1:
    Tk().withdraw()
    filename=askopenfilename()
else:
    filename="Prova7.dat" #se la finestra non funziona sostitusci Prova7 con il nome del file (nella stessa cartella)

with open(filename)as file:
    for i in file.readlines()[1:]:
        i=i.replace(',','.')
        i=i.split('\t')
        ch1.append(float(i[0]))
        ch2.append(float(i[2]))


thresh=2 #Cambia questo per cambiare la threshold

ch1_arr=np.array(ch1)
ch2_arr=np.array(ch2)
print("Canale 1:")
print("coastline: %f"%exa.coastline(ch1_arr))
spk1=exa.find_peaks(ch1_arr, threshold=thresh)
print("numero di spikes: %d"%len(spk1))


print("Canale 2:")
print("coastline: %f"%exa.coastline(ch2_arr))
spk2=exa.find_peaks(ch2_arr, threshold=thresh)
print("numero di spikes: %d"%len(spk2))


plt.subplots(1)
exa.plot_spikes(ch1_arr,spk_ind=spk1)
plt.subplots(1)
exa.plot_spikes(ch2_arr,spk_ind=spk2)
