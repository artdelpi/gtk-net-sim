import Utils

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
   
   
    def modulador(tipo, dado):
        modulated_msg = ''
        if(tipo == "FSK"):
            print(tipo)
        elif(tipo == "ASK"):
            print(tipo)
        elif(tipo == "8-QAM"):
            print(tipo)
        
        return modulated_msg
    

    def codificar_nrz_polar(dado: bytes) -> list[int]:
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
            Entrada b"A" → bits "01000001"
            Saída → [-1, 1, -1, -1, -1, -1, 1, -1]
        """
        # Transforma bytes em string de bits e remove espaços
        bits_str = Utils.byte_formarter(dado).replace(' ', '')

        # Faz o mapeamento 0 → -1 e 1 → +1
        sinal = [1 if bit == '1' else -1 for bit in bits_str]
        return sinal


    def codificar_manchester(dado:bytes) -> list[int]:
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
        • Para cada par de bit do clock, faz o XOR com a entrada de bit
        • Retorna a lista com a codificação manchester

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

             


    def codificar_bipolar(dado:bytes) -> list[int]:
        """
        Comentário...
        """
        pass


    def modular_fsk(sinal_digital:list) -> list:
        """
        Comentário...
        """
        pass


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