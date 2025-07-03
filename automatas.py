import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parámetros
size = 100  # Tamaño de la membrana (100x100)
c = 0.2     # Velocidad de propagación (debe ser < 1 para estabilidad)
steps = 200 # Pasos de tiempo

# Inicialización de matrices
u_past = np.zeros((size, size))  # t - 1
u_now = np.zeros((size, size))   # t
u_next = np.zeros((size, size))  # t + 1

# Condición inicial: un pico en el centro
center = size // 2
u_now[center, center//2] = 1

# Configuración del gráfico
fig, ax = plt.subplots()
im = ax.imshow(u_now, cmap='seismic', vmin=-1, vmax=1, animated=True)

def update(frame):
    global u_past, u_now, u_next
    for i in range(1, size - 1):
        for j in range(1, size - 1):
            u_next[i, j] = (2 * u_now[i, j] - u_past[i, j] +
                            c ** 2 * (u_now[i+1, j] + u_now[i-1, j] +
                                      u_now[i, j+1] + u_now[i, j-1] -
                                      4 * u_now[i, j]))
    # Actualización de estados
    u_past, u_now = u_now, u_next.copy()
    im.set_array(u_now)
    return [im]

ani = animation.FuncAnimation(fig, update, frames=steps, interval=30, blit=True)
plt.title("Simulación de ondas en una membrana 2D")
plt.show()
