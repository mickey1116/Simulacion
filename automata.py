import pygame
import numpy as np

# Parámetros de simulación
WIDTH, HEIGHT = 700, 700          # Tamaño de la ventana
GRID_SIZE = 100                   # Tamaño de la cuadrícula (GRID_SIZE x GRID_SIZE)
CELL_SIZE = WIDTH // GRID_SIZE   # Tamaño de cada celda en píxeles
C = 0.2                           # Velocidad de propagación
DAMPING = 0.999                # Amortiguamiento

# Inicializar pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ondas en membrana 2D (Pygame)")
clock = pygame.time.Clock()

# Estados de la simulación
u_past = np.zeros((GRID_SIZE, GRID_SIZE))
u_now = np.zeros((GRID_SIZE, GRID_SIZE))
u_next = np.zeros((GRID_SIZE, GRID_SIZE))
obstaculos = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)


# Condición inicial: pico en el centro
center = GRID_SIZE // 2
#u_now[center, center] = 1
obstaculos[:, GRID_SIZE // 2] = True

slit_width = 2  # Ancho de cada agujero
gap = 4         # Separación entre los agujeros

center = GRID_SIZE // 2
slit1 = center - gap // 2 - slit_width
slit2 = center + gap // 2

for i in range(slit1, slit1 + slit_width):
    obstaculos[i, GRID_SIZE // 2] = False  # Primer agujero
for i in range(slit2, slit2 + slit_width):
    obstaculos[i, GRID_SIZE // 2] = False  # Segundo agujero

# Función para actualizar la simulación
def update_wave():
    global u_past, u_now, u_next
    for i in range(1, GRID_SIZE - 1):
        for j in range(1, GRID_SIZE - 1):
            if obstaculos[i,j]:
                u_next[i,j]=0
                continue
            laplaciano = (u_now[i+1, j] + u_now[i-1, j] +
                          u_now[i, j+1] + u_now[i, j-1] -
                          4 * u_now[i, j])
            u_next[i, j] = (2 * u_now[i, j] - u_past[i, j] +
                            C**2 * laplaciano)
    u_next *= DAMPING  # Disipación
    u_past, u_now = u_now, u_next.copy()

# Función para dibujar el estado actual
def draw_wave():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if obstaculos[i,j]:
                color=(255,255,255)
            else:
                val = u_now[i, j]
                # Convertir valor de -1 a 1
                val = np.clip(u_now[i, j], -1, 1)
                # Valor absoluto y polaridad
                abs_val = abs(val)
                intensity = int(abs_val * 255)

                if val > 0:
                    color = (0,intensity, 0)  # Rojo
                elif val < 0:
                    color = (intensity, intensity,0)  # Azul
                else:
                    color = (0, 0,0)  # Fondo negro


            pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Bucle principal
running = True
while running:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Clic para generar una onda
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            j, i = x // CELL_SIZE, y // CELL_SIZE
            if event.button == 1:
                u_now[i,j]=1
            elif event.button==3:
                obstaculos[i,j]=True

    update_wave()
    draw_wave()
    pygame.display.flip()

pygame.quit()
