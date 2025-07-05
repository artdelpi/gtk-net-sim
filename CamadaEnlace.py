import Utils

class Enlace:
    @staticmethod
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

    @staticmethod
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
            return Enlace.desenquadrar_flag_insercao_bit(dado)
        raise ValueError(f"Tipo de enquadramento inválido: {tipo}")

    @staticmethod
    def aplicar_edc(tipo:str, quadro:bytes, edc:int) -> bytes:
        if tipo == "Bit de paridade par":
            return Enlace.bit_de_paridade_par(quadro)
        elif tipo == "CRC":
            return Enlace.crc(quadro, edc)
        elif tipo == "Hamming":
            return Enlace.hamming(quadro)
        raise ValueError(f"Tipo de EDC inválido: {tipo}")

   
    @staticmethod
    def verificar_edc(tipo:str, quadro:bytes, edc:int) -> bytes:
        if tipo == "Bit de paridade par":
            return Enlace.verifica_bit_de_paridade_par(quadro)
        elif tipo == "CRC":
            return Enlace.verifica_crc(quadro, edc)
        elif tipo == "Hamming":
            return Enlace.verifica_hamming(quadro)
        raise ValueError(f"Tipo de EDC inválido: {tipo}")

    
    @staticmethod
    def enquadrar_contagem_caracteres(dado:bytes) -> bytes:
        """
        Enquadramento por contagem de caracteres.

        Dinâmica de enquadramento:
            Quadro = Byte do tamanho do quadro + Payload            
        
        Funcionamento:
            • Primeiro byte = Tamanho_do_quadro (Tamanho do payload + 1 byte do cabeçalho)
            • Depois vêm os próprios dados (payload/carga útil).

        Parâmetro:
        • dado (bytes): Dados da camada de aplicação a serem enquadrados.

        Retorna:
        • bytes: Quadro enquadrado.

        Exemplo:
            Entrada: b'teste' → 5 bytes
            Saída: b'\x06teste' → 6 bytes
        """
        tamanho = len(dado) + 1 # Tamanho do quadro
        tamanho_byte = tamanho.to_bytes(1, byteorder='big') # Int → Bytes
        quadro = tamanho_byte + dado # Quadro = Tamanho_do_Quadro + Payload
        return quadro

    @staticmethod
    def desenquadrar_contagem_caracteres(quadro:bytes) -> bytes:
        """
        Desfaz o enquadramento por contagem de caracteres.

        Dinâmica:
            Remove o primeiro byte (que indica o tamanho do quadro) e retorna o restante.

        Parâmetros:
        • quadro (bytes): Quadro com o byte de tamanho seguido do payload.

        Retorna:
        • bytes: Apenas o payload (dados da camada de aplicação).
        """
        return quadro[1:] # Remove primeiro byte

    @staticmethod
    def enquadrar_flag_insercao_byte(dado:bytes, flag=b'\x7E', esc=b'\x7D') -> bytes:
        """
        Enquadramento por insercao de bytes.

        Dinâmica:
            Adiciona uma flag no inicio e no final da mensagem. Ex:mensagem -> flag + mensagem + flag
            Caso haja uma flag "acidental" na mensagem, é adicionado um caractere de escape. Ex: mensagem = flagRANTE -> flag + esc + flagRANTE + flag.
            Caso um caractere de escape "acidental", é adicionado um outro caractere de escape antes do esc. Ex: mensagem = escOLA -> flag + esc + escOLA + flag.

        Parâmetros:
        • quadro (bytes): Quadro com o byte de tamanho seguido do payload.
        • flag (bytes): Flag de sinal.
        • esc (bytes): caractere de escape.

        Retorna:
        • bytes: Apenas o payload (dados da camada de aplicação).
        """
        if flag in dado:
           esc_pos = Utils.findall(esc, dado)
           for pos in range(0, len(esc_pos)):
               offset = len(esc) * pos
               
               dado = dado[:(esc_pos[pos] + offset)] + esc + dado[(esc_pos[pos] + offset):]

           flag_pos = Utils.findall(flag, dado)
           for pos in range(0, len(flag_pos)):
               offset = len(esc) * pos
               dado = dado[:(flag_pos[pos] + offset)] + esc + dado[(flag_pos[pos] + offset):]            
        return (flag + dado + flag)

    @staticmethod
    def desenquadrar_flag_insercao_byte(quadro: bytes, flag=b'\x7E', esc='\x7D') -> bytes:
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

        if not (quadro.startswith(flag) and quadro.endswith(flag)):
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

    @staticmethod
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
    
    @staticmethod
    def desenquadrar_flag_insercao_bit(quadro:bytes) -> bytes:
        """
        Desfaz o enquadramento por inserção de bits (bit stuffing) com FLAG 0x7E.

        Parâmetro:
        quadro (bytes): Quadro recebido com flags e bit stuffing aplicado.

        Retorna:
        bytes: Dados originais (sem bit stuffing e sem flag).
        """
        FLAG = b'\x7E'  # FLAG padrão (01111110)

        # Remove as flags externas (primeiro e último byte)
        if quadro[0:1] != FLAG or quadro[-1:] != FLAG:
            raise ValueError("FLAG de delimitação ausente no quadro")
        quadro = quadro[1:-1]  # Remove as flags

        # Converte o quadro (ainda com bit stuffing) para string de bits
        bit_str = ''.join(f'{byte:08b}' for byte in quadro)

        # Remove o stuffing: elimina o 0 inserido após cinco 1 consecutivos
        bits_desenquadrados = []
        cont_1bit = 0
        i = 0
        while i < len(bit_str):
            bit = bit_str[i]
            bits_desenquadrados.append(bit)
            if bit == '1':
                cont_1bit += 1
                if cont_1bit == 5:
                    i += 1  # Pula o bit 0 inserido (stuffed bit)
                    cont_1bit = 0
            else:
                cont_1bit = 0
            i += 1

        # Remove bits adicionais adicionados para alinhamento (zero padding)
        while len(bits_desenquadrados) % 8 != 0:
            bits_desenquadrados.pop()

        # Converte os bits de volta para bytes
        dados = bytes(
            int(''.join(bits_desenquadrados[i:i+8]), 2)
            for i in range(0, len(bits_desenquadrados), 8)
        )
        return dados
        
    @staticmethod
    def hamming(dado: bytes) -> bytes:
        """
        Codifica os dados usando o código de Hamming (7,4).

        Parâmetros:
        • data (bytes): Dados de entrada a serem codificados, byte a byte.

        Retorna:
        • bytes: Dados codificados com código Hamming (7,4)
        """
        def calcular_bits_paridade(bits_dados: list) -> tuple:
            p1 = bits_dados[0] ^ bits_dados[1] ^ bits_dados[3]  # p1 = d1 ⊕ d2 ⊕ d4
            p2 = bits_dados[0] ^ bits_dados[2] ^ bits_dados[3]  # p2 = d1 ⊕ d3 ⊕ d4
            p3 = bits_dados[1] ^ bits_dados[2] ^ bits_dados[3]  # p3 = d2 ⊕ d3 ⊕ d4
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

                # Converte os 7 bits para um byte (bit mais significativo não usado)
                byte_codificado = 0
                for i, bit in enumerate(bloco_hamming):
                    byte_codificado |= bit << (6 - i) # Alinha o bit na posição certa

                # Adiciona o byte codificado à lista
                codificacao_bytes.append(byte_codificado)

        # Converte a lista para bytes e retorna
        return bytes(codificacao_bytes)

    @staticmethod
    def verifica_hamming(quadro: bytes) -> bytes:
        """
        Verifica e corrige os dados codificados com o código de Hamming (7,4).

        Parâmetros:
            quadro (bytes): Dados codificados com Hamming (7,4).

        Retorna:
            bytes: Dados corrigidos e decodificados (sem bits de paridade).
        """
        dados_decodificados = []

        for byte in quadro:
            # Obtém os bits do byte codificado (7 bits úteis)
            bits = [(byte >> (6 - i)) & 1 for i in range(7)]

            # Bits de paridade e dados:
            p1, p2, d1, p3, d2, d3, d4 = bits

            # Calcula os bits de paridade esperados
            s1 = p1 ^ d1 ^ d2 ^ d4
            s2 = p2 ^ d1 ^ d3 ^ d4
            s3 = p3 ^ d2 ^ d3 ^ d4

            # Síndrome (posição do erro)
            erro_pos = (s3 << 2) | (s2 << 1) | s1

            # Corrige o erro se for em bit de dado (posições 3,5,6,7)
            if erro_pos in {3, 5, 6, 7}:
                bits[erro_pos - 1] ^= 1  # Inverte o bit errado
                # Atualiza os bits após correção
                p1, p2, d1, p3, d2, d3, d4 = bits

            # Reconstrói o nibble (4 bits de dados)
            nibble = (d1 << 3) | (d2 << 2) | (d3 << 1) | d4
            dados_decodificados.append(nibble)

        # Combina nibbles para formar bytes originais
        bytes_decodificados = bytearray()
        for i in range(0, len(dados_decodificados), 2):
            if i + 1 < len(dados_decodificados):
                byte = (dados_decodificados[i] << 4) | dados_decodificados[i + 1]
            else:
                byte = dados_decodificados[i] << 4  # Último nibble (preenche com 0)
            bytes_decodificados.append(byte)

        return bytes(bytes_decodificados)

    @staticmethod
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

    @staticmethod
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
    
    @staticmethod
    def crc(quadro: bytes, tamanho_do_edc: int = 8, polinomio: int = 0x07) -> bytes:
        """
        Aplica o código CRC no quadro, suportando tamanho de CRC variável (ex.: 8, 16, 32 bits).

        Parâmetros:
        • quadro (bytes): Quadro de entrada (sem CRC).
        • polinomio (int): Polinômio gerador do CRC (padrão: 0x07).
        • tamanho_do_edc (int): Quantidade de bits do CRC (ex.: 8, 16, 32).

        Retorna:
        • bytes: Quadro com o CRC no final (em bytes).
        """
        crc = 0
        for byte in quadro:
            crc ^= byte
            for _ in range(8):
                # Verifica o bit mais significativo (posição depende do tamanho do CRC)
                if crc & (1 << (tamanho_do_edc - 1)):
                    crc = (crc << 1) ^ polinomio
                else:
                    crc <<= 1
                # Mantém o CRC com o tamanho correto (ex.: 8 bits → 0xFF, 16 bits → 0xFFFF)
                crc &= (1 << tamanho_do_edc) - 1

        # Calcula quantos bytes o CRC precisa para ser armazenado
        num_bytes_crc = (tamanho_do_edc + 7) // 8
        crc_bytes = crc.to_bytes(num_bytes_crc, byteorder='big')

        return quadro + crc_bytes


    @staticmethod
    def verifica_crc(quadro: bytes, tamanho_do_edc: int = 8, polinomio: int = 0x07) -> bytes:
        """
        Verifica o CRC de tamanho variável no quadro (ex.: CRC-8, CRC-16, CRC-32).

        Parâmetros:
        • quadro (bytes): Quadro com o CRC no final.
        • polinomio (int): Polinômio gerador do CRC.
        • tamanho_do_edc (int): Quantidade de bits do CRC (ex.: 8, 16, 32).

        Retorna:
        • bytes: Quadro original sem o CRC (se válido).

        Exceção:
        • ValueError: Se o CRC for inválido.
        """
        num_bytes_crc = (tamanho_do_edc + 7) // 8  # Quantos bytes o CRC ocupa
        crc = 0

        # Processa todos os bytes do quadro (incluindo o CRC no final)
        for byte in quadro:
            crc ^= byte
            for _ in range(8):
                if crc & (1 << (tamanho_do_edc - 1)):
                    crc = (crc << 1) ^ polinomio
                else:
                    crc <<= 1
                crc &= (1 << tamanho_do_edc) - 1  # Mantém o CRC com o tamanho correto

        if crc != 0:
            raise ValueError("Erro de CRC detectado!")

        # Se CRC for válido, remove os bytes do CRC e retorna o quadro original
        return quadro[:-num_bytes_crc]
