import json
import numpy as np
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import sys

def load_coefficients(json_path):
    with open(json_path, 'r') as f:
        coeffs = json.load(f)
    return coeffs

def animate_epicycles(coeffs, max_coeffs=200, frames=1000, interval=20):
    # --- Separa o componente de frequência 0 (DC Offset) ---
    offset_coeff = None
    for i, c in enumerate(coeffs):
        if c['freq'] == 0:
            offset_coeff = coeffs.pop(i)
            break
    
    # Se não houver componente de offset, começa em (0,0)
    if offset_coeff is None:
        start_x, start_y = 0.0, 0.0
    else:
        # O ponto de partida é o vetor do componente de freq 0
        start_x, start_y = offset_coeff['re'], offset_coeff['im']

    coeffs = coeffs[:max_coeffs]
    
    plt.style.use('dark_background')

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    
    # Define os limites do gráfico com base na soma das amplitudes
    max_radius = sum(c['amp'] for c in coeffs) + np.sqrt(start_x**2 + start_y**2)
    ax.set_xlim(-max_radius * 1.2, max_radius * 1.2)
    ax.set_ylim(-max_radius * 1.2, max_radius * 1.2)
    ax.set_title(f"Série de Fourier com {len(coeffs)} Componentes (Epiciclos)")
    ax.grid(True, linestyle='--', alpha=0.6)

    # Prepara os elementos gráficos para a animação
    circles, lines = [], []
    for _ in coeffs:
        c_line, = ax.plot([], [], 'b-', lw=0.5, alpha=0.5) # Círculos
        r_line, = ax.plot([], [], 'r-', lw=1)             # Vetores (raios)
        circles.append(c_line)
        lines.append(r_line)

    path_line, = ax.plot([], [], 'w-', lw=1.5) # O caminho desenhado em branco 
    path_x, path_y = [], []

    def init():
        for c_line, r_line in zip(circles, lines):
            c_line.set_data([], [])
            r_line.set_data([], [])
        path_line.set_data([], [])
        return circles + lines + [path_line]

    def update(frame):
        t = frame / frames # Tempo normalizado (0 a 1)
        
        # Começa do ponto de offset
        x, y = start_x, start_y
        
        for i, c in enumerate(coeffs):
            prev_x, prev_y = x, y
            
            freq = c['freq']
            amp = c['amp']
            phase = c['phase']
            
            # Calcula a posição da ponta do vetor atual
            angle = 2 * np.pi * freq * t + phase
            x += amp * np.cos(angle)
            y += amp * np.sin(angle)
            
            # Desenha o círculo (epiciclo)
            theta = np.linspace(0, 2 * np.pi, 100)
            circle_x = prev_x + amp * np.cos(theta)
            circle_y = prev_y + amp * np.sin(theta)
            circles[i].set_data(circle_x, circle_y)
            
            # Desenha o vetor (raio)
            lines[i].set_data([prev_x, x], [prev_y, y])

        # Adiciona o ponto final ao caminho do desenho
        path_x.append(x)
        path_y.append(y)
        path_line.set_data(path_x, path_y)

        return circles + lines + [path_line]

    ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init,
                                  interval=interval, blit=True)
    plt.show()

if __name__ == "__main__": 

    # Diretório base (para definir o padrão)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Animar epicíclos a partir de coeficientes de Fourier")
    parser.add_argument(
        "--input",
        "-i",
        default=os.path.join(base_dir, '..', 'cpp', 'output.json'),
        help="Caminho para o arquivo JSON gerado pelo C++"
    )

    args = parser.parse_args()
    json_path = args.input

    if not os.path.exists(json_path):
        print(f"Erro: Arquivo não encontrado em '{json_path}'")
        sys.exit(1)

    coefficients = load_coefficients(json_path)
    animate_epicycles(coefficients)

