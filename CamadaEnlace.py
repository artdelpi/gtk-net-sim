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
        