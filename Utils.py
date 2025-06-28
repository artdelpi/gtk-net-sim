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
            x = np.arange(len(data))
            largura = max(6, len(data) * 300)
            altura = 2.5
            fig, ax = plt.subplots(figsize=(largura, altura))
            ax.step(x, data, where='post', color='r', linewidth=2.5)
            ax.set_ylim((min(data) - 0.1), 1.1)  
            ax.set_yticks([min(data), 1])
            ax.set_title(title)
            ax.grid(True, linestyle='--', alpha=0.6)
            # Marca um tick por bit
            num_bits = len(data)
            tick_positions = list(range(num_bits))
            tick_labels = [str(i) for i in range(num_bits)]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels)
            ax.tick_params(axis='x', labelsize=6)
            ax.set_xlabel("T (Tempo de Bit)")
            fig.subplots_adjust(bottom=0.2)  # Espaço entre os gráficos
            return fig
        elif signal_type == 'sinal_analogico':
            x = np.arange(len(data))
            largura = max(6, len(data) // 300)
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