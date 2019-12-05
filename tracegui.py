# -*- coding: utf-8 -*-
"""


@author: Vincenzo Marra

Class to create the gui to visualise Ephys recordings 

"""


import MEAopen as mea
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np



class MainApp():
    def __init__(self, master):
            #variables
            self.file_name=''
            self.rec=mea.MEA_rec
            self.t_startR1=tk.DoubleVar(value=10.5)
            self.t_startR2=tk.DoubleVar(value=60.5)
            self.filt_value = tk.BooleanVar() 
            self.chan=1
            self.sweep=None
            #GUI
            self.master = master
            master.title("MEA Trace GUI")
            #top buttons
            self.open_button = tk.Button(master, text="Open", command=self.openMEA)
            self.open_button.grid(column=0, row=0)
            self.plot_button = tk.Button(master, text="Plot", command=self.plot_traces)
            self.plot_button.grid(column=1, row=0)
            self.quit_button = tk.Button(master, text="Quit", command=master.destroy)
            self.quit_button.grid(column=2, row=0)
            #Channel and sweep selection
            tk.Label(self.master, text='Channel').grid(column=0, row=1)
            tk.Label(self.master, text='Sweep').grid(column=1, row=1)
            self.chan_combo=ttk.Combobox(master)
            #filter checkbox
            self.filter_box = tk.Checkbutton(master, text='Filter 50Hz', variable=self.filt_value)
            self.filter_box.grid(column=2, row=1)
            #self.chan_combo['values']=tuple(range(1, 65))# this should be set after opening
            #self.chan_combo.current(0)# this should be set after opening
            self.chan_combo.grid(column=0, row=2)
            self.sweep_combo=ttk.Combobox(master)
            #self.sweep_combo['values']=None #tuple(range(1, 61))# this should be set after opening
            #self.sweep_combo.current(1)# this should be set after opening
            self.sweep_combo.grid(column=1, row=2)
            #file name
            self.file_label=tk.Label(self.master, text="NO FILE SELECTED!")
            self.file_label.grid(column=0, row=3)
            #figure area and navigation tools
            self.fig = Figure(figsize=(8, 7), dpi=100)
            self.canvas = FigureCanvasTkAgg(self.fig, master)  # A tk.DrawingArea.
            self.canvas.get_tk_widget().grid(column=1, row=4)
            #subplots
            self.axs=([self.fig.add_subplot(211,xlabel='ms',ylabel='mV'),
                       self.fig.add_subplot(223,xlabel='ms',ylabel='mV'),self.fig.add_subplot(224,xlabel='ms',ylabel='mV')])
            #workaround as Navigationtoolbar seems to only work with .pack and it's not comaptible with frame
            self.toolbarFrame = tk.Frame(master=root)
            self.toolbarFrame.grid(column=1, row=5)
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)
            #sliders for subplots
            tk.Label(self.master, text='Response 1').grid(column=0, row=6)
            tk.Label(self.master, text='Response 2').grid(column=0, row=7)
            self.slideR1 = tk.Scale(master, from_=0, to=100, resolution=0.1, orient='horizontal', length=400,
                                    variable = self.t_startR1, command=self.plot_traces)#needs to be just subplot
            self.slideR1.grid(column=1, row=6)
            self.slideR2 = tk.Scale(master, from_=0, to=100, resolution=0.1, orient='horizontal', length=400,
                                    variable = self.t_startR2, command=self.plot_traces)#needs to be just subplot
            self.slideR2.grid(column=1, row=7)
            self.analysis_button = tk.Button(master, text="Analysis", command=self.slope_analysis)
            self.analysis_button.grid(column=3, row=6)
            self.savesvg_button = tk.Button(master, text="Save SVG", command=self.save_svg)
            self.savesvg_button.grid(column=3, row=7)
            
    def openMEA(self):
        self.file_name = askopenfilename()
        self.rec=mea.MEA_rec(self.file_name)
        self.chan_combo['values']=self.rec.chan_list
        self.chan_combo.current(0)
        self.sweep_combo['values']=('All',)+tuple(range(1, self.rec.sweep_n))
        self.sweep_combo.current(0)
        self.label_file()
    def label_file(self):
        if self.file_name!='':
            self.file_label['text']=self.file_name[self.file_name.rfind('/')+1:]#writes filename only
    
    def notch_filter(self):
        chan=self.chan_combo.get()
        self.rec=self.rec.notch_filter(chan)
        
    
    #needs to decide whether to have one single function for all plots or not
    def plot_traces(self):
        chan=self.chan_combo.get()

        if self.sweep_combo.get()!='All': 
            sweep=int(self.sweep_combo.get())

        R1=self.t_startR1.get()
        R2=self.t_startR2.get()

        t = np.arange(0, 3, .01)

        for i in self.axs:
            i.clear()  #self.ax = self.fig.add_subplot(111)

        

        if self.filt_value.get()==True: 
            self.axs[0].plot(self.rec.get_time(),self.rec.notch_filter_mat(chan))
        else:
            self.axs[0].plot(self.rec.get_time(),self.rec.chan2matrix(chan))
        self.axs[1].plot(t, R1+2 * np.sin(2 * np.pi * t),'o') #change to actual trace
        self.axs[2].plot(t, 2 * np.sin(2 * np.pi * t),'r') #change to actual trace
        self.canvas.draw()

        

        

        
        
    def save_svg(self):
        self.fig.savefig(self.file_name[:self.file_name.rfind('.')]+self.chan_combo.get()+'.svg')
    
    def slope_analysis(self):
        chan=self.chan_combo.get()
        rec=self.rec
        R1=self.t_startR1.get()
        R2=self.t_startR2.get()
        first_sweep=1
        epsp1start=int(20*R1) #only works for 20KHz sampling
        epsp2start=int(20*R2) #only works for 20KHz sampling
        epsp1slopes=[]
        epsp2slopes=[]
        for i in range(first_sweep,rec.sweep_n+1):
            epsp1slopes.append(mea.fepsp_slope(rec.get_chan(chan,i)[epsp1start:epsp1start+80].values))
            epsp2slopes.append(mea.fepsp_slope(rec.get_chan(chan,i)[epsp2start:epsp2start+80].values))
        print(epsp1slopes)
        print(epsp2slopes)
        save=1
        if save>0:
            #this will save the slope values in a file
            heading="Response 1 \t PPR (R2/R1)\n "
            outlist=[]
            for j,k in zip(epsp1slopes,epsp2slopes):
                outlist.append(str(j)+' \t '+str(k/j)+' \n')
            outfile=self.file_name[:self.file_name.rfind('.')]+'.dat'
            f=open(outfile,'w')
            f.seek(0)
            f.write(heading)
            f.writelines(outlist)
            f.close()
        
        

        


if __name__ == "__main__":
    root = tk.Tk()
    my_app=MainApp(root)
    
    root.mainloop()
    


"""
root = tkinter.Tk()
root.wm_title("Trace GUI")

fig = Figure(figsize=(5, 4), dpi=100)
#t = np.arange(0, 3, .01)
#fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
#canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

def openMEA(fig=fig):
    file_name = askopenfilename()
    #rec=mea.MEA_rec(file_name)
    t = np.arange(0, 3, .01)
    fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
    canvas.draw()

    return file_name

def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


button_quit = tkinter.Button(master=root, text="Quit", command=_quit)
button_quit.pack(side=tkinter.RIGHT)

button_open= tkinter.Button(master=root, text="Open", command=openMEA)
button_open.pack(side=tkinter.LEFT)
label = tkinter.Label(master=root, text = 'Test').pack()


tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager."""
