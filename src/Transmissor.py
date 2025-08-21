import socket
import pickle
from queue import Queue
from src.CamadaFisica import CamadaFisica
from src.CamadaEnlace import Enlace
from src.Utils import byte_formarter, graph_generator

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
                # Mensagem (string) a ser enquadrada, modulada e transmitida
                msg = data["entrada"]

                # Mensagem em bytes
                msg_bytes = msg.encode ("utf-8") # Exemplo: mensagem -> b'mensagem'

                # Tipos de modulação e enquadramento do sinal a ser transmitido
                tipo_mod_analogica = data["mod_analogica"]  # Ex: "FSK", "ASK", "8-QAM"
                tipo_mod_digital = data["mod_digital"]      # Ex: "NRZ-Polar", "Bipolar", "Manchester"
                tipo_enquadramento = data["enquadramento"]  # Ex: "Contagem de caracteres"...
                tamanho_do_edc = data["edc"]                # Ex: 8, 16, 24... (Caso use CRC)
                tipo_detecao = data["detecao"]              # Tipo de detecção de erro. Ex: "Hamming", "CRC", "Bit de paridade par" 

                # Exibe a camada de aplicação
                self.exibir_camada_aplicacao(msg_bytes)

                # Exibe e processa a camada de enlace
                self.exibir_camada_enlace(msg_bytes, data)

                # Aplica o enquadramento selecionado na msg da aplicação
                quadro_sem_edc = Enlace.enquadramento(tipo_enquadramento, msg_bytes)

                # Aplica o EDC no quadro
                quadro_bytes = Enlace.aplicar_edc(tipo_detecao, quadro_sem_edc, tamanho_do_edc)

                # Exibe e processa sinais da camada física
                self.exibir_camada_fisica(quadro_bytes, data)

                # Obtém o sinal digital
                sinal_digital = CamadaFisica.codficador_banda_base(tipo=tipo_mod_digital, dado=quadro_bytes)

                # Obtém o sinal analógico
                sinal_modulado = CamadaFisica.modulador(tipo=tipo_mod_analogica, dado=quadro_bytes)

                # Transmissão da Mensagem: Conecta com o Receptor
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("localhost", 711))  # Porta e host iguais ao do receptor

                    # Dados dos sinais e configurações
                    msg_dict = {
                        "encoded_signal": sinal_digital,        # Sinal digital (codificado em NRZ-Polar, Bipolar ou Manchester). Ex: [-1, -1, 1, -1, 1, 1...]
                        "modulated_signal": sinal_modulado,     # Sinal analógico: lista de amostras. Ex: [0, 0, 0.0627, 0.125...] 
                        "mod_analogica": data["mod_analogica"], # Ex: "FSK", "ASK", "8-QAM"
                        "mod_digital": data["mod_digital"],     # Ex: "NRZ-Polar", "Bipolar", "Manchester"
                        "enquadramento": data["enquadramento"], # Tipo de enquadramento. Ex: "Contagem de caracteres"...
                        "edc": data["edc"],                     # Tamanho do EDC. Ex: 8, 16, 24... (Caso use CRC)
                        "detecao": data["detecao"],             # Tipo de detecção de erro. Ex: "Hamming", "CRC", "Bit de paridade par"
                        "erros": data["erros"]                  # Nível de ruído (σ). Ex: 0.10, 0.20, 0.30...
                    }

                    # Serializa o dicionário em bytes para envio
                    serialized_data = pickle.dumps(msg_dict)

                    # Envia os dados pra porta 711 do servidor localhost
                    s.sendall(serialized_data)

                    print("Mensagem enviada com sucesso!") # Confirma envio


    def exibir_camada_aplicacao(self, msg_bytes) -> None:
        """Exibe as informações da camada de aplicação"""
        try:
            # Exibe string original
            self.gui_queue.put(["aplicacao", f'Mensagem a ser Enviada: {msg_bytes}']) 

            # Exibe representação binária
            self.gui_queue.put(["aplicacao", f'Mensagem em bits: {byte_formarter(msg_bytes)}'])
        except Exception as e:
            self.gui_queue.put(["enlace", f"Erro ao processar camada de aplicação: {e}"])
        

    def exibir_camada_enlace(self, msg_bytes, data) -> None:
        """Processa e exibe as informações da camada de enlace"""
        try:
            tipo_detecao = data["detecao"]              # Recupera tipo de detecção de erros
            tamanho_do_edc = data["edc"]                # Recupera tamanho do EDC
            tipo_enquadramento = data["enquadramento"]  # Recupera tipo de enquadramento

            # Enquadra mensagem da camada de aplicação
            quadro_sem_edc = Enlace.enquadramento(tipo_enquadramento, msg_bytes)
            self.gui_queue.put([
                "enlace", 
                f'Mensagem Enquadrada: {quadro_sem_edc}'
            ]) # Exibe quadro (em bits) na interface gráfica

            self.gui_queue.put([
                "enlace", 
                f'Mensagem Enquadrada em Bits: {byte_formarter(quadro_sem_edc)}'
            ]) # Exibe quadro (em bits) na interface gráfica

            # Aplica EDC (Error Detection Code) selecionado
            quadro_bytes = Enlace.aplicar_edc(tipo_detecao, quadro_sem_edc, tamanho_do_edc)
            self.gui_queue.put([
                "enlace", 
                f"Quadro com EDC: {byte_formarter(quadro_bytes)}"
            ])
        except Exception as e:
            self.gui_queue.put(["enlace", f"Erro ao processar camada de enlace: {e}"])
    
    
    def exibir_camada_fisica(self, quadro, data) -> None:
        """Processa e exibe as informações da camada de enlace"""
        try:
            tipo_mod_analogica = data["mod_analogica"]  # Ex: "FSK", "ASK", "8-QAM"
            tipo_mod_digital = data["mod_digital"]

            sinal_digital = CamadaFisica.codficador_banda_base(tipo=tipo_mod_digital, dado=quadro)
            self.gui_queue.put([
                "fisica", 
                graph_generator(data=sinal_digital, title=f'Sinal Codificado em {tipo_mod_digital}', signal_type='sinal_banda_base')
            ]) # Exibe gráfico resultante da codificação banda base
            
            sinal_modulado = CamadaFisica.modulador(tipo=tipo_mod_analogica, dado=quadro)
            self.gui_queue.put([
                "fisica", 
                graph_generator(data=sinal_modulado, title=f'Sinal Analógico Modulado em ({data["mod_analogica"]})', signal_type='sinal_analogico')
            ]) # Exibe gráfico resultante da codificação analógica
        except Exception as e:
            self.gui_queue.put(["enlace", f"Erro ao processar camada física: {e}"])
        