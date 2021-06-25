import collections
import heapq
import types
import problema_planificación_pddl_trabajo as probpl
import random



ruedas = {'rueda-pinchada', 'rueda-repuesto'}
localizaciones = {'eje', 'maletero', 'suelo'}
en = probpl.Predicado(ruedas, localizaciones)

estado_inicial_rueda = probpl.Estado(en('rueda-pinchada', 'eje'),
                                     en('rueda-repuesto', 'maletero'))

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

objetivosPositivos = probpl.Estado(en('rueda-pinchada', 'maletero'))
objetivoImposible = probpl.Estado(en('rueda-repuesto', 'eje'))
operadores=[quitar, guardar, sacar, poner]
operadoresImposibleResolver=[quitar, guardar, sacar]

#--------------------------------------------------------------------------------------

class ListaNodos(collections.deque):
    def añadir(self, nodo):
        self.append(nodo)

    def vaciar(self):
        self.clear()

    def __contains__(self, nodo):
        return any(x.estado == nodo.estado
                   for x in self)


class PilaNodos(ListaNodos):
    def sacar(self):
        return self.pop()


class ColaNodos(ListaNodos):
    def sacar(self):
        return self.popleft()


class ColaNodosConPrioridad:
    def __init__(self):
        self.nodos = []
        self.nodo_generado = 0

    def añadir(self, nodo):
        heapq.heappush(self.nodos, (nodo.heurística, self.nodo_generado, nodo))
        self.nodo_generado += 1

    def sacar(self):
        return heapq.heappop(self.nodos)[2]

    def vaciar(self):
        self.__init__()

    def __iter__(self):
        return iter(self.nodos)

    def __contains__(self, nodo):
        return any(x[2].estado == nodo.estado and
                   x[2].heurística <= nodo.heurística
                   for x in self.nodos)


class NodoSimple:
    def __init__(self, estado, padre=None, acción=None):
        self.estado = estado
        self.padre = padre
        self.acción = acción

    def es_raíz(self):
        return self.padre is None

    def sucesor(self, acción):
        Nodo = self.__class__
        return Nodo(acción.aplicar(self.estado), self, acción)

    def solución(self):
        if self.es_raíz():
            acciones = []
        else:
            acciones = self.padre.solución()
            acciones.append(self.acción.nombre)
        return acciones

    def __str__(self):
        return 'Estado: {}'.format(self.estado)


class NodoConProfundidad(NodoSimple):
    def __init__(self, estado, padre=None, acción=None):
        super().__init__(estado, padre, acción)
        if self.es_raíz():
            self.profundidad = 0
        else:
            self.profundidad = padre.profundidad + 1

    def __str__(self):
        return 'Estado: {0}; Prof: {1}'.format(self.estado, self.profundidad)



class BúsquedaGeneral:
    def __init__(self, detallado=False):
        self.detallado = detallado
        if self.detallado:
            self.Nodo = NodoConProfundidad
        else:
            self.Nodo = NodoSimple
        self.explorados = ListaNodos()

    def es_expandible(self, nodo):
        return True

    def expandir_nodo(self, nodo, problema):
        return (nodo.sucesor(acción)
                for acción in problema.acciones_aplicables(nodo.estado))

    def es_nuevo(self, nodo):
        return (nodo not in self.frontera and
                nodo not in self.explorados)

    def buscar(self, problema):
        self.frontera.vaciar()
        self.explorados.vaciar()
        self.frontera.añadir(self.Nodo(problema.estado_inicial))
        while True:
            if not self.frontera:
                return None
            
            nodo = self.frontera.sacar()#Cuando es imposible se va fuera de rango
            if self.detallado:
                print('{0}Nodo: {1}'.format('  ' * nodo.profundidad, nodo))
            if problema.es_estado_final(nodo.estado):
                return nodo.solución()
            self.explorados.añadir(nodo)
            if self.es_expandible(nodo):
                nodos_hijos = self.expandir_nodo(nodo, problema)
                for nodo_hijo in nodos_hijos:
                    if self.es_nuevo(nodo_hijo):
                        self.frontera.añadir(nodo_hijo)
                        
                     
   
class BúsquedaEnAnchura(BúsquedaGeneral):
    def __init__(self, detallado=False):
        super().__init__(detallado)
        self.frontera = ColaNodos()


class BúsquedaEnProfundidad(BúsquedaGeneral):
    def __init__(self, detallado=False):
        super().__init__(detallado)
        self.frontera = PilaNodos()
        self.explorados = PilaNodos()

        def añadir_vaciando_rama(self, nodo):
            if self:
                while True:
                    último_nodo = self.pop()
                    if último_nodo == nodo.padre:
                        self.append(último_nodo)
                        break
            self.append(nodo)
        self.explorados.añadir = types.MethodType(añadir_vaciando_rama,
                                                  self.explorados)


