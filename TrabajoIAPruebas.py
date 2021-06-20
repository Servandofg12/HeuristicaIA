# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 14:38:24 2021

@author: Servando
"""


import problema_planificación_pddl_trabajo as probpl
import búsqueda_espacio_estados_trabajo as búsqee

#import time
#start_time = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

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

búsqueda_profundidad = búsqee.BúsquedaEnProfundidad()
búsqueda_profundidad.buscar(problema_rueda_pinchada)

búsqueda_anchura = búsqee.BúsquedaEnAnchura()
búsqueda_anchura.buscar(problema_rueda_pinchada)

#Optima
busqueda_optima = búsqee.BúsquedaÓptima()
busqueda_optima.buscar(problema_rueda_pinchada)


#Primero_mejor con heuristica de la practica
busqueda_primero_mejor = búsqee.BúsquedaPrimeroElMejor(búsqee.NodoConHeurística.f)
busqueda_primero_mejor.buscar(problema_rueda_pinchada)

#Busqueda estrella con heuristica de la practica
busqueda_estrella = búsqee.BúsquedaAEstrella(búsqee.NodoConHeurística.f)
busqueda_estrella.buscar(problema_rueda_pinchada)




#Busqueda con y sin heuristica PRUEBAS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Sin heuristica
busqueda_sin_heuristica = búsqee.BúsquedaConHeuristica(búsqee.BúsquedaConHeuristica.pregoGeneral(estado_inicial_rueda, objetivosPositivos, operadores))
busqueda_sin_heuristica.buscar(problema_rueda_pinchada)

#Con heuristica
#La heuristica devuelve quitar_pinchada y guardar_pinchada pero la solucion correcta
#es quitar_pinchada, sacar_repuesto y guardar_pinchada, ya que la heuristica no tiene en cuenta
#las precondiciones negativas pero el problema si
busqueda_con_heuristica = búsqee.BúsquedaConHeuristica(búsqee.BúsquedaConHeuristica.pregoGeneral(estado_inicial_rueda, objetivosPositivos, operadores,True))
busqueda_con_heuristica.buscar(problema_rueda_pinchada)
búsqee.BúsquedaConHeuristica.resolverConHeuristica(estado_inicial_rueda, objetivosPositivos, operadores,True)

#Con heuristica PRUEBA
busqueda_con_heuristica_prueba = búsqee.BúsquedaConHeuristicaPRUEBA(búsqee.BúsquedaConHeuristicaPRUEBA.pregoGeneral(estado_inicial_rueda, objetivosPositivos, operadores,True))
busqueda_con_heuristica_prueba.buscarConHeuristica(problema_rueda_pinchada)

#Con heuristica metiendole el problema
busqueda_con_heuristica = búsqee.BúsquedaConHeuristica(búsqee.BúsquedaConHeuristica.pregoGeneral2(estado_inicial_rueda,problema_rueda_pinchada,True))
busqueda_con_heuristica.buscar(problema_rueda_pinchada)




#Con heuristica, estado inicial = objetivo
busqueda_con_heuristica_problema_facil = búsqee.BúsquedaConHeuristica(búsqee.BúsquedaConHeuristica.pregoGeneral(estado_inicial_rueda, estado_inicial_rueda, operadores,True))
busqueda_con_heuristica_problema_facil.buscar(problema_facil)
búsqee.BúsquedaConHeuristica.resolverConHeuristica(estado_inicial_rueda, estado_inicial_rueda, operadores,True)

#Con heuristica imposible de resolver
busqueda_con_heuristica_problema_imposible = búsqee.BúsquedaConHeuristica(búsqee.BúsquedaConHeuristica.pregoGeneral(estado_inicial_rueda, objetivoImposible, operadoresImposibleResolver,True))
#cuando es imposible el buscar da fallo
busqueda_con_heuristica_problema_imposible.buscar(problema_imposible)
búsqee.BúsquedaConHeuristica.resolverConHeuristica(estado_inicial_rueda, objetivoImposible, operadoresImposibleResolver,True)

