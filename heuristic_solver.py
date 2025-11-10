import coord
import moves as mv  # <-- Al importar esta línea, las tablas ya se cargan.
import pruning as pr
import random
import defs
import face
import cubie
import time

# --- Carga de Tablas ---
# No hay que llamar a 'mv.init_move_tables()'.
# ¡Pero SÍ hay que llamar a la de 'pruning' si la usamos!
# Para este agente "a ciegas", no usamos 'pruning' para el fitness.
print("Motor (moves) cargado por importación.")


# Definimos el estado resuelto (Formato de string de face.py)
# 4xU, 4xR, 4xF, 4xD, 4xL, 4xB
SOLVED_STRING = "UUUURRRRFFFFDDDDLLLLBBBB" 

# -----------------------------------------------------------------
# 🎯 FUNCIÓN DE FITNESS "A CIEGAS" (HEURÍSTICA)
# -----------------------------------------------------------------
def get_fitness_heuristic(scramble_coords, secuencia_agente):
    """
    Función de fitness sub-óptima.
    No usa el mapa 'cornerprun'. Solo cuenta cuántas pegatinas
    están en el lugar incorrecto.
    """
    
    # 1. Simular el movimiento del agente
    cubo_simulado = coord.CoordCube()
    cubo_simulado.corntwist = scramble_coords.corntwist
    cubo_simulado.cornperm = scramble_coords.cornperm
    
    for m in secuencia_agente:
        cubo_simulado.move(m)
        
    # 2. Convertir las coordenadas (twist, perm) de nuevo a un estado físico
    cc = cubie.CubieCube()
    cc.set_cornertwist(cubo_simulado.corntwist)
    cc.set_corners(cubo_simulado.cornperm)
    
    # 3. Convertir el estado físico a un string de pegatinas
    fc = cc.to_facelet_cube() 
    cubestring_resultante = fc.to_string()
    
    # 4. Calcular el fitness (contar errores)
    fitness = 0
    for i in range(24):
        if cubestring_resultante[i] != SOLVED_STRING[i]:
            fitness += 1 # Contamos cuántas pegatinas están mal
            
    return fitness
# -----------------------------------------------------------------


# -----------------------------------------------------------------
# 🧬 LÓGICA DEL ENJAMBRE (Usando el nuevo fitness)
# -----------------------------------------------------------------
def generar_agente_aleatorio(longitud):
    return [random.randint(0, defs.N_MOVE - 1) for _ in range(longitud)]

def mutar_agente(agente, tasa_mutacion):
    hijo = list(agente)
    for i in range(len(hijo)):
        if random.random() < tasa_mutacion:
            hijo[i] = random.randint(0, defs.N_MOVE - 1)
    return hijo

# --- PARÁMETROS DEL PSO ---
N_PARTICULAS = 1000
N_GENERACIONES = 15000
LONGITUD_SOLUCION = 11 # Buscamos una solución SUB-ÓPTIMA más larga
TASA_MUTACION = 0.15      

# --- 1. Definir el problema (el scramble) ---
cubestring = 'FFBLBRDLDUBRRFDDLRLUUUFB' 
fc = face.FaceCube()
fc.from_string(cubestring)
cc = fc.to_cubie_cube()
scramble_coords = coord.CoordCube(cc) 

fitness_inicial = get_fitness_heuristic(scramble_coords, [])

print("--- Problema a Resolver (Agente Heurístico/Sub-óptimo) ---")
print(f"Scramble: {cubestring}")
print(f"Fitness Inicial (pegatinas mal): {fitness_inicial}")
print("\n--- Iniciando Solver PSO (Heurístico) ---")
print(f"Generaciones: {N_GENERACIONES}, Partículas: {N_PARTICULAS}, Longitud: {LONGITUD_SOLUCION} mov")

# --- 2. Inicializar el Enjambre ---
mejor_agente = generar_agente_aleatorio(LONGITUD_SOLUCION)
mejor_fitness = get_fitness_heuristic(scramble_coords, mejor_agente)

start_time = time.time()

# --- 3. Iniciar el ciclo de evolución (PSO) ---
for gen in range(N_GENERACIONES):
    
    enjambre_actual = [mutar_agente(mejor_agente, TASA_MUTACION) for _ in range(N_PARTICULAS)]
    enjambre_actual[0] = mejor_agente 

    for agente in enjambre_actual:
        fitness = get_fitness_heuristic(scramble_coords, agente)
        
        if fitness < mejor_fitness:
            mejor_fitness = fitness
            mejor_agente = agente
            print(f"Gen {gen+1} - ¡Nuevo mejor fitness encontrado!: {mejor_fitness} (pegatinas mal)")

    if mejor_fitness == 0:
        break

end_time = time.time()

# --- 4. Resultados ---
print("\n--- Búsqueda de Agentes (PSO) Terminada ---")
print(f"Tiempo total: {end_time - start_time:.4f} segundos")
if mejor_fitness == 0:
    print("¡ÉXITO! Se encontró una solución sub-óptima.")
    print(f"Solución (lista de {LONGITUD_SOLUCION} mov): {mejor_agente}")
else:
    print(f"FALLO. No se encontró solución en {N_GENERACIONES} generaciones.")
    print(f"El agente más cercano se quedó con {mejor_fitness} pegatinas incorrectas.")