class BúsquedaEnProfundidadAcotada(BúsquedaEnProfundidad):
    def __init__(self, cota, detallado=False):
        super().__init__(detallado)
        self.Nodo = NodoConProfundidad
        self.cota = cota

    def es_expandible(self, nodo):
        return nodo.profundidad < self.cota


class BúsquedaEnProfundidadIterativa:
    def __init__(self, cota_final, cota_inicial=0, detallado=False):
        self.cota_inicial = cota_inicial
        self.cota_final = cota_final
        self.detallado = detallado

    def buscar(self, problema):
        for cota in range(self.cota_inicial, self.cota_final):
            bpa = BúsquedaEnProfundidadAcotada(cota, self.detallado)
            solución = bpa.buscar(problema)
            if solución:
                return solución


class BúsquedaPrimeroElMejor(BúsquedaGeneral):#HEURISTICA
    def __init__(self, f, detallado=False):
        super().__init__(detallado)
        self.Nodo = NodoConHeurísticaRandom
        self.Nodo.f = staticmethod(f)#Aqui puede que vaya el prego
        self.frontera = ColaNodosConPrioridad()
        self.explorados = ListaNodos()
        self.explorados.__contains__ = types.MethodType(
            lambda self, nodo: any(x.estado == nodo.estado and
                                   x.heurística <= nodo.heurística
                                   for x in self),
            self.explorados)


class BúsquedaÓptima(BúsquedaPrimeroElMejor):
    def __init__(self, detallado=False):
        def coste(nodo):
            return nodo.coste
        super().__init__(coste, detallado)


class BúsquedaAEstrella(BúsquedaPrimeroElMejor):
    def __init__(self, h, detallado=False):
        def coste(nodo):
            return nodo.coste

        def f(nodo):
            return coste(nodo) + h(nodo)
        super().__init__(f, detallado)


#--------------Trabajo Heuristica--------------------------------------------------

class NodoConHeurísticaRandom(NodoSimple):#HEURISTICA
    def __init__(self, estado, padre=None, acción=None):
        super().__init__(estado, padre, acción)
        if self.es_raíz():
            self.profundidad = 0
            self.coste = 0
        else:
            self.profundidad = padre.profundidad + 1
            self.coste = padre.coste + acción.coste_de_aplicar(padre.estado)
        self.heurística = self.f(self)

    @staticmethod#HEURISTICA
    def f(nodo):
        aleatorio = random.randint(0,10)
        print("Estado actual ", nodo.estado)
        print("Heurística: ", aleatorio)
        return aleatorio

class BúsquedaConHeuristica(BúsquedaGeneral):#HEURISTICA
    def __init__(self, detallado=False):
        super().__init__(detallado)
        self.Nodo = NodoConHeurísticaRandom
        self.frontera = ColaNodosConPrioridad()
        self.explorados = ListaNodos()
        self.explorados.__contains__ = types.MethodType(
            lambda self, nodo: any(x.estado == nodo.estado and
                                  x.heurística <= nodo.heurística 
                                   for x in self),
            self.explorados)
  
    
            
