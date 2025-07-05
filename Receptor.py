import socket
import time
import pickle
import numpy as np
from queue import Queue
from CamadaFisica import CamadaFisica
from CamadaEnlace import Enlace
from Utils import byte_formarter, graph_generator, graph_constellation_8qam

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
            # Extrai sinais e parâmetros de comunicação
            sinal_digital = data["encoded_signal"]      # Sinal digital (codificado em NRZ-Polar, Bipolar ou Manchester). Ex: [-1, -1, 1, -1, 1, 1...]
            sinal_modulado = data["modulated_signal"]   # Sinal analógico (modulado em FSK, ASK ou 8-QAM). Ex: [0, 0, 0.0627, 0.125...] 
            params = {
                "tipo_mod_analogica": data["mod_analogica"],    # Ex: "FSK", "ASK", "8-QAM"
                "tipo_mod_digital": data["mod_digital"],        # Ex: "NRZ-Polar", "Bipolar", "Manchester"
                "tipo_enquadramento": data["enquadramento"],    # Ex: "Contagem de caracteres"...
                "tipo_detecao": data["detecao"],                # Tipo de detecção de erro. Ex: 
                "tamanho_do_edc": data["edc"],                  # Ex: 8, 16, 24... (Caso use CRC)
                "erros": float(data["erros"])                   # Nível de ruído (σ). Ex: 0.10, 0.20, 0.30...
            }

            # Processa ruído (se houver)
            if (params["erros"]) > 0:
                # Aplica o mesmo ruído ao sinal analógico e digital
                sinal_modulado, sinal_digital = self.processar_ruido(
                    sinal_modulado, sinal_digital, params["erros"]
                )

            # Exibe sinais da camada física
            self.exibir_camada_fisica(sinal_modulado, sinal_digital, params)

            # Exibe e processa a camada de enlace
            self.exibir_camada_enlace(sinal_digital, params)

            # Decodifica sinal digital, obtendo o quadro
            quadro_bytes = CamadaFisica.decodificador_banda_base(params["tipo_mod_digital"], sinal_digital)
            
            # Exibe e processa a camada de aplicação
            self.exibir_camada_aplicacao(quadro_bytes, params)

        except Exception as e:
            self.gui_queue.put(["aplicacao", f"Erro ao processar sinal: {e}"]) # Comunica erro de processamento


    def processar_ruido(self, sinal_modulado, sinal_digital, sigma) -> tuple:
        # Gera vetor de ruído pro sinal analógico considerando Curva Gaussiana
        ruido = np.random.normal(0, sigma, size=len(sinal_modulado))

        # Aplica ruído no sinal analógico (Alteração em todos os pontos)
        sinal_modulado_ruidoso = np.array(sinal_modulado) + np.array(ruido)

        # Acumula a média do ruído anterior pra cada 100 pontos (1 bit)     
        ruido_por_bit = [] 

        # Pra cada 100 pontos (1 bit)
        for i in range(0, len(ruido), 100): # (0, 100, 200, 300 ...)
            media = np.mean(np.array(ruido[i:i+100])) # Tira média de ruído de 100 amostras
            ruido_por_bit.append(media) # Guarda essa média
                
        # Aplica (soma) as médias do ruído de cada 100 pontos ao valor digital correspondente
        sinal_digital_ruidoso = np.array(sinal_digital) + ruido_por_bit

        return (sinal_modulado_ruidoso.tolist(), sinal_digital_ruidoso.tolist())


    def exibir_camada_fisica(self, sinal_modulado, sinal_digital, params) -> None:
        """Exibe as informações da camada física"""
        try: 
            tipo_mod_analogica = params["tipo_mod_analogica"] # Recupera tipo de modulação analógica
            tipo_mod_digital = params["tipo_mod_digital"]     # Recupera tipo de modulação digital

            # Exibe sinal analógico
            self.gui_queue.put([
                "fisica", 
                graph_generator(sinal_modulado, f"Sinal Analógico Recebido em ({tipo_mod_analogica})", 'sinal_analogico')
            ])

            # Exibe sinal digital
            self.gui_queue.put([
                "fisica", 
                graph_generator(sinal_digital, f"Sinal Codificado em {tipo_mod_digital}", 'sinal_banda_base')
            ])
        except Exception as e:
            self.gui_queue.put(["fisica", f"Erro ao processar camada física: {e}"])


    def exibir_camada_enlace(self, sinal_digital, params) -> None:
        """Processa e exibe as informações da camada de enlace"""
        try:
            tipo_mod_digital = params["tipo_mod_digital"]       # Recupera tipo de modulação digital
            tipo_detecao = params["tipo_detecao"]               # Recupera tipo de detecção de erros
            tamanho_do_edc = params["tamanho_do_edc"]           # Recupera tamanho do EDC
            tipo_enquadramento = params["tipo_enquadramento"]   # Recupera tipo de enquadramento

            # Decodifica o sinal digital para obter o quadro com EDC
            quadro_bytes = CamadaFisica.decodificador_banda_base(tipo_mod_digital, sinal_digital)

            # Exibe tipo de EDC utilizado
            self.gui_queue.put(["enlace", f">>> EDC utilizado: {tipo_detecao} <<<"])

            # Exibe quadro com EDC
            self.gui_queue.put(["enlace", f"Quadro com EDC: {byte_formarter(quadro_bytes)}"])

            # Tenta verificar e remover o EDC
            try:
                quadro_sem_edc = Enlace.verificar_edc(tipo_detecao, quadro_bytes, tamanho_do_edc)
                self.gui_queue.put(["enlace", f"Quadro sem EDC: {byte_formarter(quadro_sem_edc)}"])
            except Exception as e:
                quadro_sem_edc = quadro_bytes  # Mantém o quadro original se der erro
                self.gui_queue.put(["enlace", f"Erro ao verificar EDC: {e}"])

            # Exibe tipo de enquadramento
            self.gui_queue.put(["enlace", f">>> Tipo de enquadramento: {tipo_enquadramento} <<<"])

            # Exibe quadro antes e depois do desenquadramento
            self.gui_queue.put(["enlace", f"Quadro antes do desenquadramento: {byte_formarter(quadro_sem_edc)}"])

            try:
                quadro_desenquadrado = Enlace.desenquadramento(tipo_enquadramento, quadro_sem_edc)
                self.gui_queue.put(["enlace", f"Quadro desenquadrado (dados originais): {byte_formarter(quadro_desenquadrado)}"])
            except Exception as e:
                quadro_desenquadrado = quadro_sem_edc  # Mantém como estava se falhar
                self.gui_queue.put(["enlace", f"Erro ao desenquadrar quadro: {e}"])

        except Exception as e:
            self.gui_queue.put(["enlace", f"Erro ao processar camada de enlace: {e}"])


    def exibir_camada_aplicacao(self, quadro_bytes, params) -> None:
        """Processa e exibe as informações da camada de aplicação"""
        tipo_enquadramento = params["tipo_enquadramento"] # Recupera tipo de enquadramento
        tipo_detecao = params["tipo_detecao"]             # Recupera tipo de detecção de erros
        tamanho_do_edc = params["tamanho_do_edc"]         # Recupera tamanho do EDC

        # Remove EDC do quadro
        quadro_sem_edc = Enlace.verificar_edc(tipo_detecao, quadro_bytes, tamanho_do_edc)

        # Desenquadra quadro e recupera mensagem original
        msg_bytes = Enlace.desenquadramento(tipo_enquadramento, quadro_sem_edc)
        
        # Exibe mensagem da aplicação em bits
        self.gui_queue.put(["aplicacao", f"Mensagem recebida (bits): {byte_formarter(msg_bytes)}"])

        # Exibe mensagem da aplicação em bytes
        self.gui_queue.put(["aplicacao", f"Mensagem recebida: {msg_bytes}"])


    def stop(self):
        self.running = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
        except:
            pass
