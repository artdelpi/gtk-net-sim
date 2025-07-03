import socket
import pickle
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
        # Loop principal: aguarda novos dados da GUI pela fila
        while True:
            data = self.in_queue.get() # Recebe dicionário com dados de transmissão (mensagem, enquadramento, modulação)

            # Condição de encerramento
            if data == "SAIR":
                print("Transmissor encerrando...")
                break # Interrompe o loop
            else:
                # Mensagem, em bytes, a ser enquadrada, modulada e transmitida
                msg = data["entrada"]

                # Tipos de modulação e enquadramento do sinal a ser transmitido
                tipo_mod_analogica = data["mod_analogica"]
                tipo_mod_digital = data["mod_digital"]
                tipo_enquadramento = data["enquadramento"]
                tamanho_do_edc = data["edc"]
                tipo_detecao = data["detecao"]

                # Camada de Aplicação: Geração da Mensagem
                encoded_msg = msg.encode("utf-8") # Exemplo: mensagem -> b'mensagem'
                self.gui_queue.put(["aplicacao", f'Mensagem a ser Enviada: {msg}']) # Exibe string original
                self.gui_queue.put(["aplicacao", f'Mensagem em bytes: {byte_formarter(encoded_msg)}']) # Exibe representação binária
                
                # Camada de Enlace: Enquadramento
                framed_msg = Enlace.enquadramento(tipo_enquadramento, encoded_msg) # Enquadra mensagem da camada de aplicação
                self.gui_queue.put([
                    "enlace", 
                    f'Mensagem Enquadrada: {byte_formarter(framed_msg)}'
                ]) # Exibe quadro (em bits) na interface gráfica

                # Aplica EDC (Error Detection Code), caso selecionado
                if (tipo_detecao):
                    framed_msg = Enlace.aplicar_edc(tipo_detecao, framed_msg, tamanho_do_edc)
                    self.gui_queue.put([
                        "enlace", 
                        f"Quadro com EDC: {byte_formarter(framed_msg)}"
                    ])
                
                # Camada Física: Codificação Banda Base
                encoded_signal = CamadaFisica.codficador_banda_base(tipo_mod_digital, framed_msg) # Aplica codificação banda base no quadro
                self.gui_queue.put([
                    "fisica", 
                    graph_generator(data=encoded_signal, title=f'Sinal Codificado em {data["mod_digital"]}', signal_type='sinal_banda_base')
                ]) # Exibe gráfico resultante da codificação banda base
                
                # Camada Física: Modulação Analógica
                modulated_signal = CamadaFisica.modulador(tipo_mod_analogica, encoded_signal) # Aplica modulação analógica no sinal digital
                self.gui_queue.put([
                    "fisica", 
                    graph_generator(data=modulated_signal, title=f'Sinal Codificado em {data["mod_analogica"]}', signal_type='sinal_analogico')
                ]) # Exibe gráfico resultante da codificação analógica

                # Transmissão da Mensagem: Conecta com o Receptor
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("localhost", 711))  # Porta e host iguais ao do receptor

                    # Dados dos sinais e configurações
                    msg_dict = {
                        "encoded_signal": encoded_signal, # Sinal digital: lista de níveis lógicos
                        "modulated_signal": modulated_signal, # Sinal analógico: lista de amostras
                        "mod_analogica": data["mod_analogica"],
                        "mod_digital": data["mod_digital"],
                        "enquadramento": data["enquadramento"],
                        "edc": data["edc"], # Tamanho do EDC
                        "detecao": data["detecao"] # Tipo do EDC
                    }

                    # Serializa o dicionário em bytes para envio
                    serialized_data = pickle.dumps(msg_dict)

                    # Envia os dados pra porta 711 do servidor localhost
                    s.sendall(serialized_data)

                    print("Mensagem enviada com sucesso!") # Confirma envio


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
        "enquadramento": "FLAGS Inserção de bits",  # Tipo de enquadramento
        "mod_digital": "Bipolar",                   # Tipo de modulação digital
        "mod_analogica": "8-QAM"                    # Tipo de modulação analógica
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
