class Enlace:
    def enquadramento(tipo, dado) -> bytes:
        """
        Escolhe e executa algum tipo de enquadramento.

        Parâmetros:
        • tipo (str): Tipo de enquadramento.
        • dado (bytes): Dados da camada de aplicação.

        Retorna:
        • bytes: Quadro enquadrado.
        """
        framed_msg = ''
        if(tipo == "Contagem de caracteres"):
            return Enlace.enquadrar_contagem_caracteres(dado)
        elif(tipo == "FLAGS e inserção de bytes ou caracteres"):
            return Enlace.enquadrar_flag_insercao_byte(dado)
        elif(tipo == "FLAGS Inserção de bits"):
            return Enlace.enquadrar_flag_insercao_bit(dado)
        raise ValueError(f"Tipo de enquadramento inválido: {tipo}")


    def desenquadramento(tipo, dado) -> bytes:
        """
        Escolhe e executa algum tipo de desenquadramento.

        Parâmetros:
        • tipo (str): Tipo de enquadramento.
        • dado (bytes): Quadro enquadrado.

        Retorna:
        • bytes: Dados da camada de aplicação.
        """
        unframed_msg = ''
        if(tipo == "Contagem de caracteres"):
            return CamadaEnlace.desenquadrar_contagem_caracteres(dado)
        elif(tipo == "FLAGS e inserção de bytes ou caracteres"):
            print("Falta implementar")
        elif(tipo == "FLAGS Inserção de bits"):
            print("Falta implementar")
        raise ValueError(f"Tipo de enquadramento inválido: {tipo}")


    def enquadrar_contagem_caracteres(dado:bytes) -> bytes:
        """
        Enquadramento por contagem de caracteres.

        Dinâmica de enquadramento:
            Quadro = Tamanho_do_Payload (1 byte) + Payload            
        
        Funcionamento:
            • Primeiro byte = número de bytes do payload.
            • Depois vêm os próprios dados (payload/carga útil).

        Parâmetro:
        • dado (bytes): Dados da camada de aplicação a serem enquadrados.

        Retorna:
        • bytes: Quadro enquadrado.

        Exemplo:
            Entrada: b'teste' → 5 bytes
            Saída: b'\x05teste' → 6 bytes
        """
        tamanho = len(dado) # Tamanho do Payload
        tamanho_byte = tamanho.to_bytes(1, byteorder='big') # Int → Bytes
        quadro = tamanho_byte + dado # Quadro = Tamanho_do_Payload + Payload
        return quadro


    def desenquadrar_contagem_caracteres(quadro:bytes) -> bytes:
        """
        Desfaz o enquadramento por contagem de caracteres.

        Dinâmica:
            Remove o primeiro byte (que indica o tamanho do payload) e retorna o restante.

        Parâmetros:
        • quadro (bytes): Quadro com o byte de tamanho seguido do payload.

        Retorna:
        • bytes: Apenas o payload (dados da camada de aplicação).
        """
        return quadro[1:] # Remove primeiro byte


    def enquadrar_flag_insercao_byte(dado:bytes) -> bytes:
        """
        Comentário...
        """
        pass


    def desenquadrar_flag_insercao_byte(quadro:bytes) -> bytes:
        """
        Comentário...
        """
        pass


    def enquadrar_flag_insercao_bit(dado:bytes) -> bytes:
        """
        Enquadra os dados usando a técnica de bit stuffing com flag 0x7E (01111110).

        Dinâmica:
            Insere um 0 após 5 bits 1 consecutivos para evitar sequência de flag.
            Garante que o byte 0x7E nunca apareça dentro do quadro, somente nas extremidades.

        Parâmetro:
        dados (bytes): Conteúdo da carga útil.

        Retorna:
        bytes: Quadro enquadrado com flags e bit stuffing aplicado.
        """
        FLAG = b'\x7E' # Delimitador padrão usado do protocolo HDLC (01111110)

        # Converte os dados em string de bits
        bit_str = ''.join(f'{byte:08b}' for byte in dado)

        bits_preenchidos = []  # Lista para armazenar os bits com stuffing
        cont_1bit = 0  # Contador de bits 1 consecutivos

        # Percorre cada bit da mensagem original
        for bit in bit_str:
            if bit == '1':
                cont_1bit += 1
            else:
                cont_1bit = 0  # Reinicia o contador se for 0

            bits_preenchidos.append(bit)

            # Se já houver 5 bits 1 consecutivos, insere um bit 0
            if cont_1bit == 5:
                bits_preenchidos.append('0')
                cont_1bit = 0  # Reinicia após inserção

        # Garante que a quantidade total de bits seja múltipla de 8
        while len(bits_preenchidos) % 8 != 0:
            bits_preenchidos.append('0')

        # Agrupa os bits de 8 em 8 e converte para bytes
        bytes_preenchidos = bytes(
            int(''.join(bits_preenchidos[i:i+8]), 2)
            for i in range(0, len(bits_preenchidos), 8)
        )
        # Adiciona FLAG 0x7E no início e no final
        return FLAG + bytes_preenchidos + FLAG
    

    def desenquadrar_flag_insercao_bit(quadro:bytes) -> bytes:
        pass
    
    
    def hamming(dado: bytes) -> bytes:
        """
        Codifica os dados usando o código de Hamming (7,4).

        Parâmetros:
        • data (bytes): Dados de entrada a serem codificados, byte a byte.

        Retorna:
        • bytes: Dados codificados com código Hamming (7,4)
        """
        def calcular_bits_paridade(bits_dados: list) -> tuple:
            """
            Calcula os 3 bits de paridade com base em 4 bits de dados.

            Fórmulas usadas no Hamming(7,4):
                p1 = d1 ⊕ d2 ⊕ d4
                p2 = d1 ⊕ d3 ⊕ d4
                p3 = d2 ⊕ d3 ⊕ d4
            
            Parâmetros:
            • bits_dados (List[int]): Lista de 4 bits, representando os bits de dados.

            Retorna:
            • Tuple[int, int, int]: Tupla com os três bits de paridade (p1, p2, p3).
            """
            p1 = bits_dados[0] ^ bits_dados[1] ^ bits_dados[3]
            p2 = bits_dados[0] ^ bits_dados[2] ^ bits_dados[3]
            p3 = bits_dados[1] ^ bits_dados[2] ^ bits_dados[3]
            return p1, p2, p3

        codificacao_bytes = [] # Lista que vai armazenar os bytes codificados

        for byte in dado:
            # Divide o byte em dois nibbles
            nibbles = [(byte >> 4) & 0b1111, byte & 0b1111]

            for nibble in nibbles:
                # Converte o nibble em uma lista de bits [d1, d2, d3, d4]
                bits_dados = [(nibble >> j) & 1 for j in range(3, -1, -1)]

                # Calcula os bits de paridade p1, p2, p3
                p1, p2, p3 = calcular_bits_paridade(bits_dados)

                # Organiza os bits no formato [p1, p2, d1, p3, d2, d3, d4]
                bloco_hamming = [
                    p1,
                    p2,
                    bits_dados[0],
                    p3,
                    bits_dados[1],
                    bits_dados[2],
                    bits_dados[3]
                ]

                byte_codificado = 0
                for i, bit in enumerate(bloco_hamming):
                    byte_codificado |= bit << (6 - i) # Alinha o bit na posição certa

                # Adiciona o byte codificado à lista
                codificacao_bytes.append(byte_codificado)

        # Converte a lista para bytes e retorna
        return bytes(codificacao_bytes)

        
    def bit_de_paridade_par(quadro:bytes) -> bytes:
        """
        Força o quadro a ter número par de 1s, através do bit de paridade par.
        Se o receptor captar um número ímpar de 1s, então houve erro e o receptor detecta.

        Funcionamento:
           • Saída = Quadro ++ 1 (se número ímpar de 1s).
           • Saída = Quadro ++ 0 (se número de 1s já for par).

        Parâmetro:
        • dado (bytes): Quadro sem o bit de paridade par.

        Retorna:
        • bytes: Quadro com o bit de paridade par.

        Exemplo Ímpar:
            Entrada: b's' → 01110011 (Número ímpar de 1s) 
            Saída: 011100111 (Número par de 1s: acrescenta o bit de paridade 1)

        Exemplo Par:
            Entrada: b's' → 01110010 (Número par de 1s) 
            Saída: 011100100 (Acrescenta o bit de paridade 0)
        """
        # Passa o quadro de bytes pra bits e remove espaços
        bits = Utils.byte_formarter(quadro).replace(" ", "")
        
        # Se o número de bits for ímpar, acrescenta o bit de paridade par
        if (bits.count("1") % 2 != 0):
            bits_com_paridade = bits + "1"
        else:
            bits_com_paridade = bits + "0" # Já tem número par de 1s

        # Converte para inteiro e depois para bytes
        return int(bits_com_paridade, 2).to_bytes((len(bits)+7)//8, "big")


    def verifica_bit_de_paridade_par(quadro:bytes) -> bytes:
        """
        Detecta erro se o número de bits 1 é ímpar e remove o bit de paridade.

        Parâmetro:
        • dado (bytes): Quadro com o bit de paridade par.

        Retorna:
        • bytes: Quadro sem o bit de paridade par.
        • ValueError: Detecção de erro se o número de 1s for ímpar.

        Exemplo:
            Entrada: b's' → 01110011 (Número ímpar de 1s) 
            Saída: ValueError: "Erro de paridade! número ímpar de bits 1."
        """
        # Passa o quadro de bytes pra bits e remove espaços
        bits = Utils.byte_formarter(quadro).replace(" ", "")

        if (bits.count("1") % 2 != 0):
            raise ValueError("Erro de paridade! número ímpar de bits 1.")
        
        bits_sem_paridade = bits[:-1] # Remove o último bit (bit de paridade, 1 ou 0)

        # Converte para inteiro e depois para bytes
        return int(bits_sem_paridade, 2).to_bytes((len(bits_sem_paridade)+7)//8, "big")


    def crc():
        pass
