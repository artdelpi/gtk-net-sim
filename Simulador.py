from queue import Queue
from threading import Thread
from InterfaceGUI import GUI
from Transmissor import Transmissor
from Receptor import Receptor

# Fila de saída para GUI (mensagens e gráficos)
q1 = Queue()
# Fila de entrada da aplicação (entrada do transmissor)
q2 = Queue()

# GUI e componentes
gui = GUI(q1, q2)
transmissor = Transmissor(in_queue=q2, gui_queue=q1)
receptor = Receptor(gui_queue=q1)

# Threads da execução concorrente
t3 = Thread(target=receptor.start)  # Inicia um servidor socket
t2 = Thread(target=transmissor.start)
t1 = Thread(target=gui.start)

# Inicia threads
t3.start()
t2.start()
t1.start()

# Espera a GUI encerrar
t1.join()

# Quando a GUI fechar, manda o transmissor parar
q2.put("SAIR")
t2.join()

receptor.stop()
t3.join()
