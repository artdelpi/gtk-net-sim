from queue import Queue
from threading import Thread
from InterfaceGUI import GUI
from matplotlib.figure import Figure
import numpy as np
from Transmissor import Transmissor


q1 = Queue()
q2 = Queue()

gui = GUI(q1, q2)
transmissor = Transmissor(in_queue=q2, gui_queue=q1)
t1 = Thread(target = gui.start)
t2 = Thread(target = transmissor.start)

t1.start()
t2.start()  

t1.join() 
q2.put("SAIR") 
t2.join()
