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
        array: Lista de inteiros para plotar.
        titulo: Título do gráfico.
    
    Returns:
        Figure: Objeto Figure do matplotlib contendo o gráfico.
    """
    if data:
        if signal_type == 'sinal_banda_base':
            amostras = 100 # 100 pontos por bit (nível de tensão)
            data_expandido = np.repeat(data, amostras)
            x = np.arange(len(data_expandido) + 1) 
            largura = max(6, len(data) * 3)  
            altura = 6
            fig, ax = plt.subplots(figsize=(largura, altura))
            data_extended = np.append(data_expandido, data_expandido[-1])  # Mantém o último degrau
            ax.step(x, data_extended, where='post', color='r', linewidth=2.5)
            y_min = min(data)
            y_max = max(data)
            ax.set_ylim(y_min - 0.1, y_max + 0.1)
            num_ticks = 5
            tick_values = np.linspace(y_min, y_max, num_ticks)
            ax.set_yticks(tick_values)
            ax.set_title(title)
            ax.grid(True, linestyle='--', alpha=0.6)
            num_bits = len(data)
            tick_positions = [i * amostras for i in range(num_bits + 1)]
            tick_labels = [str(i) for i in range(num_bits + 1)]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels)
            ax.tick_params(axis='x', labelsize=6)
            ax.set_xlabel("T (Tempo de Bit)")
            fig.subplots_adjust(bottom=0.2)
            return fig

        elif signal_type == 'sinal_analogico':
            x = np.arange(len(data))
            max_largura = 100  # Limite máximo seguro (ajuste se necessário)
            largura = min(max_largura, max(6, len(data) // 300))        
            altura = 3 
            fig, ax = plt.subplots(figsize=(largura, altura))
            ax.plot(x, data, linewidth=1.5)

            num_bits = len(data) // 100
            tick_positions = [i * 100 for i in range(num_bits + 1)] # Cada bit são 100 pontos (amostras)
            tick_labels = [f"{i}" for i in range(num_bits + 1)]

            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels) 
            ax.tick_params(axis='x', labelsize=6)

            ax.set_title(title)
            ax.set_xlabel("T (Tempo de Bit)")
            ax.set_ylabel("Amplitude")
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
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