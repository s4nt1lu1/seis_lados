#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import math
from dataclasses import dataclass
from typing import List

# ========================================================================
# struct and function declaration
# ========================================================================

@dataclass
class Cube:
    """
    Define el estado de un cubo.
    p: una permutación de S_7 (lista de 7 ints)
    q: una orientación de Z_3^7 (lista de 7 ints)
    """
    p: List[int]
    q: List[int]
    
    # __eq__ (para '==') y __repr__ (para 'print') 
    # son generados automáticamente por @dataclass

# helper functions
def compose(sgm: List[int], tau: List[int]) -> List[int]:
    """
    Compone dos permutaciones `sgm` y `tau`.
    e.g. si sgm = {2, 0, 1}, tau = {1, 0, 2}, comp(sgm, tau) = {0, 2, 1}
    ya que {0, 1, 2} --tau--> {1, 0, 2} --sgm--> {0, 2, 1}
    """
    return [sgm[tau[i]] for i in range(len(sgm))]

# ========================================================================
# constants and global variables
# ========================================================================

X  = Cube(p=[4, 1, 0, 3, 6, 5, 2], q=[0, 0, 0, 0, 0, 0, 0])
X_ = Cube(p=[2, 1, 6, 3, 0, 5, 4], q=[0, 0, 0, 0, 0, 0, 0])
X2 = Cube(p=[6, 1, 4, 3, 2, 5, 0], q=[0, 0, 0, 0, 0, 0, 0])

Y  = Cube(p=[0, 2, 6, 3, 4, 1, 5], q=[0, 2, 1, 0, 0, 1, 2])
Y_ = Cube(p=[0, 5, 1, 3, 4, 6, 2], q=[0, 2, 1, 0, 0, 1, 2])
Y2 = Cube(p=[0, 6, 5, 3, 4, 2, 1], q=[0, 0, 0, 0, 0, 0, 0])

Z  = Cube(p=[0, 1, 2, 5, 3, 6, 4], q=[0, 0, 0, 1, 2, 2, 1])
Z_ = Cube(p=[0, 1, 2, 4, 6, 3, 5], q=[0, 0, 0, 1, 2, 2, 1])
Z2 = Cube(p=[0, 1, 2, 6, 5, 4, 3], q=[0, 0, 0, 0, 0, 0, 0])

MOVES = [X, X_, X2, Y, Y_, Y2, Z, Z_, Z2]
# MOVES = [X, X_, Y, Y_, Z, Z_] # Descomentar para usar el set más pequeño

SOLVED = Cube(p=[0, 1, 2, 3, 4, 5, 6], q=[0, 0, 0, 0, 0, 0, 0])

P = math.factorial(7)
Q = 3**6
N = P * Q

M = len(MOVES)

# ========================================================================
# cube state representation
# ========================================================================

def encode_p(p_in: List[int]) -> int:
    """Mapea un elemento de S7 a [0, 7! - 1] usando el código de Lehmer."""
    p = list(p_in) # Copiar para no modificar el original
    q = list(np.argsort(p))
    r = 0
    n = len(p)
    for k in range(n - 1, 0, -1):
        s = p[k]
        p[k], p[q[k]] = p[q[k]], p[k] # swap p
        q[k], q[s] = q[s], q[k]     # swap q
        r += s * math.factorial(k)
    return r

def decode_p(x: int, n: int) -> List[int]:
    """Mapea un int de [0, 7! - 1] a un elemento de S7."""
    p = list(range(n)) # iota
    for k in range(n - 1, 0, -1):
        f = math.factorial(k)
        s = x // f
        x %= f
        p[k], p[s] = p[s], p[k] # swap
    return p

def encode_q(q: List[int]) -> int:
    """Convierte 'q' de base 3 a decimal."""
    # Las orientaciones de 6 cubies determinan la 7ma
    v = q[:-1] # Tomar los primeros 6 elementos
    v.reverse()
    dec = 0
    for i in range(6):
        dec += v[i] * (3**i)
    return dec

