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



class MainApp:
    def __init__(self, master):
            #variables
            self.file_name=''
            self.rec=None
            self.t_startR1=10.5
            self.t_startR2=60.5
            self.chan=1
            self.sweep=None
            #GUI
            self.master = master
            master.title("MEA Trace GUI")
            self.open_button = tk.Button(master, text="Open", command=self.openMEA)
            self.open_button.grid(column=0, row=0)
            self.plot_button = tk.Button(master, text="Plot", command=self.plot_trace)
            self.plot_button.grid(column=1, row=0)
            self.quit_button = tk.Button(master, text="Quit", command=master.quit)
            self.quit_button.grid(column=2, row=0)
            tk.Label(self.master, text='Channel').grid(column=0, row=1)
            tk.Label(self.master, text='Sweep').grid(column=1, row=1)
            self.chan_combo=ttk.Combobox(master)
            self.chan_combo['values']=tuple(range(1, 65))# this should be set after opening
            self.chan_combo.current(0)# this should be set after opening
            self.chan_combo.grid(column=0, row=2)
            self.sweep_combo=ttk.Combobox(master)
            self.sweep_combo['values']=None #tuple(range(1, 61))# this should be set after opening
            #self.sweep_combo.current(1)# this should be set after opening
            self.sweep_combo.grid(column=1, row=2)
            self.file_label=tk.Label(self.master)
            self.file_label.grid(column=3, row=3)
            self.fig = Figure(figsize=(5, 4), dpi=100)
            self.canvas = FigureCanvasTkAgg(self.fig, master)  # A tk.DrawingArea.
            self.canvas.get_tk_widget().grid(column=1, row=4)#pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def label_file(self):
        if self.file_name=='':
            self.file_label.configure(text="NO FILE SELECTED!")
        else: 
            self.file_label.configure(text=self.file_name)
    def plot_trace(self):
        self.label_file()
        t = np.arange(0, 3, .01)
        self.fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t)) #change to actual trace
        self.canvas.draw()    
    def openMEA(self):
        self.file_name = askopenfilename()
        self.rec=mea.MEA_rec(file_name)
        


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