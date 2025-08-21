import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np 

def byte_formarter(bytes_data):
    """
    Transforma bytes em string dos bits correspondentes.

    Parâmetros:
    • bytes_data (bytes): Dados em bytes.

    Retorna:
    • str: String dos bits formatada, com espaço entre os bytes.

    Exemplo:
        Entrada → b'teste'
        Saída  → "01110100 01100101 01110011 01110100 01100101"
    """
    return ' '.join(f"{byte:08b}" for byte in bytes_data)


def graph_generator(data, title, signal_type):
    """
    Gera um gráfico a partir de um array de inteiros e um título.
    
    Args:
        data (list): Lista de inteiros para plotar no gráfico.
        titulo (str): Título do gráfico.
        signal_type (str): Sinal analógico ou digital
    
    Returns:
        Figure: Objeto Figure do matplotlib contendo o gráfico.
    """
    if data:
        if signal_type == "sinal_analogico":
            # ===============
            # SINAL ANALÓGICO
            # ===============
            x = np.arange(len(data))  # Eixo X baseado no número de amostras

            # Define tamanho do gráfico
            max_largura = 100  # Limite máximo de largura (ajuste conforme necessário)
            largura = min(max_largura, max(6, len(data) // 300))  # Escala conforme o tamanho do sinal
            altura = 3  # Altura fixa

            fig, ax = plt.subplots(figsize=(largura, altura))

            # Gera o gráfico de linha
            ax.plot(x, data, linewidth=1.5)

            # Configura o eixo X para mostrar ticks por bit (100 pontos por bit)
            num_bits = len(data) // 100
            tick_positions = [i * 100 for i in range(num_bits + 1)]
            tick_labels = [str(i) for i in range(num_bits + 1)]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels)
            ax.tick_params(axis='x', labelsize=6)

            # Título, labels e grid
            ax.set_title(title)
            x_label = "T (Tempo de Bit)"
            if title == "Sinal Analógico Modulado em (8-QAM)" or title == "Sinal Analógico Recebido em (8-QAM)":
                x_label = "T (Tempo de Símbolo)"
            ax.set_xlabel(x_label)
            ax.set_ylabel("Amplitude")
            ax.grid(True, alpha=0.3)

            fig.tight_layout()
            return fig

        elif signal_type == "sinal_banda_base":
            # ==========================
            # SINAL DIGITAL (BANDA BASE)
            # ==========================
            amostras = 100  # Cada bit será representado por 100 amostras
            data_expandido = np.repeat(data, amostras)
            
            # Cria o eixo X com uma amostra extra no final para manter o degrau no fim
            x = np.arange(len(data_expandido) + 1)
            
            # Define tamanho do gráfico
            largura = max(6, len(data) * 3)  # Largura proporcional ao número de bits
            altura = 6  # Altura fixa

            fig, ax = plt.subplots(figsize=(largura, altura))

            # Extende o sinal para manter o último degrau até o fim
            data_extended = np.append(data_expandido, data_expandido[-1])

            # Gera o gráfico em degraus (sinal digital)
            ax.step(x, data_extended, where='post', color='r', linewidth=2.5)

            # Configura o eixo Y (nível de tensão)
            y_min = min(data)
            y_max = max(data)
            ax.set_ylim(y_min - 0.1, y_max + 0.1)
            num_ticks = 5
            tick_values = np.linspace(y_min, y_max, num_ticks)
            ax.set_yticks(tick_values)

            # Título e grid
            ax.set_title(title)
            ax.grid(True, linestyle='--', alpha=0.6)

            # Configura o eixo X para mostrar ticks por bit
            num_bits = len(data)
            tick_positions = [i * amostras for i in range(num_bits + 1)]
            tick_labels = [str(i) for i in range(num_bits + 1)]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels)
            ax.tick_params(axis='x', labelsize=6)
            ax.set_xlabel("T (Tempo de Bit)")

            # Ajusta o layout do gráfico
            fig.subplots_adjust(bottom=0.2)
            return fig

        else:
            raise ValueError('Tipo de sinal não reconhecido: {signal_type}')
    else:
        raise ValueError('Nenhum dado foi fornecido.')
    
def findall(substring, string):
    """
    Encontra todas as ocorrencias de uma substring na string original
     
    Args:
        substring: substring que deseja ser encotnrada
        string: String original
    
    Returns:
        Lista de com todos os indexs do inicio da substring

    """
    l = []
    i = -1
    while True:
        i = string.find(substring, i+1)
        if i == -1:
            return l
        l.append(string.find(substring, i))

def find_xor(a:str, b:str) -> str:
    """
    Realiza o Xor bit a bit da palavra
     
    Args:
        a: string que será relizada o xor
        b: string que será relizada o xor
    
    Returns:
        String com do resultado do xor bit a bit de a e b 

    """
    n = len(b)
    result = ""
    for i in range(1, n):  # Skip first bit (CRC standard)
        result += '0' if a[i] == b[i] else '1'
    return result
