# Simulación de fractura macro en material cerámico poroso usando autómatas celulares hexagonales
import numpy as np
import matplotlib.pyplot as plt
import random
import time

# --- Parámetros generales ---
random.seed(time.time())  # semilla variable
radius = 60                  # radio del grid hexagonal (~120 celdas, ~72 µm)
porosity = 0.15             # fracción de celdas porosas
sigma_threshold = 0.22       # umbral base de ruptura
phi = 0.3                   # variabilidad relativa en enlace (solo debilitamiento)
xsi = 0.4                   # fracción de celdas con subumbrales débiles
N = 2                       # número de enlaces debilitados por celda afectada
max_stress = 5.0            # esfuerzo máximo aplicado
steps = 60                  # número de incrementos de carga
damage_cycles = 4          # ciclos de carga para fatiga
fatigue_factor = 0.93      # reducción de umbral tras fatiga

# --- Vecindario hexagonal (coordenadas axiales) ---
HEX_DIRS = [
    ( +1,  0), ( +1, -1), ( 0, -1),
    ( -1,  0), ( -1, +1), ( 0, +1)
]

# --- Inicialización de celdas ---
cells = {}
for q in range(-radius, radius + 1):
    for r in range(-radius, radius + 1):
        s = -q - r
        if abs(s) <= radius:
            cells[(q, r)] = {
                'poro': False,
                'bonds': [sigma_threshold] * 6,
                'failed': [False] * 6,
                'damage': [0] * 6
            }

# --- Introducir poros al azar ---
num_poros = int(porosity * len(cells))
for pos in random.sample(list(cells), num_poros):
    cells[pos]['poro'] = True

# --- Debilitar enlaces aleatorios en algunas celdas ---
candidates = [pos for pos in cells if not cells[pos]['poro']]
num_weak = int(xsi * len(candidates))
for pos in random.sample(candidates, num_weak):
    dirs = random.sample(range(6), N)
    for d in dirs:
        variation = 1 - abs(random.uniform(-phi, phi))
        cells[pos]['bonds'][d] *= variation

# --- Simulación de carga uniaxial y acumulación de fatiga ---
def apply_stress():
    no_break_steps=0
    for step in range(steps):
        stress = (step + 1) * max_stress / steps
        broken = 0
        max_breaks_per_step = 300  # máximo número de enlaces que pueden romperse por paso
        step_fractures = 0
        for (q, r), data in cells.items():
            if data['poro']:
                continue
            for d, (dq, dr) in enumerate(HEX_DIRS):
                nq, nr = q + dq, r + dr
                if (nq, nr) in cells and not cells[(nq, nr)]['poro']:
                    if not data['failed'][d]:
                        threshold = data['bonds'][d]
                        if stress >= threshold:
                            data['failed'][d] = True
                            opposite = (d + 3) % 6
                            cells[(nq, nr)]['failed'][opposite] = True
                            broken += 1
                        else:
                            data['damage'][d] += 1
                            if data['damage'][d] >= damage_cycles:
                                data['bonds'][d] *= fatigue_factor
                                data['damage'][d] = 0
        if broken == 0:
            no_break_steps+=1
            if no_break_steps>=5:
                print(f"Detenido en paso {step+1}, estrés={stress:.2f}, fracturas en paso=0")
            #break
        if broken > 1189:
            print("¡Demasiadas fracturas, deteniendo!")
            break
    print(f"Total enlaces rotos: {sum(sum(data['failed']) for data in cells.values())}")

apply_stress()

# --- Visualización macroescala (solo contornos) ---
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_aspect('equal')
ax.axis('off')

size = 1.0  # radio del hexágono
for (q, r), data in cells.items():
    if data['poro']:
        continue  # celda poro: omitir contorno
    # posición cartesiana
    x = size * 3/2 * q
    y = size * np.sqrt(3) * (r + q/2)
    # dibujar contornos intactos
    for d, (dq, dr) in enumerate(HEX_DIRS):
        if not data['failed'][d]:
            nq, nr = q + dq, r + dr
            if (nq, nr) in cells and not cells[(nq, nr)]['poro']:
                # línea entre centros
                x2 = x + size * 3/2 * dq
                y2 = y + size * np.sqrt(3) * (dr + dq/2)
                ax.plot([x, x2], [y, y2], color='black', linewidth=0.5)

plt.title("Patrón de fractura macro - Hexagonal", color='black')
#plt.savefig("fractura_macro_hex.png", dpi=300, facecolor='white')
plt.show()
