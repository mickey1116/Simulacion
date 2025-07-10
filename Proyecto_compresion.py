import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors

# --- Función para truncar el colormap (evita colores muy oscuros al inicio) ---
def truncar_colormap(cmap_in, minval=0.2, maxval=1.0, n=100):
    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        'truncado', cmap_in(np.linspace(minval, maxval, n))
    )
    return new_cmap

# Parámetros
N = 30
sigma_c = 1.0
carga_incremental = 0.05
pasos = 50
porosidades = [0.05, 0.3]

# Colormap truncado para evitar el negro en tensiones bajas
cmap_grad = truncar_colormap(plt.cm.inferno, minval=0.3)
norm_grad = mcolors.Normalize(vmin=0, vmax=sigma_c)

def simular_porosidad(porosidad, ax, fig_title):
    estado = np.ones((N, N), dtype=int)
    tension = np.zeros((N, N))
    estado[np.random.rand(N, N) < porosidad] = 0  # poros

    def vecinos_validos(i, j):
        vecinos = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            ni, nj = i+dx, j+dy
            if 0 <= ni < N and 0 <= nj < N and estado[ni, nj] == 1:
                vecinos.append((ni, nj))
        return vecinos

    def actualizar(frame):
        nonlocal estado, tension

        # Carga combinada (arriba + derecha)
        tension[0, estado[0] == 1] += carga_incremental
        tension[:, -1][estado[:, -1] == 1] += carga_incremental

        fracturados = []
        for i in range(N):
            for j in range(N):  #estado de fracturados si superan el umbrarl de tension
                if estado[i, j] == 1 and tension[i, j] >= sigma_c:
                    estado[i, j] = 2
                    fracturados.append((i, j))

        for i, j in fracturados:
            vecinos = vecinos_validos(i, j)
            if vecinos:     #transmision de tension
                carga = tension[i, j] / len(vecinos)
                for ni, nj in vecinos:
                    tension[ni, nj] += carga
            tension[i, j] = 0

        # Crear imagen RGB con color personalizado según tensión
        img = np.zeros((N, N, 3))

        for i in range(N):
            for j in range(N):
                if estado[i, j] == 0:
                    img[i, j] = [0, 0, 0]  # poro = Negro
                elif estado[i, j] == 1:
                    img[i, j] = cmap_grad(norm_grad(tension[i, j]))[:3] #gradiente de color por intensidad de tension
                elif estado[i, j] == 2:
                    img[i, j] = [0, 0, 0]  # fracturado = negro

        ax.clear()
        ax.imshow(img)
        ax.set_title(f'{fig_title}\nPaso {frame}')
        ax.axis('off')

    return actualizar

# Comparación entre dos porosidades
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

ani1 = FuncAnimation(fig, simular_porosidad(0.1, axs[0], 'Porosidad 10%'), frames=pasos, interval=300)
ani2 = FuncAnimation(fig, simular_porosidad(0.3, axs[1], 'Porosidad 30%'), frames=pasos, interval=300)

plt.tight_layout()
plt.show()

#import seaborn as sns
#import matplotlib.pyplot as plt
#
#def heatmap_final(porosidad, pasos):
#    estado = np.ones((N, N), dtype=int)
#    tension = np.zeros((N, N))
#    estado[np.random.rand(N, N) < porosidad] = 0
#
#    def vecinos_validos(i, j):
#        vecinos = []
#        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
#            ni, nj = i+dx, j+dy
#            if 0 <= ni < N and 0 <= nj < N and estado[ni, nj] == 1:
#                vecinos.append((ni, nj))
#        return vecinos
#
#    for _ in range(pasos):
#        tension[0, estado[0] == 1] += carga_incremental
#        tension[:, -1][estado[:, -1] == 1] += carga_incremental
#
#        fracturados = []
#        for i in range(N):
#            for j in range(N):
#                if estado[i, j] == 1 and tension[i, j] >= sigma_c:
#                    estado[i, j] = 2
#                    fracturados.append((i, j))
#
#        for i, j in fracturados:
#            vecinos = vecinos_validos(i, j)
#            if vecinos:
#                carga = tension[i, j] / len(vecinos)
#                for ni, nj in vecinos:
#                    tension[ni, nj] += carga
#            tension[i, j] = 0
#
#    # Poros y fracturados en blanco
#    mask = (estado != 1)
#
#    return tension.copy(), mask
#
## Ejecutar para ambas porosidades
#t1, m1 = heatmap_final(0.1, pasos)
#t2, m2 = heatmap_final(0.3, pasos)
#
## Graficar heatmaps lado a lado
#fig, axs = plt.subplots(1, 2, figsize=(12, 5))
#
#sns.heatmap(t1, mask=m1, ax=axs[0], cmap='inferno', cbar=True, square=True)
#axs[0].set_title('Tensión final - Porosidad 10%')
#
#sns.heatmap(t2, mask=m2, ax=axs[1], cmap='inferno', cbar=True, square=True)
#axs[1].set_title('Tensión final - Porosidad 30%')
#
#plt.tight_layout()
#plt.show()
#
#