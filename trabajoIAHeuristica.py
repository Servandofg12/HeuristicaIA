# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 11:45:56 2021

@author: Servando
"""

import problema_planificación_pddl as probpl
import búsqueda_espacio_estados as búsqee


#PROBLEMA RUEDA PINCHADA ---------------------------------------------------------

ruedas = {'rueda-pinchada', 'rueda-repuesto'}
localizaciones = {'eje', 'maletero', 'suelo'}
en = probpl.Predicado(ruedas, localizaciones)

estado_inicial_rueda = probpl.Estado(en('rueda-pinchada', 'eje'),
                                     en('rueda-repuesto', 'maletero'))
print(estado_inicial_rueda)

# Sacar la rueda de repuesto del maletero
sacar = probpl.AcciónPlanificación(
    nombre='sacar_repuesto',
    precondicionesP=en('rueda-repuesto', 'maletero'),
    efectosP=en('rueda-repuesto', 'suelo'),
    efectosN=en('rueda-repuesto', 'maletero')
)

# Quitar la rueda pinchada del eje
quitar = probpl.AcciónPlanificación(
    nombre='quitar_pinchada',
    precondicionesP=en('rueda-pinchada', 'eje'),
    efectosP=en('rueda-pinchada', 'suelo'),
    efectosN=en('rueda-pinchada', 'eje')
)

# Colocar la rueda de repuesto en el eje
poner = probpl.AcciónPlanificación(
    nombre='poner_repuesto',
    precondicionesP=en('rueda-repuesto', 'suelo'),
    precondicionesN=en('rueda-pinchada', 'eje'),
    efectosP=en('rueda-repuesto', 'eje'),
    efectosN=en('rueda-repuesto', 'suelo')
)

# Guardar la rueda pinchada en el maletero
guardar = probpl.AcciónPlanificación(
    nombre='guardar_pinchada',
    precondicionesP=en('rueda-pinchada', 'suelo'),
    precondicionesN=en('rueda-repuesto', 'maletero'),
    efectosP=en('rueda-pinchada', 'maletero'),
    efectosN=en('rueda-pinchada', 'suelo')
)

print(quitar)
print(guardar)

objetivosP=[en('rueda-pinchada', 'maletero'),
                en('rueda-repuesto', 'eje')]

problema_rueda_pinchada = probpl.ProblemaPlanificación(
    operadores=[quitar, guardar, sacar, poner],
    estado_inicial=estado_inicial_rueda,
    objetivosP=[en('rueda-pinchada', 'maletero'),
                en('rueda-repuesto', 'eje')]
)

búsqueda_profundidad = búsqee.BúsquedaEnProfundidad()
búsqueda_profundidad.buscar(problema_rueda_pinchada)

búsqueda_anchura = búsqee.BúsquedaEnAnchura()
búsqueda_anchura.buscar(problema_rueda_pinchada)

#Optima
busqueda_optima = búsqee.BúsquedaÓptima()
busqueda_optima.buscar(problema_rueda_pinchada)


#Primero_mejor
busqueda_primero_mejor = búsqee.BúsquedaPrimeroElMejor(búsqee.NodoConHeurística.f)
busqueda_primero_mejor.buscar(problema_rueda_pinchada)
