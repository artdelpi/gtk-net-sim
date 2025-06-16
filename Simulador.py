from queue import Queue
from threading import Thread
from InterfaceGUI import GUI
from matplotlib.figure import Figure
import numpy as np


q1 = Queue()
q2 = Queue()

def consumer(inQ: Queue, outQ: Queue):
    while True:
        msg = inQ.get()
        print(msg)
        
        if msg == "SAIR":
            print("Consumer encerrando...")
            break

        # Enviar texto para aba da aplicação
        outQ.put(["aplicacao", "Dados processados: 11010011"])

        # Enviar texto para aba de enlace
        outQ.put(["enlace", "Quadro: 0110 | EDC: 101"])

        # Enviar gráfico para aba da física
        fig = Figure()
        ax = fig.add_subplot(111)
        x = np.linspace(0, 1, 100)
        y = np.sin(2 * np.pi * 3 * x)
        ax.plot(x, y)
        outQ.put(["fisica", fig])
        outQ.put(["fisica", fig])
        outQ.put(["fisica", fig])

gui = GUI(q1, q2)

t1 = Thread(target = gui.start)
t2 = Thread(target = consumer, args =(q2, q1))
t1.start()
t2.start()  

t1.join() 
q2.put("SAIR") 
t2.join()