#PROBLEMA RUEDA RECURSIVA
class NodoConHeurísticaRuedaRecursiva(NodoSimple):#HEURISTICA
    def __init__(self, estado, padre=None, acción=None):
        super().__init__(estado, padre, acción)
        if self.es_raíz():
            self.profundidad = 0
            self.coste = 0
        else:
            self.profundidad = padre.profundidad + 1
            self.coste = padre.coste + acción.coste_de_aplicar(padre.estado)
        self.heurística = self.f(self)
        
    @staticmethod#HEURISTICA
    def f(nodo):
        return NodoConHeurísticaRuedaRecursiva.pregoGeneral(nodo.estado, objetivosPositivos, operadores, True)
        
    def __str__(self):
        return 'Estado: {0}; Prof: {1}; Heur: {2}; Coste: {3}'.format(
            self.estado, self.profundidad, self.heurística, self.coste)
    
    @staticmethod
    def pregoGeneral(estado_inicial, objetivo, operadores, heuristica=False):
        if heuristica:
            print("")
            print("------COMIENZO DE LA HEURISTA------")
            lista = NodoConHeurísticaRuedaRecursiva.pregoRecursivo(estado_inicial, objetivo, operadores, heuristica)
            solucion = reversed(lista)
            
            print("")
            #La lista es al reves dado que vamos del objetivo al estado inicial
            print("------LISTA DE OPERADORES SOLUCION:------")
            for operador in solucion:
                print(operador.nombre)
            print("")
            
            #print("------LISTA NORMAL DE OPERADORES SOLUCION:------")
            #for operador in lista:
            #    print(operador.nombre)
            #print("")
                
            print("------Cantidad para heuristica: " + str(len(lista)) + " ------")
            print("")
            return len(lista)
        else:
            print("")
            print("NO SE HA USADO HEURISTICA")
    
   
    @staticmethod#un objetivo formado por un solo literal positivo cerrado
    def pregoRecursivo(estado_inicial, objetivo, operadores, heuristica=False):
        lista = []#lista con los operadores solucion optima
        if heuristica:
            print("Estado actual: ")
            print(estado_inicial)
            
            #Si el estado e satisface p, entonces devolver prego(e,p) = lista vacía.
            if estado_inicial.satisface_positivas(objetivo.atomos):
                print("")
                print("El estado inicial es el objetivo")
                #return len(lista)
                return lista
    
            #Si el estado e no satisface p, y además no existe ninguna acción que lo incluya entre sus
            #efectos, entonces devolver prego(e,p) = lista con todas las acciones del problema
            if estado_inicial.satisface_positivas(objetivo.atomos)==False:
               listaEfectosPositivo = [] 
               listaPrecondicionesPositivas = []
               for operador in operadores:
                   efectosDeOperador = operador.obtener_EfectosP()#hacerlo lista
                   precondicionesDeOperador = operador.obtener_precondicionesP()#hacerlo lista
                   listaEfectosPositivo.append(probpl.Estado(efectosDeOperador).atomos)
                   listaPrecondicionesPositivas.append(probpl.Estado(precondicionesDeOperador).atomos)
               
               satisface = False
               precondicionAGuardar = []
               indice = 0
               for efecto in listaEfectosPositivo:#Lista de diccionarios
                   if probpl.Estado(efecto).satisface_positivas(objetivo.atomos) and satisface==False:
                       satisface = True
                       #lista.append(probpl.Estado(efecto).atomos)#Añadimos la precondicion del efecto que satisface el objetivo
                       lista.append(operadores[indice])
                       precondicionAGuardar.append(probpl.Estado(listaPrecondicionesPositivas[indice]))
                   indice = indice + 1
               if satisface==False:
                   print("")
                   print("Imposible de resolver")
                   return operadores
               
            #En caso contrario, devolver la lista más corta entre las siguientes opciones:
                #▪ [A] + prego(e,prepA),
                #para cada acción A que tenga a p entre sus efectos, donde el “+” representa la
                #concatenación de listas, y prepA representa la lista de literales positivos de la
                #precondición de A
               else:
                   print("")
                   print("Realización de iteración")
                   #Cogemos la precondicion del operador que satisface al objetivo de esta iteracion
                   precondiciones = precondicionAGuardar[len(precondicionAGuardar)-1]
                   #A la lista resultado, lista de todos los operadores solucion, le concatenamos
                   #el resto de operadores hasta que se llega al estado inicial
                   lista+=NodoConHeurísticaRuedaRecursiva.pregoRecursivo(estado_inicial, precondiciones, operadores, True)
                   return lista
        else:
            return lista
    

    
