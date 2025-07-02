from queue import Queue
from threading import Thread
from InterfaceGUI import GUI_TX, GUI_RX
from Transmissor import Transmissor
from Receptor import Receptor

# Fila do transmissor (envia pra GUI_TX)
tx_out_queue = Queue()
tx_in_queue = Queue()

# Fila do receptor (envia pra GUI_RX)
rx_out_queue = Queue()
rx_in_queue = Queue()

# Instancia interfaces gráficas
gui_tx = GUI_TX(tx_out_queue, tx_in_queue)
gui_rx = GUI_RX(rx_out_queue)

# Instancia módulos
transmissor = Transmissor(in_queue=tx_in_queue, gui_queue=tx_out_queue)
receptor = Receptor(gui_queue=rx_out_queue)

# Threads das interfaces e módulos
t_gui_tx = Thread(target=gui_tx.start)
t_gui_rx = Thread(target=gui_rx.start)
t_transmissor = Thread(target=transmissor.start)
t_receptor = Thread(target=receptor.start)

# Inicia tudo
t_gui_tx.start()
t_gui_rx.start()
t_transmissor.start()
t_receptor.start()

# Espera janelas fecharem
t_gui_tx.join()
t_gui_rx.join()

# Finaliza lógica de execução
tx_in_queue.put("SAIR")  # Manda transmissor encerrar
t_transmissor.join()

receptor.stop()
t_receptor.join()
