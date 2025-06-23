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


def graph_generator(data, title):
    """
    Gera um gráfico a partir de um array de inteiros e um título.
    
    Args:
        array: Lista de inteiros para plotar.
        titulo: Título do gráfico.
    
    Returns:
        Figure: Objeto Figure do matplotlib contendo o gráfico.
    """
    if data:
        x = np.arange(len(data))
        fig, ax = plt.subplots(figsize=(max(6, (len(data) * 0.8)), 4))
        ax.step(x, data, where='post', color='r', linewidth=2.5)
        ax.set_ylim((min(data) - 0.1), 1.1)  
        ax.set_yticks([min(data), 1])
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        return fig