import coord
import moves as mv  # <--- Importamos 'moves' para que se ejecuten sus tablas
import pruning as pr
import random
import defs
import face
import cubie

# --- Carga TODAS las tablas (motor y mapa) ---
try:
    # 'moves' se carga solo con el import.
    # 'pruning' SÍ necesita que llamemos a su función:
    pr.create_cornerprun_table() # Carga 'cornerprun' en memoria
    print("Motor (moves) y Mapa (pruning) cargados.")
except FileNotFoundError:
    print("¡Error! Asegúrate de haber ejecutado moves.py y pruning.py primero.")
    exit()

# -----------------------------------------------------------------
# 🎯 ESTA ES TU FUNCIÓN DE FITNESS PARA EL PSO
# -----------------------------------------------------------------
def get_fitness(scramble_coords, secuencia_agente):
    """
    Toma las coordenadas de un cubo revuelto y una secuencia de movimientos
    (tu agente de PSO). Devuelve qué "tan cerca" está de la solución.
    
    Un fitness de 0 significa que está resuelto.
    """
    
    # Copiamos el estado revuelto para no modificar el original
    cubo_simulado = coord.CoordCube()
    cubo_simulado.corntwist = scramble_coords.corntwist
    cubo_simulado.cornperm = scramble_coords.cornperm
    
    # Aplicamos la secuencia de movimientos del agente
    for m in secuencia_agente:
        cubo_simulado.move(m)
        
    # Obtenemos el estado final
    twist_final = cubo_simulado.corntwist
    perm_final = cubo_simulado.cornperm
    
    # ¡LA MAGIA!
    # Consultamos la tabla de poda (el oráculo) para saber la distancia
    distancia = pr.corner_depth[defs.N_TWIST * perm_final + twist_final]
    
    return distancia
# -----------------------------------------------------------------


# --- Ejemplo de cómo usar tu función de fitness ---

# 1. Define tu cubo revuelto (el mismo de test_solver.py)
cubestring = 'FFBLBRDLDUBRRFDDLRLUUUFB' 

# Convertimos el string a coordenadas
fc = face.FaceCube()
fc.from_string(cubestring)
cc = fc.to_cubie_cube()
scramble_coords = coord.CoordCube(cc) 

distancia_inicial = get_fitness(scramble_coords, [])
print(f"Estado inicial revuelto: {scramble_coords}")
print(f"Fitness (distancia) inicial: {distancia_inicial} movimientos (óptimo determinístico)")

# 2. 🤖 Tu PSO generará "agentes" (secuencias aleatorias)
agente_1 = [random.randint(0, defs.N_MOVE - 1) for _ in range(15)] 
agente_2 = [random.randint(0, defs.N_MOVE - 1) for _ in range(15)]

# 3. Mides el fitness de cada agente
fitness_1 = get_fitness(scramble_coords, agente_1)
fitness_2 = get_fitness(scramble_coords, agente_2)

print("\n--- Prueba de Agentes PSO ---")
print(f"Agente 1 (15 mov aleatorios) alcanzó un fitness de: {fitness_1} (distancia restante)")
print(f"Agente 2 (15 mov aleatorios) alcanzó un fitness de: {fitness_2} (distancia restante)")