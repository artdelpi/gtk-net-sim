import socket
import time
import pickle
import numpy as np
from queue import Queue
from CamadaFisica import CamadaFisica
from CamadaEnlace import Enlace
from Utils import byte_formarter, graph_generator

class Receptor:
    def __init__(self, host="localhost", port=711, gui_queue=Queue()):
        self.host = host
        self.port = port
        self.gui_queue = gui_queue
        self.running = True  # Flag de controle

    def start(self):
        # Mensagem de status no terminal
        print("Receptor esperando conexão...")

        # Cria o socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Associa o socket ao host e à porta especificados na construtora
            s.bind((self.host, self.port))

            # Socket no modo de escuta, no máximo 1 conexão pendente
            s.listen(1)
            
            s.settimeout(1.0) # Evita bloqueio eterno no accept()

            # Loop principal do receptor
            while self.running:
                try:
                    # Espera conexão. Se passar de 1 segundo, dá timeout (socket.timeout)
                    conn, addr = s.accept()
                except socket.timeout:
                    # Sem conexão, volta pro início do loop pra checar o self.running
                    continue
                    
                # conn é o "canal" de comunicação do transmissor com o receptor
                with conn:
                    print(f"Conectado por {addr}")

                    # Buffer pra armazenar os dados recebidos
                    raw_data = b""

                    while True:
                        packet = conn.recv(4096) # Lê até 4096 bytes por vez na porta 711
                        if not packet:
                            break # Encerra a conexão se não tiver mais dados
                        raw_data += packet # Acumula dados no buffer

                    try:
                        data = pickle.loads(raw_data) # Reconstrói o dicionário (data) enviado pelo transmissor (Bytes -> Dicionário)
                    except Exception as e:
                        # Se não conseguir desserializar os bytes em dicionário
                        self.gui_queue.put(["aplicacao", f"Erro ao desserializar: {e}"])
                        continue

                    self.processar(data)

    def processar(self, data):
        time.sleep(2) # Espera 2 segundos pra processar o sinal (Efeito visual na GUI)

        try:
            # Sinal digital recebido pelo receptor
            sinal_digital = data["encoded_signal"]

            # Sinal analógico recebido pelo receptor
            sinal_modulado = data["modulated_signal"]
            
            # Tipos de modulação e enquadramento do sinal recebido
            tipo_mod_analogica = data["mod_analogica"]
            tipo_mod_digital = data["mod_digital"]
            tipo_enquadramento = data["enquadramento"]
            tipo_detecao = data["detecao"]
            tamanho_do_edc = data["edc"]
            taxa_de_erros = data["erros"]

            # Tratamento dos sinais caso haja ruído
            if (float(taxa_de_erros) > 0):
                sigma = taxa_de_erros # Desvio padrão do ruído

                # Gera vetor de ruído pro sinal analógico considerando Curva Gaussiana
                ruido = np.random.normal(0, sigma, size=len(sinal_modulado))

                # Aplica ruído no sinal analógico (Alteração em todos os pontos)
                sinal_modulado_ruidoso = np.array(sinal_modulado) + ruido

                # Camada Física: Exibe sinal analógico COM RUÍDO (Sem demodular)
                self.gui_queue.put([
                    "fisica",
                    graph_generator(sinal_modulado_ruidoso.tolist(), f"Sinal Recebido COM RUÍDO ({tipo_mod_analogica})", "sinal_analogico")
                ])

                # Gera vetor de ruído pro sinal digital
                ruido = np.random.normal(0, sigma, size=len(sinal_digital))

                # Aplica no sinal digital
                sinal_digital_ruidoso = np.array(sinal_digital) + ruido
                
                # Camada Física: Exibe Sinal Digital COM RUÍDO
                self.gui_queue.put([
                    "fisica",
                    graph_generator(sinal_digital_ruidoso.tolist(), f"Sinal Demodulado COM RUÍDO ({tipo_mod_digital})", "sinal_banda_base")
                ])
                sinal_digital, sinal_modulado = sinal_digital_ruidoso, sinal_modulado_ruidoso # Atualiza sinais, caso haja erro

            else:
                # Camada Física: Exibe sinal analógico (Sem demodular)
                self.gui_queue.put([
                    "fisica", 
                    graph_generator(sinal_modulado, f"Sinal Recebido SEM RUÍDO ({tipo_mod_analogica})", 'sinal_analogico')
                ])

                # Camada Física: Demodulação do Sinal Digital
                self.gui_queue.put([
                    "fisica", 
                    graph_generator(sinal_digital, f"Sinal Demodulado ({tipo_mod_digital})", 'sinal_banda_base')
                ])
            # Demodula sinal digital
            quadro_bytes = CamadaFisica.decodificador_banda_base(tipo_mod_digital, sinal_digital)

            # Verifica o EDC, caso utilizado
            if (tipo_detecao):
                self.gui_queue.put([
                    "enlace", 
                    f"Quadro com EDC: {byte_formarter(quadro_bytes)}"
                ])
                quadro_bytes = Enlace.verificar_edc(tipo_detecao, quadro_bytes, tamanho_do_edc)
                self.gui_queue.put([
                    "enlace", 
                    f"Quadro sem EDC: {byte_formarter(quadro_bytes)}"
                ])

            # Camada de Enlace: Desenquadramento
            self.gui_queue.put([
                "enlace", 
                f"Quadro decodificado: {byte_formarter(quadro_bytes)}"
            ])
            msg_bytes = Enlace.desenquadramento(tipo_enquadramento, quadro_bytes) # Recupera mensagem original, em bytes
            
            self.gui_queue.put(["aplicacao", f"Mensagem recebida (bytes): {byte_formarter(msg_bytes)}"]) # Confirmação de recebimento
            self.gui_queue.put(["aplicacao", f"Mensagem recebida: {msg_bytes}"]) # Confirmação de recebimento
        except Exception as e:
            self.gui_queue.put(["aplicacao", f"Erro ao processar sinal: {e}"]) # Comunica erro de processamento

    def stop(self):
        self.running = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
        except:
            pass
