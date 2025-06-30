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
        
        return framed_msg


    def desenquadramento(tipo, dado) -> bytes:
        unframed_msg = ''
        if(tipo == "Contagem de caracteres"):
            print("Falta implementar")
        elif(tipo == "FLAGS e inserção de bytes ou caracteres"):
            print("Falta implementar")
        elif(tipo == "FLAGS Inserção de bits"):
            print("Falta implementar")
        
        return unframed_msg


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
        Comentário...
        """
        pass


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
        Comentário...
        """
        pass
    

    def desenquadrar_flag_insercao_bit(quadro:bytes) -> bytes:
        """
        Comentário...
        """
        pass
        

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


    def hamming():
        pass