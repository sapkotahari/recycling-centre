from tkinter.filedialog import askopenfilename, Tk
import matplotlib.pyplot as plt
import numpy as np

Tk().withdraw()
with open(askopenfilename()) as f:
    
    eachline=f.readlines()


chan_names=(list(range(12,18))+list(range(21,29))+list(range(31,39))
+list(range(41,49))+list(range(51,59))+list(range(61,69))+list(range(71,79))+list(range(82,88)))

spk_times={}


for ch in chan_names:
    ch=str(ch)
    line_ind=3+ eachline.index('t\t'+ch+'\n')
    line=eachline[line_ind]
    spk_times[ch]=[]
    t_spike=lambda line: float(line[0:line.find('\t')])
    
    while eachline[line_ind]!='\n':
        
        spk_times[ch].append(t_spike(line))
        line_ind+=1
        line=eachline[line_ind]

for ch,spt in spk_times.items():
    if len(spt)>10:
        plt.hist(np.diff(spt), range=(0,2))
        plt.title('Channel '+ch)
        plt.show()

        
    
