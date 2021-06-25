# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 14:38:24 2021

@author: Servando
"""


import problema_planificación_pddl_trabajo as probpl
import búsqueda_espacio_estados_trabajo as búsqee
import time


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

operadores=[quitar, guardar, sacar, poner]
operadoresImposibleResolver=[quitar, guardar, sacar]

objetivosPositivos = probpl.Estado(en('rueda-pinchada', 'maletero'))

#Problema normal
problema_rueda_pinchada = probpl.ProblemaPlanificación(
    operadores=operadores,
    estado_inicial=estado_inicial_rueda,
    objetivosP=objetivosPositivos.atomos
)

#Problema con estado inicial = objetivo
problema_facil = probpl.ProblemaPlanificación(
    operadores=[quitar, guardar, sacar, poner],
    estado_inicial=estado_inicial_rueda,
    objetivosP=estado_inicial_rueda.atomos
)

#Problema imposible de resolver
objetivoImposible = probpl.Estado(en('rueda-repuesto', 'eje'))

problema_imposible = probpl.ProblemaPlanificación(
    operadores=[quitar, guardar, sacar],
    estado_inicial=estado_inicial_rueda,
    objetivosP=objetivoImposible.atomos
)

#Busqueda en profundidad
start_time = time.time()
búsqueda_profundidad = búsqee.BúsquedaEnProfundidad()
búsqueda_profundidad.buscar(problema_rueda_pinchada)
print("--- %s seconds ---" % (time.time() - start_time))

#Busqueda en anchura
start_time = time.time()
búsqueda_anchura = búsqee.BúsquedaEnAnchura()
búsqueda_anchura.buscar(problema_rueda_pinchada)
print("--- %s seconds ---" % (time.time() - start_time))

#Busqueda Optima
start_time = time.time()
busqueda_optima = búsqee.BúsquedaÓptima()
busqueda_optima.buscar(problema_rueda_pinchada)
print("--- %s seconds ---" % (time.time() - start_time))

#Busqueda Primero_mejor con heuristica 
start_time = time.time()
busqueda_primero_mejor = búsqee.BúsquedaPrimeroElMejor(búsqee.NodoConHeurística.f)
busqueda_primero_mejor.buscar(problema_rueda_pinchada)
print("--- %s seconds ---" % (time.time() - start_time))

#Busqueda estrella con heuristica
start_time = time.time()
busqueda_estrella = búsqee.BúsquedaAEstrella(búsqee.NodoConHeurística.f)
busqueda_estrella.buscar(problema_rueda_pinchada)
print("--- %s seconds ---" % (time.time() - start_time))




#Busqueda con y sin heuristica PRUEBAS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Sin heuristica 
busqueda_sin_heuristica = búsqee.BúsquedaSinHeuristicaRueda(búsqee.BúsquedaSinHeuristicaRueda.f)
busqueda_sin_heuristica.buscar(problema_rueda_pinchada)

#Con heuristica random 
#La heuristica devuelve quitar_pinchada y guardar_pinchada pero la solucion correcta
#es quitar_pinchada, sacar_repuesto y guardar_pinchada, ya que la heuristica no tiene en cuenta
#las precondiciones negativas pero el problema si
busqueda_con_heuristica = búsqee.BúsquedaConHeuristica()
busqueda_con_heuristica.buscar(problema_rueda_pinchada)
búsqee.BúsquedaConHeuristicaRuedaRecursiva.resolverConHeuristica(estado_inicial_rueda, objetivosPositivos, operadores,True)

#Con heuristica random 2
busqueda_con_heuristica = búsqee.BúsquedaConHeuristica()
busqueda_con_heuristica.buscar(problema_rueda_pinchada)

#Con heuristica PRUEBA -hace bien la heurística problema recursivo-
busqueda_con_heuristica_rueda_recursiva = búsqee.BúsquedaConHeuristicaRuedaRecursiva()
busqueda_con_heuristica_rueda_recursiva.buscar(problema_rueda_pinchada)


#Con heuristica, estado inicial = objetivo
busqueda_con_heuristica_problema_facil = búsqee.BúsquedaConHeuristicaRuedaFacil()
busqueda_con_heuristica_problema_facil.buscar(problema_facil)
búsqee.BúsquedaConHeuristicaRuedaRecursiva.resolverConHeuristica(estado_inicial_rueda, estado_inicial_rueda, operadores,True)


#Con heuristica imposible de resolver
busqueda_con_heuristica_problema_imposible = búsqee.BúsquedaConHeuristicaRuedaImposible(búsqee.NodoConHeurísticaRuedaRecursiva.pregoGeneral(estado_inicial_rueda, objetivoImposible, operadoresImposibleResolver, True))
#cuando es imposible el buscar da fallo
busqueda_con_heuristica_problema_imposible.buscar(problema_imposible)#Da fallo 
búsqee.BúsquedaConHeuristicaRuedaRecursiva.resolverConHeuristica(estado_inicial_rueda, objetivoImposible, operadoresImposibleResolver,True)

