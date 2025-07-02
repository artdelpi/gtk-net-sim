import Utils
import numpy as np

class CamadaFisica:
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
        return encoded_msg # Codificação não especificada
   
   
    def decodificador_banda_base(tipo, dado):
        decoded_msg = ''
        if(tipo == "NRZ-Polar"):
            return CamadaFisica.decodificar_nrz_polar(dado)
        elif(tipo == "Manchester"):
            print("Falta implementar")
        elif(tipo == "Bipolar"):
            return CamadaFisica.decodificar_bipolar(dado)
        return decoded_msg # Codificação não especificada


    def modulador(tipo, dado):
        modulated_msg = ''
        if(tipo == "FSK"):
            return CamadaFisica.modular_fsk(dado)
        elif(tipo == "ASK"):
             return CamadaFisica.modular_ask(dado)
        elif(tipo == "8-QAM"):
            return CamadaFisica.modular_8qam(dado)
        
        return modulated_msg
    

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
        # Desfaz o mapeamento da NRZ-Polar numa string dos bits
        bits_str = "".join(["1" if v == 1 else "0" for v in sinal_digital])

        # Toma o quadro em inteiro na base 2 pra aplicar o to_bytes()
        quadro_bits = int(bits_str, 2)

        # Calcula o número de bytes
        num_bytes = (len(bits_str)+7)//8 

        # Obtém o quadro original, em bytes
        quadro = quadro_bits.to_bytes(num_bytes, "big")
        return quadro


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
        print(clock)
        sinal = []
        for bit in range(0,len(bits_str)):
           bit1 = int(bits_str[bit]) ^ int(clock[2*bit])
           bit2 = int(bits_str[bit]) ^ int(clock[(2*bit) + 1]) 
           sinal.append(bit1)
           sinal.append(bit2)
        print(sinal)
        return sinal


    def decodificar_manchester(sinal_digital:list) -> bytes:
        """
        Comentário...
        """
        pass


    def codificar_bipolar(dado:bytes) -> list:
        """
        Transforma uma sequência de bytes em um sinal codificado no formato bipolar AMI (Alternate Mark Inversion).

        Dinâmica da codificação:
            • Bit 0 → 0
            • Bit 1 → +1 ou -1

        Parâmetro:
        • dado (bytes): Um quadro da camada de enlace.

        Retorna:
        • list[int]: Lista com o sinal bipolar.

        Exemplo:
            Entrada: b"A" → bits "0101001"
            Saída: [0, 1, 0, -1, 0, 0, 1]
        """
        bits_str = Utils.byte_formarter(dado).replace(' ', '')
        sinal = []
        polaridade = 1

        for bit in bits_str:
            if bit == '1':
                sinal.append(polaridade)
                polaridade *= -1
            else:
                sinal.append(0)
        return sinal


    def decodificar_bipolar(sinal: list[int]) -> bytes:
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
            Saída:    '10101010'
        """
        # Constrói a sequência de bits
        bits = ''.join('1' if valor != 0 else '0' for valor in sinal)

        # Agrupa em blocos
        blocos = [bits[i:i+8] for i in range(0, len(bits), 8)]

        # Converte os blocos para bytes
        return bytes(int(bloco, 2) for bloco in blocos)



    def modular_fsk(sinal_digital: list, f0=2, f1=5, amostras_por_bit=100, fs=800) -> list:
        """
        Modula um sinal digital usando FSK (Frequency Shift Keying).
        
        Parâmetros:
        • sinal_digital: lista com bits (0s e 1s).
        • f0: frequência para bit 0 (em Hz).
        • f1: frequência para bit 1 (em Hz).
        • amostras_por_bit: número de amostras (pontos no gráfico) por bit.
        • fs: frequência de amostragem (em Hz).

        Retorna:
        • Lista com o sinal FSK modulado (amostrado).
        """
        dt = 1 / fs  # Tempo entre amostras
        fase = 0     # Fase acumulada
        sinal_modulado = []

        for bit in sinal_digital:
            freq = f1 if bit == 1 else f0
            for _ in range(amostras_por_bit):
                fase += 2 * np.pi * freq * dt
                sinal_modulado.append(np.sin(fase))

        return sinal_modulado


    def demodular_fsk(sinal_modulado, f0=2, f1=5, amostras_por_bit=100, fs=800):
        pass

    def modular_ask(sinal_digital: list, amostras_por_bit: int = 100, fs: int = 800,) -> list:
        """
        Gera um sinal modulado em ASK (Amplitude Shift Keying) com ciclo completo por bit.
        
        Parâmetros:
        sinal_digital (list): Lista de bits (0s e 1s) a ser modulada
        amostras_por_bit (int): Número de amostras por bit (default=100)
        fs (int): Frequência de amostragem em Hz (default=800)
        freq (float): Frequência da portadora em Hz. Se None, será calculada para 1 ciclo/bit (default=None)
        
        Retorna:
        list: Sinal modulado em ASK
        """
        
        # Calcula frequência padrão para 1 ciclo completo por bit
        freq = fs / amostras_por_bit
        
        dt = 1 / fs  # Período de amostragem
        tempo_acumulado = 0  # Mantém o tempo contínuo
        sinal_modulado = []
        
        for bit in sinal_digital:
            for _ in range(amostras_por_bit):
                if bit == 1:
                    fase = 2 * np.pi * freq * tempo_acumulado
                    sinal_modulado.append(np.sin(fase))
                else:
                    sinal_modulado.append(0)
                    
                tempo_acumulado += dt  # Atualiza o tempo
                
        return sinal_modulado
    
    def demodular_ask(sinal_alogico:list) -> list:
        """
        Comentário...
        """
        pass


    def modular_8qam(sinal_digital: list) -> list:
        """
        Modula um sinal digital usando 8-QAM.

        • Cada grupo de 3 bits representa um ponto na constelação (I, Q).
        • O mapeamento é feito com uma tabela fixa:

        Parâmetro:
        • sinal_digital: lista com bits (0s e 1s).

        Retorna:
        • Lista de tuplas (I, Q) representando do sinal modulado.
        """
        
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

        bits_str = ''.join(f'{byte:08b}' for byte in sinal_digital)

        padding = (3 - len(bits_str) % 3) % 3
        bits_str += '0' * padding

        sinal = []

        for i in range(0, len(bits_str), 3):
            bit_trio = bits_str[i:i+3]
            simbolo = rangeMap.get(bit_trio, (0, 0)) 
            sinal.append(simbolo)

        return sinal


    def demodular_8qam(sinal_analogico:list) -> list:
        """
        Comentário...
        """
        pass
