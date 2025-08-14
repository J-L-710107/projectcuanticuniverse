import random
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para Termux
import matplotlib.pyplot as plt
import os

# Configuración
START = (0, 0)  # Casa: Oriente 164 y Norte 5
GOAL = (-12, -8)  # Escuela: Retorno 35 de Cecilio Robelo 52
MAX_STEPS = 300  # Más pasos para aumentar llegadas
NUM_TRIALS = 100
OBS_PROB = {1: 0.85, 2: 0.25, 3: 0.15}  # Más observaciones
INTERF_PROB = 0.02  # Menos interferencias (acusaciones)
NEUTRALIZE_PROB = 0.5  # Ceder al niño (menos confrontación)

def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def choose_direction():
    """Elige dirección con preferencia al suroeste."""
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Norte, Sur, Este, Oeste
    weights = [0.1, 0.45, 0.1, 0.35]  # Más probable sur y oeste
    return random.choices(directions, weights=weights, k=1)[0]

def simulate_walk():
    """Simula un trayecto."""
    target_pos = START
    traveler_pos = (random.randint(1, 3), random.randint(-1, 1))
    steps = 0
    observations = 0
    interferences = 0
    neutralizations = 0
    path = [target_pos]
    traveler_path = [traveler_pos]

    while steps < MAX_STEPS and target_pos != GOAL:
        interference = random.random() < INTERF_PROB
        if interference:
            interferences += 1

        # Asegurar que el viajero esté a 1-3 manzanas
        dist = manhattan_distance(target_pos, traveler_pos)
        if dist > 3 or dist == 0:
            dx = -1 if target_pos[0] > traveler_pos[0] else 1 if target_pos[0] < traveler_pos[0] else 0
            dy = -1 if target_pos[1] > traveler_pos[1] else 1 if target_pos[1] < traveler_pos[1] else 0
            traveler_pos = (target_pos[0] + dx * random.randint(1, 3), target_pos[1] + dy * random.randint(1, 3))
            dist = manhattan_distance(target_pos, traveler_pos)

        # Observación
        observe = dist in OBS_PROB and random.random() < OBS_PROB[dist]
        if observe:
            observations += 1

        # Movimiento del target
        if interference and (not observe or random.random() >= NEUTRALIZE_PROB):
            target_pos = (target_pos[0] + 1, target_pos[1])  # Interferencia: forzar este
        else:
            dx, dy = choose_direction()
            target_pos = (target_pos[0] + dx, target_pos[1] + dy)
            if observe and interference:
                neutralizations += 1

        path.append(target_pos)
        steps += 1

        # Movimiento del viajero
        dx, dy = choose_direction()
        new_traveler_pos = (traveler_pos[0] + dx, traveler_pos[1] + dy)
        if 1 <= manhattan_distance(new_traveler_pos, target_pos) <= 3:
            traveler_pos = new_traveler_pos
        traveler_path.append(traveler_pos)

    return {
        "reached_goal": target_pos == GOAL,
        "steps": steps,
        "observations": observations,
        "interferences": interferences,
        "neutralizations": neutralizations,
        "path": path,
        "traveler_path": traveler_path
    }

# Ejecutar simulación
results = [simulate_walk() for _ in range(NUM_TRIALS)]
reached_goal = sum(1 for r in results if r["reached_goal"])
avg_steps = np.mean([r["steps"] for r in results])
avg_observations = np.mean([r["observations"] / r["steps"] if r["steps"] > 0 else 0 for r in results])
avg_interferences = np.mean([r["interferences"] for r in results])
avg_neutralizations = np.mean([r["neutralizations"] / r["interferences"] if r["interferences"] > 0 else 0 for r in results if r["interferences"] > 0])

# Imprimir resultados
print(f"Resultados de {NUM_TRIALS} trayectos:")
print(f"Probabilidad de llegar a la escuela: {reached_goal / NUM_TRIALS:.2f}")
print(f"Promedio de pasos por trayecto: {avg_steps:.2f}")
print(f"Fracción promedio de intersecciones observadas: {avg_observations:.2f}")
print(f"Promedio de interferencias por trayecto: {avg_interferences:.2f}")
print(f"Fracción de interferencias neutralizadas: {avg_neutralizations:.2f}")

# Visualizar y guardar gráfica
try:
    path = results[0]["path"]
    traveler_path = results[0]["traveler_path"]
    x, y = zip(*path)
    tx, ty = zip(*traveler_path)

    plt.plot(x, y, 'b-o', label='Target (Tú de niño)')
    plt.plot(tx, ty, 'r--x', label='Viajero (Tú adulto)')
    plt.plot(START[0], START[1], 'go', label='Casa (Oriente 164)')
    plt.plot(GOAL[0], GOAL[1], 'ro', label='Escuela (Retorno 35)')
    plt.grid(True)
    plt.xlabel('X (Este-Oeste)')
    plt.ylabel('Y (Norte-Sur)')
    plt.title('Ejemplo de Trayecto')
    plt.legend()

    output_file = 'trayecto.png'
    plt.savefig(output_file, dpi=100)
    plt.close()

    if os.path.exists(output_file):
        print(f"Gráfica guardada como '{output_file}'.")
        print("Mueve el archivo a tu galería con: mv trayecto.png /sdcard/")
    else:
        print("Error: No se pudo generar la gráfica.")
except Exception as e:
    print(f"Error al generar la gráfica: {e}")
