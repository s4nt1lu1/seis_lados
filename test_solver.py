import solver as sv
import time

# Un scramble de ejemplo (11 movimientos)
# R U2 R' F2 U' F' U F2 U' F' D'


cubestring = 'FFBLBRDLDUBRRFDDLRLUUUFB' 

print(f"Resolviendo: {cubestring}")
print("Buscando solución óptima (determinística)...")

start_time = time.time()
solucion = sv.solve(cubestring) # <--- Esta es la magia
end_time = time.time()

print(f"\n¡Solución encontrada en {end_time - start_time:.4f} segundos!")
print(solucion)