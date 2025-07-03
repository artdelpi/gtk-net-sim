import Utils

class Enlace:
    def enquadramento(tipo:str, dado:bytes) -> bytes:
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


    def desenquadramento(tipo:str, dado:bytes) -> bytes:
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
            return Enlace.desenquadrar_contagem_caracteres(dado)
        elif(tipo == "FLAGS e inserção de bytes ou caracteres"):
           return Enlace.desenquadrar_flag_insercao_byte(dado)
        elif(tipo == "FLAGS Inserção de bits"):
            print("Falta implementar")
        raise ValueError(f"Tipo de enquadramento inválido: {tipo}")


    def aplicar_edc(tipo:str, quadro:bytes, edc:int) -> bytes:
        if tipo == "Bit de paridade par":
            return Enlace.bit_de_paridade_par(quadro)
        elif tipo == "CRC":
            return Enlace.crc(quadro)
        elif tipo == "Hamming":
            return Enlace.hamming(quadro)
        raise ValueError(f"Tipo de EDC inválido: {tipo}")


    def verificar_edc(tipo:str, quadro:bytes, edc:int) -> bytes:
        if tipo == "Bit de paridade par":
            return Enlace.verifica_bit_de_paridade_par(quadro)
        elif tipo == "CRC":
            return Enlace.verifica_crc(quadro)
        elif tipo == "Hamming":
            return Enlace.verifica_hamming(quadro)
        raise ValueError(f"Tipo de EDC inválido: {tipo}")


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


    def enquadrar_flag_insercao_byte(dado:bytes, flag='flag', esc='esc') -> bytes:
        """
        Enquadramento por insercao de bytes.

        Dinâmica:
            Adiciona uma flag no inicio e no final da mensagem. Ex:mensagem -> flag + mensagem + flag
            Caso haja uma flag "acidental" na mensagem, é adicionado um caractere de escape. Ex: mensagem = flagRANTE -> flag + esc + flagRANTE + flag.
            Caso um caractere de escape "acidental", é adicionado um outro caractere de escape antes do esc. Ex: mensagem = escOLA -> flag + esc + escOLA + flag.

        Parâmetros:
        • quadro (bytes): Quadro com o byte de tamanho seguido do payload.
        • flag (string): flag de sinal.
        • esc (string): caracrtere de escape.

        Retorna:
        • bytes: Apenas o payload (dados da camada de aplicação).
        """
        dado = dado.decode("utf-8")
        if flag in dado:
           esc_pos = Utils.findall(esc, dado)
           for pos in range(0, len(esc_pos)):
               offset = len(esc) * pos
               
               dado = dado[:(esc_pos[pos] + offset)] + 'esc' + dado[(esc_pos[pos] + offset):]

           flag_pos = Utils.findall(flag, dado)
           for pos in range(0, len(flag_pos)):
               offset = len(esc) * pos
               dado = dado[:(flag_pos[pos] + offset)] + 'esc' + dado[(flag_pos[pos] + offset):]            
        return (flag + dado + flag).encode()


    def desenquadrar_flag_insercao_byte(quadro: bytes, flag='flag', esc='esc') -> bytes:
        """
        Desenquadramento por insercao de bytes.

        Dinâmica:
            Remove as flags do inicio e do final do quadro.
            Remove os caracteres de escape inseridos, reconstruindo a mensagem original.
            Quando encontra um escape, remove-o e mantém o próximo bloco (seja flag ou escape) como dado.

        Parâmetros:
        • quadro (bytes): Quadro enquadrado a ser processado.
        • flag (string): Flag de sinal utilizada no enquadramento.
        • esc (string): Caractere de escape utilizado no enquadramento.

        Retorna:
        • bytes: Dados originais (payload da camada de aplicação).

        Exceções:
        • ValueError: Se o quadro não tiver formato válido (UTF-8, flags ausentes ou escape incompleto).
        """
        try:
            quadro_str = quadro.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError("Quadro não é UTF-8 válido") from e

        len_flag = len(flag)
        len_quadro = len(quadro_str)

        if len_quadro < 2 * len_flag:
            raise ValueError("Quadro muito curto")

        if not (quadro_str.startswith(flag) and quadro_str.endswith(flag)):
            raise ValueError("Flags de início/fim ausentes")

        # Remove flags externas
        dado_sem_flag = quadro_str[len_flag:len_quadro - len_flag]
        len_esc = len(esc)
        resultado = []
        i = 0
        n = len(dado_sem_flag)

        # Processa o conteúdo removendo escapes
        while i < n:
            # Verifica se há uma ocorrência de escape na posição atual
            if i + len_esc <= n and dado_sem_flag[i:i+len_esc] == esc:
                i += len_esc  # Pula o escape
                if i + len_esc > n:
                    raise ValueError("Escape incompleto")
                # Mantém o próximo bloco (dado original)
                resultado.append(dado_sem_flag[i:i+len_esc])
                i += len_esc
            else:
                # Adiciona caracteres normais
                resultado.append(dado_sem_flag[i])
                i += 1

        return ''.join(resultado).encode("utf-8")


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
        Adiciona o bit de paridade par no final da mensagem (dentro de um byte novo).

        Funcionamento:
           • Saída = Quadro + \x01 (se número ímpar de 1s).
           • Saída = Quadro + \x00 (se número par de 1s).

        Parâmetro:
        • dado (bytes): Quadro sem o bit de paridade par.

        Retorna:
        • bytes: Quadro com o bit de paridade par.

        Exemplo Ímpar:
            Entrada: b's' → 01110011 (Número ímpar de 1s) 
            Saída: 01110011 00000001 (Número par de 1s: acrescenta o bit de paridade 1)

        Exemplo Par:
            Entrada: b's' → 01110010 (Número par de 1s) 
            Saída: 01110010 00000000 (Bit de paridade é zero)
        """
        # Passa o quadro de bytes pra bits e remove espaços
        bits = Utils.byte_formarter(quadro).replace(" ", "")

        # Se o número de bits for ímpar, acrescenta o bit de paridade par
        if (bits.count("1") % 2 != 0):
            return quadro + b"\x01"
        else:
            return quadro + b"\x00"

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

        # Verifica se o número de 1s é ímpar
        if (bits.count("1") % 2 != 0):
            raise ValueError("Erro de paridade! número ímpar de bits 1.")
        
        # Remove o último byte com o bit de paridade
        return quadro[:-1]

    def crc(quadro:bytes, tamanho_do_edc:int) -> bytes:
        pass
