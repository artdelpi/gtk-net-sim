import src.Utils as Utils
import numpy as np

class CamadaFisica:
    @staticmethod
    def codficador_banda_base(tipo, dado):
        """
        Escolhe e executa algum tipo de codificação de banda base.

        Parâmetros:
        • tipo (str): Tipo de codificação.
        • dado (bytes): Quadro vindo da camada de enlace.

        Retorna:
        • list[int]: Lista com o sinal codificado.
        """
        encoded_msg = ''
        if(tipo == "NRZ-Polar"):
            return CamadaFisica.codificar_nrz_polar(dado)
        elif(tipo == "Manchester"):
            return CamadaFisica.codificar_manchester(dado)
        elif(tipo == "Bipolar"):
            return CamadaFisica.codificar_bipolar(dado)
        raise ValueError(f"Tipo de codificação inválida: {tipo}")
   
    @staticmethod
    def decodificador_banda_base(tipo, dado):
        decoded_msg = ''
        if(tipo == "NRZ-Polar"):
            return CamadaFisica.decodificar_nrz_polar(dado)
        elif(tipo == "Manchester"):
            return CamadaFisica.decodificar_manchester(dado)
        elif(tipo == "Bipolar"):
            return CamadaFisica.decodificar_bipolar(dado)
        raise ValueError(f"Tipo de codificação inválida: {tipo}")


    @staticmethod
    def modulador(tipo, dado):
        modulated_msg = ''
        if(tipo == "FSK"):
            return CamadaFisica.modular_fsk(dado)
        elif(tipo == "ASK"):
             return CamadaFisica.modular_ask(dado)
        elif(tipo == "8-QAM"):
            return CamadaFisica.modular_8qam(dado)
        raise ValueError(f"Tipo de modução inválida: {tipo}")
    

    @staticmethod
    def codificar_nrz_polar(dado: bytes) -> list:
        """
        Transforma sequência de bytes em um sinal codificado NRZ-Polar.

        Dinâmica da codificação:
            Bit 0 → -1
            Bit 1 → +1
        
        Funcionamento:
        • Converte bytes (ex: b'teste') em string de bits (ex: '01000001 01100101...').
        • Remove espaços na string de bits.
        • Monta uma lista com valores da modulação NRZ-Polar (ex: [-1, 1, -1, ...]).

        Parâmetro:
        • dado (bytes): Um quadro da camada de enlace.

        Retorna:
        • list[int]: Lista com o sinal NRZ-Polar.

        Exemplo:
            Entrada: b"A" → bits "01000001"
            Saída: [-1, 1, -1, -1, -1, -1, 1, -1]
        """
        # Transforma bytes em string de bits e remove espaços
        bits_str = Utils.byte_formarter(dado).replace(' ', '')

        # Faz o mapeamento 0 → -1 e 1 → +1
        sinal = [1 if bit == '1' else -1 for bit in bits_str]
        return sinal


    @staticmethod
    def decodificar_nrz_polar(sinal_digital:list) -> bytes:
        """
        Decodifica um sinal digital codificado com NRZ-Polar.

        Funcionamento:
        • Converte lista com valores da NRZ-Polar (ex: [-1, 1, -1, ...]) em uma lista de 1s e 0s.
        • Agrupa bits em uma string e transforma num inteiro binário.
        • Converte de inteiro pra bytes e recupera o quadro.

        Parâmetro:
        • list[int]: Lista com o sinal NRZ-Polar.

        Retorna:
        • bytes: Um quadro da camada de enlace.

        Exemplo:
            Entrada: [-1, 1, -1, -1, -1, -1, 1, -1]
            Saída: bits "01000001" → b"A"
        """
        # Tratamento pra ruído: caso algum valor não seja -1 ou 1
        if (any(v not in (1, -1) for v in sinal_digital)):
            buffer = []
            for v in sinal_digital:
                # Entende valores < 0 como -1
                if (v < 0):
                    buffer.append(-1)
                # Entende valores >=0 como 1
                else:
                    buffer.append(1)
            # Atualiza sinal digital pra decodificar após ajuste
            sinal_digital = buffer

        # Desfaz o mapeamento da NRZ-Polar numa string dos bits
        bits_str = "".join(["1" if v == 1 else "0" for v in sinal_digital])

        # Toma o quadro em inteiro na base 2 pra aplicar o to_bytes()
        quadro_bits = int(bits_str, 2)

        # Calcula o número de bytes
        num_bytes = (len(bits_str)+7)//8 

        # Obtém o quadro original, em bytes
        quadro = quadro_bits.to_bytes(num_bytes, "big")
        return quadro


    @staticmethod
    def codificar_manchester(dado:bytes) -> list:
        """
        Transforma sequência de bytes em um sinal codificado Manchester.

        Dinâmica da codificação:
            Bit XOR CLK: 
            Bit 0 CLK 0 → 0
            Bit 0 CLK 1 → 1
            Bit 1 CLK 0 → 1
            Bit 1 CLK 1 → 0
        
        Funcionamento:
        • Converte bytes (ex: b'teste') em string de bits (ex: '01000001 01100101...').
        • Remove espaços na string de bits.
        • Monta um sinal clock de duas vezes o tamanho da palavra de bits.
        • Para cada par de bit do clock, faz o XOR com a entrada de bit.
        • Retorna a lista com a codificação manchester.

        Parâmetro:
        • dado (bytes): Um quadro da camada de enlace.

        Retorna:
        • list[int]: Lista com o sinal Manchester.

        Exemplo:
            Entrada b"A" → bits "0101001"
            Saída → [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0]
        """
        bits_str = Utils.byte_formarter(dado).replace(' ', '')
        clock = '01' * len(bits_str)
        sinal = []
        for bit in range(0,len(bits_str)):
           bit1 = int(bits_str[bit]) ^ int(clock[2*bit])
           bit2 = int(bits_str[bit]) ^ int(clock[(2*bit) + 1]) 
           sinal.append(bit1)
           sinal.append(bit2)
        return sinal


    @staticmethod
    def decodificar_manchester(sinal_digital:list) -> bytes:
        """
        Decodifica um sinal codificado em Manchester, recuperando os bytes originais.

        Dinâmica da decodificação:
            • Cada bit original foi convertido em 2 bits no sinal:
                - '10' → bit original 1
                - '01' → bit original 0
            • Percorre o sinal de 2 em 2 bits para reconstruir os bits originais.
            • Converte os bits em bytes.

        Parâmetro:
        • sinal (list[int]): Lista com o sinal codificado Manchester.

        Retorna:
        • bytes: Dados decodificados.
        """
        bits_recuperados = ''
        for i in range(0, len(sinal_digital), 2):
            par = sinal_digital[i:i+2]
            if par == [1, 0]:
                bits_recuperados += '1'
            elif par == [0, 1]:
                bits_recuperados += '0'
            else:
                raise ValueError(f"Sinal Manchester inválido no par: {par}")

        # Agrupa os bits em bytes (8 bits por byte)
        bytes_recuperados = bytes(
            int(bits_recuperados[i:i+8], 2) 
            for i in range(0, len(bits_recuperados), 8)
        )
        return bytes_recuperados


    @staticmethod
    def codificar_bipolar(quadro:bytes) -> list:
        """
        Transforma uma sequência de bytes em um sinal codificado no formato bipolar AMI (Alternate Mark Inversion).

        Dinâmica da codificação:
            • Bit 0 → 0
            • Bit 1 → +1 ou -1

        Parâmetro:
        • quadro (bytes): Um quadro da camada de enlace.

        Retorna:
        • list[int]: Lista com o sinal bipolar.

        Exemplo:
            Entrada: b"A" → bits "0101001" → [0, 1, 0, 1, 0, 0, 1]
            Saída: [0, 1, 0, -1, 0, 0, 1]
        """
        bits_str = Utils.byte_formarter(quadro).replace(' ', '')
        sinal = []
        polaridade = 1

        for bit in bits_str:
            if bit == '1':
                sinal.append(polaridade)
                polaridade *= -1
            else:
                sinal.append(0)
        return sinal


    @staticmethod
    def decodificar_bipolar(sinal: list) -> bytes:
        """
        Transforma um sinal codificado em bipolar de volta em bytes.

        Dinâmica da decodificação:
            • Valor  0 → bit 0
            • Valor +1 ou -1 → bit 1

        Parâmetro:
        • sinal (list[int]): Lista com o sinal codificado em bipolar.

        Retorna:
        • bytes: Dados decodificados a partir do sinal.

        Exemplo:
            Entrada: [1, 0, -1, 0, 1, 0, -1, 0]
            Saída: '10101010'
        """
        # Tratamento pra ruído: caso algum valor não seja -1, 0 ou 1
        if (any(v not in (1, 0, -1) for v in sinal)):
            buffer = []
            for v in sinal:
                # Entende valores em ]-0.5V,0.5V[ como 0
                if (v > -0.5 and v < 0.5):
                    buffer.append(-1)
                # Entende valores <= -0.5V como -1
                elif (v <= -0.5):
                    buffer.append(-1)
                # Entende valores >= 0.5V como 1
                else:
                    buffer.append(1)
            # Atualiza sinal digital pra decodificar após ajuste
            sinal = buffer
        
        # Constrói a sequência de bits
        bits = ''.join('1' if valor != 0 else '0' for valor in sinal)

        # Agrupa em blocos
        blocos = [bits[i:i+8] for i in range(0, len(bits), 8)]

        # Converte os blocos para bytes
        return bytes(int(bloco, 2) for bloco in blocos)

    @staticmethod
    def modular_fsk(quadro: bytes, f0=2, f1=5, amostras_por_bit=100, fs=800) -> list:
        """
        Modula um quadro usando FSK (Frequency Shift Keying).
        
        Parâmetros:
        • quadro (bytes): Um quadro da camada de enlace.
        • f0: frequência para bit 0 (em Hz).
        • f1: frequência para bit 1 (em Hz).
        • amostras_por_bit: número de amostras (pontos no gráfico) por bit.
        • fs: frequência de amostragem (em Hz).

        Retorna:
        • Lista com o sinal FSK modulado (amostrado).
        """
        bits_str = Utils.byte_formarter(quadro).replace(" ", "") # String de bits (ex: "00101...")

        dt = 1 / fs  # Tempo entre amostras
        fase = 0     # Fase acumulada
        sinal_modulado = []

        for bit in bits_str:
            freq = f1 if int(bit) == 1 else f0
            for _ in range(amostras_por_bit):
                fase += 2 * np.pi * freq * dt
                sinal_modulado.append(np.sin(fase))

        return sinal_modulado

    @staticmethod
    def modular_ask(quadro: bytes, amostras_por_bit: int = 100, fs: int = 800) -> list:
        """
        Gera um sinal modulado em ASK (Amplitude Shift Keying) com ciclo completo por bit.
        
        Parâmetros:
        • quadro (bytes): Um quadro da camada de enlace.
        • amostras_por_bit: número de amostras (pontos no gráfico) por bit.
        • freq (float): Frequência da portadora em Hz. Se None, será calculada para 1 ciclo/bit (default=None).
        • fs: frequência de amostragem (em Hz).
        
        Retorna:
        • list: Sinal modulado em ASK
        """
        bit_str = Utils.byte_formarter(quadro).replace(" ","") # String de bits (ex: "00101...")

        # Calcula frequência padrão para 1 ciclo completo por bit
        freq = fs / amostras_por_bit
        
        dt = 1 / fs  # Período de amostragem
        tempo_acumulado = 0  # Mantém o tempo contínuo
        sinal_modulado = []
        
        for bit in bit_str:
            for _ in range(amostras_por_bit):
                if int(bit) == 1:
                    fase = 2 * np.pi * freq * tempo_acumulado # Amplitude =/= zero
                    sinal_modulado.append(np.sin(fase))
                else:
                    sinal_modulado.append(0) # Amplitude zero
                    
                tempo_acumulado += dt  # Atualiza o tempo
                
        return sinal_modulado
    
    @staticmethod
    def modular_8qam(quadro: bytes, amostras_por_simbolo: int = 100, fs: int = 800) -> list:
        """
        Gera um sinal modulado em 8-QAM com ciclo(s) completo(s) por símbolo.
        
        • Cada grupo de 3 bits representa um símbolo (I, Q).
        
        Parâmetros:
        • quadro (bytes): Quadro da camada de enlace.
        • amostras_por_simbolo (int): Número de amostras por símbolo.
        • fs (int): Frequência de amostragem (Hz).
        
        Retorna:
        • list: Sinal modulado 8-QAM (lista de pontos no tempo)
        """
        # Tabela de mapeamento da constelação 8-QAM
        rangeMap = {
            '000': (-1, -1),
            '001': (-1, 0),
            '010': (-1, 1),
            '011': (0, -1),
            '100': (0, 1),
            '101': (1, -1),
            '110': (1, 0),
            '111': (1, 1)
        }

        # Converte quadro em string de bits
        bits_str = Utils.byte_formarter(quadro).replace(" ", "")
        
        # Faz padding pra múltiplo de 3
        padding = (3 - len(bits_str) % 3) % 3
        bits_str += '0' * padding

        # Calcula frequência padrão para 1 ciclo por símbolo
        freq = fs / amostras_por_simbolo
        
        dt = 1 / fs  # Período de amostragem
        tempo_acumulado = 0
        sinal_modulado = []

        # Modula cada símbolo
        for i in range(0, len(bits_str), 3):
            bits = bits_str[i:i+3]
            I, Q = rangeMap.get(bits, (0, 0))
            
            for _ in range(amostras_por_simbolo):
                fase = 2 * np.pi * freq * tempo_acumulado
                s = I * np.cos(fase) + Q * np.sin(fase)
                sinal_modulado.append(s)
                tempo_acumulado += dt

        return sinal_modulado
