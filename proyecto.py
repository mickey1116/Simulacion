import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- Parámetros generales ---
N = 30
sigma_c = 1.0
carga_incremental = 0.05
pasos = 50
porosidades = [0.1, 0.3]  # comparar 10% vs 30%

# --- Función para simular y animar una porosidad ---
def simular_porosidad(porosidad, ax, fig_title):

    # Inicializar estado y tensión
    estado = np.ones((N, N), dtype=int)
    tension = np.zeros((N, N))

    # Asignar poros
    mask_poros = np.random.rand(N, N) < porosidad
    estado[mask_poros] = 0

    frames = []

    def vecinos_validos(i, j):
        vecinos = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            ni, nj = i+dx, j+dy
            if 0 <= ni < N and 0 <= nj < N:
                if estado[ni, nj] == 1:
                    vecinos.append((ni, nj))
        return vecinos

    def actualizar(frame):
        nonlocal estado, tension
        # Aplicar carga en fila superior
        tension[0, estado[0] == 1] += carga_incremental

        fracturados = []
        for i in range(N):
            for j in range(N):
                if estado[i, j] == 1 and tension[i, j] >= sigma_c:
                    estado[i, j] = 2
                    fracturados.append((i, j))

        # Redistribuir
        for i, j in fracturados:
            vecinos = vecinos_validos(i, j)
            if vecinos:
                carga = tension[i, j] / len(vecinos)
                for ni, nj in vecinos:
                    tension[ni, nj] += carga
            tension[i, j] = 0

        ax.clear()
        ax.imshow(estado, cmap='viridis', vmin=0, vmax=2)
        ax.set_title(f'{fig_title}\nPaso {frame}')
        ax.axis('off')

    return actualizar

# --- Crear figura y animaciones para las dos porosidades ---
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

ani1 = FuncAnimation(fig, simular_porosidad(0.1, axs[0], 'Porosidad 10%'), frames=pasos, interval=300)
ani2 = FuncAnimation(fig, simular_porosidad(0.3, axs[1], 'Porosidad 30%'), frames=pasos, interval=300)

plt.tight_layout()
plt.show()
