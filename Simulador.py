from queue import Queue
from threading import Thread
from InterfaceGUI import GUI_TX, GUI_RX
from Transmissor import Transmissor
from Receptor import Receptor
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# Fila do transmissor (envia pra GUI_TX)
tx_out_queue = Queue()
tx_in_queue = Queue()

# Fila do receptor (envia pra GUI_RX)
rx_out_queue = Queue()
rx_in_queue = Queue()

# Instancia módulos
transmissor = Transmissor(in_queue=tx_in_queue, gui_queue=tx_out_queue)
receptor = Receptor(gui_queue=rx_out_queue)

# Instancia interfaces gráficas
gui_rx = GUI_RX(rx_out_queue)
gui_tx = GUI_TX(tx_out_queue, tx_in_queue, gui_rx) 
# Cria as janelas na thread principal
tx_window = gui_tx.create_window()
rx_window = gui_rx

# Configura o fechamento
def fechar_tudo(*_):
    tx_in_queue.put("SAIR")
    receptor.stop()
    Gtk.main_quit()

tx_window.connect("destroy", fechar_tudo)
rx_window.connect("destroy", fechar_tudo)

# Mostra ambas as janelas
tx_window.show_all()
rx_window.show_all()

# Threads dos módulos
t_transmissor = Thread(target=transmissor.start)
t_receptor = Thread(target=receptor.start)

# Inicia os módulos
t_transmissor.start()
t_receptor.start()

# Loop principal GTK (na thread principal)
Gtk.main()

# Finalização após fechamento das janelas
t_transmissor.join()
t_receptor.join()