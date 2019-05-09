import h5py
import numpy as np
import pylab as pl
from os import listdir, path
from scipy import signal

filedir=listdir(path.dirname(path.realpath(__file__)))# or listdir(getcwd())

allh5=[]

for files in filedir:
    if files.find(".h5")!=-1:
        allh5.append(files)



traces = h5py.File(allh5[0], "r") #opens the h5 file
presynvoltage='im sec'
postsyncurrent='2nd VmscalAI #4'
stim_name=presynvoltage
channelname=postsyncurrent
#h5 files store data points in dictionaries so the next few lines print the keys info
print(traces.keys()) #print the keys for your specific file
print('\n')

print(traces[channelname].keys()) #Change Scaled to whatever keys you have in your specific file
#getting deeper in the file
print('\n')
print(traces[channelname]['section_0'].keys())
print('\n')
print(traces[channelname]['section_0']['data'][:])
stim_trace=traces[stim_name]['section_0']['data'][:]
resp_trace=traces[channelname]['section_0']['data'][:] #finally got the raw numbers

spikes=find_events(stim_trace,'ap')

epscs=find_responses(resp_trace,spikes)
twenty=[]
infl=[]
val=[]
bslval=[]
for i in epscs:
    twenty.append((int(find_perc(resp_trace,i,0.2,20,onset='onset')[0])))
    infl.append((int(find_perc(resp_trace,i,0.2,20,onset='onset')[1])))
    val.append((int(find_perc(resp_trace,i,0.2,20,onset='onset')[2])))
    bslval.append((int(find_perc(resp_trace,i,0.2,20,onset='onset')[3])))


pl.plot(resp_trace,'.')
pl.plot(twenty,resp_trace[twenty],'go')
pl.plot(infl,resp_trace[infl],'ro')
pl.plot(twenty,val,'ko')
pl.plot(epscs,resp_trace[bslval],'yo')


"""
pl.plot(resp_trace)
pl.show()
ev=find_responses(resp_trace,find_events(stim_trace,'ap'),'epsc')
pl.plot(ev,raw_traces[ev],'go')
#pl.plot(rej,raw_traces[rej],'ro')
"""
