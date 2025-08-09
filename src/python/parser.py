import os
import argparse
from svgpathtools import svg2paths
import numpy as np
import csv

# ===== CONFIGURAÇÕES PADRÃO =====
base_dir = os.path.dirname(os.path.abspath(__file__))
# Arquivo SVG padrão (usado se não for passado via argumento)
default_svg = os.path.join(base_dir, "..", "..", "svg", "github_logo.svg")
# Arquivo CSV padrão de saída para C++
default_csv = os.path.join(base_dir, "..", "cpp", "input.csv")
# Número de pontos para amostragem
num_points = 3000
# ================================

# --- Parser de argumentos ---
parser = argparse.ArgumentParser(description="Extrai pontos de um SVG e salva em CSV para Fourier.")
parser.add_argument("--input", type=str, default=default_svg, help="Caminho para o arquivo SVG de entrada.")
parser.add_argument("--output", type=str, default=default_csv, help="Caminho para o arquivo CSV de saída.")
args = parser.parse_args()

svg_file = args.input
csv_file = args.output

# --- FUNÇÃO DE OTIMIZAÇÃO ---
# Reordena os pontos para criar um caminho suave e contínuo
def greedy_shortest_path(points_list):
    """Reordena uma lista de pontos para formar um caminho contínuo."""
    # Converte para números complexos para facilitar o cálculo de distância
    points_complex = np.array([p[0] + 1j*p[1] for p in points_list])
    
    if len(points_complex) == 0:
        return []

    path = []
    # Começa com o primeiro ponto
    current_point = points_complex[0]
    remaining_points = list(points_complex[1:])
    path.append(current_point)

    total = len(remaining_points)
    print("Otimizando o traçado dos pontos...")
    
    i = 0
    while remaining_points:
        # Encontra o índice do ponto mais próximo do ponto atual
        nearest_idx = np.argmin([abs(p - current_point) for p in remaining_points])
        
        # Atualiza o ponto atual
        current_point = remaining_points.pop(nearest_idx)
        path.append(current_point)
        
        # Mostra o progresso
        i += 1
        if i % 100 == 0:
            print(f"  Progresso: {i}/{total}", end='\r')
    
    print("\nOtimização concluída.")
    
    return [[p.real, p.imag] for p in path]

print(f"Lendo SVG de: {svg_file}")
print(f"Salvando CSV em: {csv_file}")

# Lê caminhos do SVG
paths, _ = svg2paths(svg_file)

# Calcula comprimento total
total_length = sum(p.length() for p in paths)
if total_length == 0:
    raise ValueError("Comprimento total do SVG é zero. Verifique o arquivo.")

# Distância entre pontos (para espaçamento uniforme)
spacing = total_length / num_points

points = []

# Amostragem de pontos igualmente espaçados ao longo dos paths
for path in paths:
    length = path.length()
    if length == 0:
        continue
    num_samples = max(1, int(length / spacing))
    for t in np.linspace(0, 1, num_samples, endpoint=False):
        point = path.point(t)
        points.append((point.real, point.imag))

# Normaliza pontos: centraliza e escala
points = np.array(points)
mean = points.mean(axis=0)
points -= mean
scale = max(points.max(), abs(points.min()))
if scale != 0:
    points /= scale

optimized_points = greedy_shortest_path(points.tolist())

# Salva no CSV os pontos OTIMIZADOS
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["x", "y"])
    writer.writerows(optimized_points)

print(f"{len(optimized_points)} pontos otimizados e salvos em {csv_file}")
