from queue import Queue
from CamadaFisica import CamadaFisica
from CamadaEnlace import Enlace
from Utils import byte_formarter, graph_generator

"""
Padrao msg 
{'entrada': '', 'quadro': 3, 'edc': 0, 'enquadramento': '1', 'detecao': 'Tipo 1', 'mod_digital': 'A', 'mod_analogica': 'Tipo 1', 'erros': 0}
"""
class Transmissor:
    def __init__(self, in_queue:Queue, gui_queue:Queue):
        self.in_queue = in_queue
        self.gui_queue = gui_queue
   
    def start(self):
        while True:
            data = self.in_queue.get() # Recebe dicionário com dados de transmissão (mensagem, enquadramento, modulação)

            if data == "SAIR":
                print("Transmissor encerrando...")
                break
            else:
                msg = data["entrada"]

                encoded_msg = msg.encode("utf-8") # Exemplo: mensagem -> b'mensagem'
                self.gui_queue.put(["aplicacao", f'Mensagem a ser Enviada: {msg}'])
                self.gui_queue.put(["aplicacao", f'Mensagem em bytes: {byte_formarter(encoded_msg)}'])
                
                framed_msg = Enlace.enquadramento(data["enquadramento"], encoded_msg)
                self.gui_queue.put(["enlace", f'Mensagem Enquadrada: {byte_formarter(framed_msg)}'])
                
                encoded_signal = CamadaFisica.codficador_banda_base(data["mod_digital"], framed_msg)
                self.gui_queue.put(["fisica", graph_generator(data=encoded_signal, title=f'Sinal Codificado em {data["mod_digital"]}')])
                
                modulated_signal = CamadaFisica.modulador(data["mod_analogica"], encoded_signal)
                self.gui_queue.put(["fisica", graph_generator(data=modulated_signal, title=f'Sinal Codificado em {data["mod_analogica"]}')])


#  =============================
#         DEPURAÇÃO LOCAL
#  =============================

if __name__ == "__main__":
    # Cria as filas de comunicação
    in_queue = Queue()
    gui_queue = Queue()

    # Define os dados de entrada (simulando a camada de aplicação)
    data = {
        "entrada": "teste",                         # Mensagem que será transmitida
        "enquadramento": "Contagem de caracteres",  # Tipo de enquadramento
        "mod_digital": "NRZ-Polar",                 # Tipo de modulação digital
        "mod_analogica": "FSK"                      # Tipo de modulação analógica
    }

    # Coloca os dados na fila de entrada do transmissor
    in_queue.put(data)
    in_queue.put("SAIR") # Encerra depois de uma execução

    # Instancia o transmissor e inicia
    transmissor = Transmissor(in_queue, gui_queue)
    transmissor.start()

    # Imprime todos os valores da fila GUI (resultado das etapas de transmissão)
    while not transmissor.gui_queue.empty():
        print(transmissor.gui_queue.get())
