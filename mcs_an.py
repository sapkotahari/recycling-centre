from tkinter.filedialog import askopenfilename, askdirectory, Tk
from os import listdir, path
import ntpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class MCS_Spikes(object):
    """This class loads an MultiChannelSystems (MCS) spike analyser (MCS software) output and 
    provides a few  analyses"""
    def __init__(self, filename):
        self.condition="" #experimental condition
        self.filename=filename #full path and name
        self.recid= ntpath.basename(self.filename[:self.filename.find('.txt')]) #short name no path nor extention
        with open(filename) as f:
            eachline=f.readlines()
        #finds the name of the channels by searching each line
        self.chan_names=['Ch'+i[i.find('t\t')+2:i.find('\n')] for i in eachline if i.find("t\t")==0]
        #remove reference that may appear in some files
        if 'ChRef' in self.chan_names: self.chan_names.remove('ChRef')
        
        #populates a dict with channels as keys and a list of spike times as values
        self.spk_times={}
        for ch in self.chan_names:
            #creates a dictionary with ChN and spike times
            ch_n=ch[2:] #remove Ch from channel name
            line_ind=3+ eachline.index('t\t'+ch_n+'\n') #this is very specific to the MCS file format
            line=eachline[line_ind]
            self.spk_times[ch]=[]
            t_spike=lambda line: float(line[0:line.find('\t')])           
            while eachline[line_ind]!='\n':             
                self.spk_times[ch].append(t_spike(line))
                line_ind+=1
                line=eachline[line_ind]

    def chan_dict2mat(self, chan_dict):
        """Converts dict with spikes per each channel to an 8x8 matrix similar
        to MEA probe arrangement. Specific to MCS: First digit is the column the second the row """
        mat=np.ones((8,8)) #creates the matrix
        for c in self.chan_names: #finds the spatial position of the channel
            chan_row=int(c[-1])-1
            chan_col=int(c[2:-1])-1
            mat[chan_row,chan_col]=chan_dict[c] #assings a single value to the matrix position
        return mat
    
    def get_chan_mean_isi(self):
        """from the spiketime dict returns the mean InterSpikeInterval
        and pouplates a dict with channels as keys and meanISI as values"""
        chan_mean_isi={}
        for ch,spt in self.spk_times.items():
            chan_mean_isi[ch]=np.mean(np.diff(spt))
        return chan_mean_isi
    
    def get_chan_std_isi(self):
        """from the spiketime dict returns the standanrd deviation of InterSpikeInterval
        and pouplates a dict with channels as keys and standard deviation of ISI as values"""
        chan_std_isi={}
        for ch,spt in self.spk_times.items():
            chan_std_isi[ch]=np.std(np.diff(spt))
        return chan_std_isi
    
    def get_chan_CV_isi(self):
        """from the spiketime dictreturns the coefficient of variation of InterSpikeInterval
        and pouplates a dict with channels as keys and coefficient of variation of ISI as values"""
        chan_CV_isi={}
        for ch,spt in self.spk_times.items():
            chan_CV_isi[ch]=np.std(np.diff(spt))/np.mean(np.diff(spt))
        return chan_CV_isi
    
    def get_chan_mean_freq(self):
        """from the spiketime dict returns the mean frequency (Hz)
        and pouplates a dict with channels as keys and mean frequency as values"""
        chan_freq={}
        for ch, spt in self.spk_times.items():
            chan_freq[ch]=np.mean(1./np.diff(spt))
        return chan_freq
    
    def get_rec_mean_freq(self):
        """from the mean channel frequency dict returns the mean frequency (Hz)
        of the 3 most active channels"""

        active_chan_freq=sorted([x for x in self.get_chan_mean_freq().values() if not np.isnan(x)])
        return np.mean(active_chan_freq[-3:])
    
    def get_rec_CV_isi(self):
        """from the coefficient of variation channel ISI dict returns the mean CV of ISI
        of the 3 most active channels"""
        #find the 3 highest frequencies
        high_freq=sorted([x for x in self.get_chan_mean_freq().values() if not np.isnan(x)])[-3:]
        #find the channel with the 3 highest values
        CV_isi_active=[]
        for k,v in self.get_chan_mean_freq().items():
            if v in high_freq:
                CV_isi_active.append(self.get_chan_CV_isi()[k])

        return np.mean(CV_isi_active)
        
    def find_adj_ch(self, ch_name):
        """finds the channels adjectent to ch_name based on MCS probe layout"""
        ch_int=int(ch_name[2:])
    
        adj_dist=[1,10,9,11]
        adj_ch=[]
        for i in self.chan_names:
    
            i_int=int(i[2:])
            if abs(i_int-ch_int) in adj_dist:
                adj_ch.append(i)
        return(adj_ch)
    
    
    
    def plot_isi_hist(self, min_spikes=10, hist_range=(0,2)):
        """plots the histogram of the ISI for the channels with more than 10 spikes"""
        for ch,spt in self.spk_times.items():
            if len(spt)>min_spikes:
                plt.hist(np.diff(spt), range=hist_range)
                plt.title('Channel '+ch)
                plt.show()
                 
    def plot_mat(self, chan_dict, parameter="", save=0):
        """generate a heatmat similar to the MEA physical arrangement from a 
        dict with channel name"""
        fig, ax= plt.subplots()
        im=ax.imshow(self.chan_dict2mat(chan_dict), cmap='plasma')
        ax.set_title(self.recid+parameter)
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel(parameter, rotation=-90, va="bottom")
        if save==1:
            plt.savefig(self.filename[:-4]+' '+parameter+'.png')
    
    def make_summary(self):
        """creates a summary dict with condition, freq, and CV of ISI for the
        recording"""
        summary={}
        summary['Name']=self.recid
        summary['Condition']=self.condition
        summary['Frequency']=self.get_rec_mean_freq()
        summary['ISI CV']=self.get_rec_CV_isi()
        return summary

      

def batch_open():
    """batch opens several files and puts them in a list of MCS_Spikes objects"""
    Tk().withdraw()
    filepath=askdirectory()
    filedir=listdir(filepath)
    print(filedir)
    reclist=[]
    for files in filedir:
        print(files)
        if files.find(".txt")!=-1:
            reclist.append(MCS_Spikes(filepath+'/'+files))
    return reclist

def set_batch_condition(reclist,condition):
    """sets or changes the experimental condition for a list of MCS_Spikes objects"""
    for i in reclist:    
        i.condition=condition

def make_dataframe(*reclists):
    """takes several lists of MCS_Spikes objects and turns them into a pandas dataframe"""

    summ=[i.make_summary() for sublist in reclists for i in sublist]
    
    return pd.DataFrame(summ)
    
    
        

if __name__ == "__main__":
    #opens a single text file with spike recordings
    Tk().withdraw()
    Spkt=MCS_Spikes(askopenfilename())