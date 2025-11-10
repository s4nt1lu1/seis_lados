import coord
import moves as mv  # Importa 'moves' para que se ejecuten sus tablas
import pruning as pr
import random
import defs
import face
import cubie
import time

# --- Carga TODAS las tablas (motor y mapa) ---
try:
    pr.create_cornerprun_table() # Carga 'cornerprun' en memoria
    print("Motor (moves) y Mapa (pruning) cargados.")
except FileNotFoundError:
    print("¡Error! Asegúrate de haber ejecutado moves.py y pruning.py primero.")
    exit()

# -----------------------------------------------------------------
# 🎯 FUNCIÓN DE FITNESS (La copiamos de pso_fitness.py)
# -----------------------------------------------------------------
def get_fitness(scramble_coords, secuencia_agente):
    cubo_simulado = coord.CoordCube()
    cubo_simulado.corntwist = scramble_coords.corntwist
    cubo_simulado.cornperm = scramble_coords.cornperm
    
    for m in secuencia_agente:
        cubo_simulado.move(m)
        
    twist_final = cubo_simulado.corntwist
    perm_final = cubo_simulado.cornperm
    
    distancia = pr.corner_depth[defs.N_TWIST * perm_final + twist_final]
    return distancia
# -----------------------------------------------------------------


# -----------------------------------------------------------------
# 🧬 LÓGICA DEL ENJAMBRE (PSO / Algoritmo Evolutivo)
# -----------------------------------------------------------------
def generar_agente_aleatorio(longitud):
    # Un agente es una lista de 'longitud' movimientos aleatorios (0-8)
    return [random.randint(0, defs.N_MOVE - 1) for _ in range(longitud)]

def mutar_agente(agente, tasa_mutacion):
    # Crea un "hijo" mutado del agente
    hijo = list(agente) # Copia
    for i in range(len(hijo)):
        if random.random() < tasa_mutacion:
            # Cambia este movimiento por uno nuevo aleatorio
            hijo[i] = random.randint(0, defs.N_MOVE - 1)
    return hijo

# --- PARÁMETROS DEL PSO ---
N_PARTICULAS = 200       # 100 agentes por generación
N_GENERACIONES = 20000    # Máximo de intentos
LONGITUD_SOLUCION = 11  # Le decimos que busque soluciones de 11 mov (el óptimo)
TASA_MUTACION = 0.1      # 10% de probabilidad de que un movimiento mute

# --- 1. Definir el problema (el scramble) ---
cubestring = 'FFBLBRDLDUBRRFDDLRLUUUFB' 
fc = face.FaceCube()
fc.from_string(cubestring)
cc = fc.to_cubie_cube()
scramble_coords = coord.CoordCube(cc) 
distancia_inicial = get_fitness(scramble_coords, [])

print("--- Problema a Resolver ---")
print(f"Scramble: {cubestring}")
print(f"Distancia Óptima (Determinística): {distancia_inicial} movimientos")
print("\n--- Iniciando Solver PSO/Evolutivo ---")
print(f"Generaciones: {N_GENERACIONES}, Partículas: {N_PARTICULAS}, Longitud: {LONGITUD_SOLUCION} mov")

# --- 2. Inicializar el Enjambre (Generación 0) ---
# Empezamos con el "mejor agente" siendo uno aleatorio
mejor_agente = generar_agente_aleatorio(LONGITUD_SOLUCION)
mejor_fitness = get_fitness(scramble_coords, mejor_agente)

start_time = time.time()

# --- 3. Iniciar el ciclo de evolución (PSO) ---
for gen in range(N_GENERACIONES):
    
    # Creamos un nuevo enjambre de "hijos" mutados del mejor agente
    enjambre_actual = [mutar_agente(mejor_agente, TASA_MUTACION) for _ in range(N_PARTICULAS)]
    
    # Añadimos al "mejor agente" anterior (Elitismo)
    enjambre_actual[0] = mejor_agente 

    # Evaluamos el fitness de todo el enjambre
    for agente in enjambre_actual:
        fitness = get_fitness(scramble_coords, agente)
        
        # Si este agente es el mejor que hemos visto, lo guardamos
        if fitness < mejor_fitness:
            mejor_fitness = fitness
            mejor_agente = agente
            print(f"Gen {gen+1} - ¡Nuevo mejor fitness encontrado!: {mejor_fitness} (Distancia restante)")

    # Condición de parada: ¡Encontramos la solución!
    if mejor_fitness == 0:
        break

end_time = time.time()

# --- 4. Resultados ---
print("\n--- Búsqueda de Agentes (PSO) Terminada ---")
print(f"Tiempo total: {end_time - start_time:.4f} segundos")
if mejor_fitness == 0:
    print("¡ÉXITO! Se encontró una solución óptima.")
    print(f"Solución (lista de mov): {mejor_agente}")
else:
    print(f"FALLO. No se encontró solución en {N_GENERACIONES} generaciones.")
    print(f"El agente más cercano se quedó a {mejor_fitness} movimientos de la solución.")