def decode_q(y: int) -> List[int]:
    """Convierte 'y' de decimal a base 3 (para 7 elementos)."""
    q = [0] * 7
    idx = 1
    temp_y = y
    while temp_y > 0:
        q[idx] = temp_y % 3
        temp_y //= 3
        idx += 1
    
    q.reverse() # Replicar la lógica del C++
    
    # FTC: sum(q) = 0 mod 3. Usar esto para recuperar el 7mo elemento.
    s = sum(q)
    q[6] = (3 - s % 3) % 3
    return q

def encode_cube(cube: Cube) -> int:
    """Codifica un estado completo del cubo a un solo entero."""
    x = encode_p(cube.p)
    y = encode_q(cube.q)
    return x * Q + y

def decode_cube(i: int) -> Cube:
    """Decodifica un entero a un estado completo del cubo."""
    x = i // Q
    y = i % Q
    return Cube(p=decode_p(x, 7), q=decode_q(y))

def apply_move(before: Cube, move: Cube) -> Cube:
    """Aplica un movimiento 'move' al estado 'before'."""
    p = compose(before.p, move.p)
    _q = compose(before.q, move.p)
    q = [(_q[i] + move.q[i]) % 3 for i in range(7)]
    return Cube(p=p, q=q)

# ========================================================================
# main program
# ========================================================================

def main():
    # Y[i][j] = k significa: desde el estado 'i', aplicando el mov 'j',
    # llegamos al estado 'k'.
    print(f"Construyendo la matriz de transición Y ({N}x{M})...")
    Y = np.zeros((N, M), dtype=np.int32) # Usar int32 es suficiente

    for i in range(N):
        cube = decode_cube(i)
        for j in range(M):
            Y[i, j] = encode_cube(apply_move(cube, MOVES[j]))
    
    print("Matriz construida. Iniciando simulación...")

    ui = 1.0 / N
    # x[i] = probabilidad de estar en el estado 'i'
    x = np.zeros(N, dtype=np.float64)
    
    # Asumimos que el estado 0 es el resuelto (SOLVED).
    # Verifiquemos esto:
    solved_idx = encode_cube(SOLVED)
    # x[solved_idx] = 1.0 # Empezar desde el estado resuelto
    
    # El código C++ inicia en el estado 0 (x[0] = 1.0).
    # El estado 0 corresponde a:
    # x=0, y=0 -> decode_p(0, 7) = [0, 1, 2, 3, 4, 5, 6]
    #           -> decode_q(0)   = [0, 0, 0, 0, 0, 0, 0]
    # Así que el estado 0 ES el estado resuelto.
    
    x[0] = 1.0

    for t in range(1, 51):
        # cur_x es la distribución de probabilidad en el tiempo t-1
        cur_x = x 

        # x_new[i] = sum(P(i -> k) * cur_x[k] for k in states)
        # Esto es equivalente a la transpuesta:
        # x_new = T.dot(cur_x)
        
        # El código C++ calcula:
        # x_new[i] = sum(cur_x[Y[i][j]] / M for j in moves)
        # x_new[i] = (1/M) * sum(cur_x[k] for k in {Y[i,0], Y[i,1], ...})
        
        # Esto se puede vectorizar en numpy:
        # 1. cur_x[Y] crea una matriz (N, M) usando indexación avanzada:
        #    matriz[i, j] = cur_x[Y[i, j]]
        # 2. np.sum(..., axis=1) suma sobre los movimientos (dimensión j)
        #    vector[i] = sum(matriz[i, j] for j in 0..M-1)
        # 3. Dividimos por M
        
        x = np.sum(cur_x[Y], axis=1) / M
        
        # Calcular la distancia de variación total (d/2)
        d = np.sum(np.abs(x - ui))
        
        print(f"{t}\t{d / 2.0:.20f}")

if __name__ == "__main__":
    main()