class BúsquedaConHeuristicaRuedaRecursiva(BúsquedaGeneral):
    def __init__(self, detallado=False):
        super().__init__(detallado)
        self.Nodo = NodoConHeurísticaRuedaRecursiva
        self.frontera = ColaNodosConPrioridad()
        self.explorados = ListaNodos()
        self.explorados.__contains__ = types.MethodType(
            lambda self, nodo: any(x.estado == nodo.estado and
                                  x.heurística >= nodo.heurística 
                                   for x in self),
            self.explorados)
        
        
    def resolverConHeuristica(estado_inicial, objetivo, operadores, heuristica=False):
        numHeuristica = NodoConHeurísticaRuedaRecursiva.pregoGeneral(estado_inicial, objetivo, operadores, heuristica)
        resultado = BúsquedaConHeuristicaRuedaRecursiva.resolverConHeuristicaAuxiliar(estado_inicial, objetivo, operadores, True, numHeuristica)
        return resultado
    
    def resolverConHeuristicaAuxiliar(estado_inicial, objetivo, operadores, heuristica, numHeuristica):
        auxiliar = []
        resultado = [auxiliar]
        #recorridos = []
        cogidos = []
        profundidad = 0
        if numHeuristica==len(operadores):
            print("IMPOSIBLE DE RESOLVER")
            return resultado
        if numHeuristica==0:
            print("ESTADO INICIAL ES EL OBJETIVO")
            return resultado
        if profundidad > heuristica:
            print("No es suficiente eficiente, hay más eficientes")
        #precondicionEstadoIncicial = estado_inicial.obtener_precondicionesP()
        for operador in operadores:
            precondicionesOperador = probpl.Estado(operador.obtener_precondicionesP())
            print("PRECONDICION: ")
            print(precondicionesOperador)
            #for precondicon in precondicionesOperador:
                #probpl.Estado(efecto).satisface_positivas(objetivo.atomos
                #print("EFECTO:")
                #print(precondicon)
                #print("ESTADO EFECTO:")
                #print(probpl.Estado(precondicon))
                #print(estado_inicial.obtener_precondicionesP())
            #hay que buscar el operador que tiene el efecto positivo del estado inicial
            if (estado_inicial.obtener_EfectosP()).satisface_positivas(precondicionesOperador.atomos):#falla aquí
                    #probpl.Estado(precondicon).satisface_positivas(estado_inicial.obtener_PrecondicionesP()):
                    #estado_inicial.obtener_PrecondicionesP().satisface_positivas(operador)
                if operador not in cogidos:
                    cogidos.append(operador)
        profundidad = profundidad + 1
        for cogido in cogidos:
            resultado.append(cogido)
            nuevoEstadoActual = cogido
            resultado += BúsquedaConHeuristica.resolverConHeuristicaAuxiliar(nuevoEstadoActual, objetivo, operadores, True, numHeuristica)
        
        return min(resultado)
      
    
#PROBLEMA RUEDA FACIL
class NodoConHeurísticaRuedaFacil(NodoSimple):#HEURISTICA
    def __init__(self, estado, padre=None, acción=None):
        super().__init__(estado, padre, acción)
        if self.es_raíz():
            self.profundidad = 0
            self.coste = 0
        else:
            self.profundidad = padre.profundidad + 1
            self.coste = padre.coste + acción.coste_de_aplicar(padre.estado)
        self.heurística = self.f(self)
        
    @staticmethod#HEURISTICA
    def f(nodo):
        return NodoConHeurísticaRuedaRecursiva.pregoGeneral(nodo.estado, nodo.estado, operadores, True)
        

class BúsquedaConHeuristicaRuedaFacil(BúsquedaGeneral):
    def __init__(self, detallado=False):
        super().__init__(detallado)
        self.Nodo = NodoConHeurísticaRuedaFacil
        self.frontera = ColaNodosConPrioridad()
        self.explorados = ListaNodos()
        self.explorados.__contains__ = types.MethodType(
            lambda self, nodo: any(x.estado == nodo.estado and
                                  x.heurística >= nodo.heurística 
                                   for x in self),
            self.explorados)
 
    
#PROBLEMA RUEDA IMPOSIBLE
class BúsquedaConHeuristicaRuedaImposible(BúsquedaGeneral):#HEURISTICA
    def __init__(self, pregoGeneral, detallado=False):
        super().__init__(detallado)
        self.Nodo = NodoSinHeurística
        self.pregoGeneral = staticmethod(NodoConHeurísticaRuedaRecursiva.pregoGeneral)#Valor de heuristica
        self.frontera = ColaNodosConPrioridad()
        self.explorados = ListaNodos()
        self.explorados.__contains__ = types.MethodType(
            lambda self, nodo: any(x.estado == nodo.estado and
                                  x.heurística <= nodo.pregoGeneral 
                                   for x in self),
            self.explorados)    
        
#SIN HEURISTICA
class NodoSinHeurística(NodoSimple):#HEURISTICA
    def __init__(self, estado, padre=None, acción=None):
        super().__init__(estado, padre, acción)
        if self.es_raíz():
            self.profundidad = 0
            self.coste = 0
        else:
            self.profundidad = padre.profundidad + 1
            self.coste = padre.coste + acción.coste_de_aplicar(padre.estado)
        self.heurística = 0
      

class BúsquedaSinHeuristicaRueda(BúsquedaGeneral):#HEURISTICA
    def __init__(self, f, detallado=False):
        super().__init__(detallado)
        self.Nodo = NodoSinHeurística
        self.pregoGeneral = staticmethod(f)#Valor de heuristica
        self.frontera = ColaNodosConPrioridad()
        self.explorados = ListaNodos()
        self.explorados.__contains__ = types.MethodType(
            lambda self, nodo: any(x.estado == nodo.estado and
                                  x.heurística <= nodo.heurística 
                                   for x in self),
            self.explorados)
        
    @staticmethod
    def f(nodo):   
        return 0