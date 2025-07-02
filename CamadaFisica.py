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
            print("Falta implementar")
        return decoded_msg # Codificação não especificada


    def modulador(tipo, dado):
        modulated_msg = ''
        if(tipo == "FSK"):
            return CamadaFisica.modular_fsk(dado)
        elif(tipo == "ASK"):
            print("Falta implementar")
        elif(tipo == "8-QAM"):
            print("Falta implementar")
        
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
        Comentário...
        """
        pass


    def decodificar_bipolar(sinal_digital:list) -> bytes:
        """
        Comentário...
        """
        pass


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


    def modular_ask(sinal_digital:list) -> list:
        """
        Comentário...
        """
        pass


    def modular_8qam(sinal_digital:list) -> list:

        """
        Comentário...
        """
        pass
