"""Instructions:
-Modify line 15 to indicate the channel you want an average of.    
-Run the script (F5 in spyder)
-Open the file you need (the window may not appear at the forefront/OSX may give issue see instructions)
-Save the image as SVG (or any other format)
"""

import matplotlib.pyplot as plt
import numpy as np
import tracefunc as trf
import MEAopen as mea
from tkinter.filedialog import askopenfilename, Tk


channel= 11 #change the number to match the channel you want to analyse

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearin
"""if the code below doesn't work on OSX by opening a window 
substitute the part after filename = 
with file path expressed this way 
"/Users/USERNAME/Desktop/somedir/somefile.txt" """

file_name = askopenfilename() 
rec=mea.MEA_rec(file_name)

m=rec.chan2matrix(channel)
plt.plot(rec.get_time(),m.mean(1))
plt.show()