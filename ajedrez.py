import random
import numpy as np

""" POBLACIÓN """ 
def generarRandom():
    array= np.arange(8)
    np.random.shuffle(array)
    return array

def generarIndividuo():
    individuo=generarRandom()
    for i, valor in enumerate(individuo):
        while i == valor:
            np.random.shuffle(individuo)
            valor = individuo[i]
    return individuo



def generaPoblacion(tamaño):
    poblacion = []
    for _ in range(tamaño):
        arreglo_unico = generarIndividuo()
        poblacion.append(arreglo_unico)
    return poblacion



for i, arreglo in enumerate(generaPoblacion(10)):
    print(f"Arreglo {i+1}: {arreglo}")

""" EVALUAR """
# Función para evaluar el número de choques en un individuo
def evaluar_choques(individuo):
    # Inicializamos el contador de choques
    choques = 0
    # Iteramos sobre todas las reinas
    for i in range(8):
        # Iteramos sobre las reinas restantes
        for j in range(i+1, 8):
            # Verificamos si hay choques en diagonales
            if abs(individuo[i] - individuo[j]) == abs(i - j):
                choques += 2
    # Devolvemos el número total de choques
    return choques

# Función para evaluar el fitness de una población de individuos
def evaluar_poblacion(poblacion):
    # Calculamos el número de individuos en la población
    n = len(poblacion)
    # Creamos un arreglo para almacenar el fitness de cada individuo en la población
    fitness = np.zeros(n, dtype=int)
    # Iteramos sobre cada individuo en la población
    for i in range(n):
        # Calculamos el número de choques en el individuo actual
        choques = evaluar_choques(poblacion[i])
        # Asignamos el número de choques al arreglo de fitness
        fitness[i] = choques
    # Devolvemos el arreglo de fitness de la población
    return fitness

print (evaluar_poblacion(generaPoblacion(10)))


""" CRUZA """

def cruza(poblacion):
    # Creamos una lista para almacenar a los padres seleccionados
    ChildParents = []

    # Creamos una matriz para almacenar a los hijos
    childs = []

    # Mientras no hayamos generado suficientes hijos
    while len(childs) < len(poblacion):
        # Seleccionamos el primer padre aleatoriamente
        firstParent = random.choice(poblacion)
        # Seleccionamos el segundo padre aleatoriamente, asegurándonos de que sea diferente al primer padre
        secondParent = random.choice([p for p in poblacion if not np.array_equal(p, firstParent)])
        # Agregamos las filas seleccionadas a la lista de padres
        ChildParents.append((firstParent, secondParent))
        # Eliminamos las filas seleccionadas de la lista poblacion
        poblacion.remove(firstParent)
        poblacion.remove(secondParent)

    # Generamos los hijos
    for parents in ChildParents:
        firstParent, secondParent = parents
        firstChild = firstParent[:4] + [num for num in secondParent if num not in firstParent[:4]]
        secondChild = secondParent[:4] + [num for num in firstParent if num not in secondParent[:4]]
        childs.append(firstChild)
        childs.append(secondChild)
    return childs





""" MUTACIÓN """

PORCENTAJE_MUTACION = 0.10

# Función para generar los índices que van a mutar en la población de hijos
def generar_indices(poblacion_hijos):
    # Calcula el número de hijos a mutar
    cantidad_de_hijos = int(PORCENTAJE_MUTACION * len(poblacion_hijos))

    # Genera índices aleatorios para mutar
    indices_a_mutar = random.sample(range(len(poblacion_hijos)), cantidad_de_hijos)

    return indices_a_mutar

# Función para realizar la mutación en la población de hijos
def mutar(poblacion_hijos):
    # Genera los índices de los hijos que se van a mutar
    indices_a_mutar = generar_indices(poblacion_hijos)

    # print("Indices")
    # print(indices_a_mutar)

    # Realiza la mutación en los hijos seleccionados
    for indice in indices_a_mutar:
        # Genera dos índices aleatorios distintos
        indice_1, indice_2 = random.sample(range(8), 2)
        # print("Indices aletorios")
        # print(indice_1, indice_2)

        # Intercambia los valores en las posiciones seleccionadas
        poblacion_hijos[indice, indice_1], poblacion_hijos[indice, indice_2] = poblacion_hijos[indice, indice_2], poblacion_hijos[indice, indice_1]

    return poblacion_hijos


""" DECENDENCIA """
#compara hijos y padres y selecciona a los mejores, los almacena en una matriz
def decendientes(poblacion_hijos, poblacion_padres):
    # Evaluar las poblaciones
    fitness_hijos = evaluar_poblacion(poblacion_hijos)
    fitness_padres = evaluar_poblacion(poblacion_padres)
    # Crear una matriz de descendencia del mismo tamaño que la población de hijos
    _decendientes = np.zeros_like(poblacion_hijos)
    # Iterar sobre los índices de los individuos
    for i in range(len(poblacion_hijos)):
        if fitness_hijos[i] > fitness_padres[i]:
            _decendientes[i] = poblacion_hijos[i]
        else:
            _decendientes[i] = poblacion_padres[i]
    return _decendientes




""" GENREACIOÓN """
poblacion_actual = generaPoblacion(10)
generaciones = 0

while generaciones < 30:
    descendientes_generados = cruza(poblacion_actual)
    descendientes_mutados = mutar(np.array(descendientes_generados))
    poblacion_actual = decendientes(descendientes_mutados, poblacion_actual)
    generaciones += 1
    # Evaluar si hay un individuo con fitness 0
    fitness_poblacion = evaluar_poblacion(poblacion_actual)
    for i, fitness in enumerate(fitness_poblacion):
        if fitness == 0:
            print(f"Se encontró un individuo con fitness 0 en la generación {generaciones}: {poblacion_actual[i]}")
            break
        # Si no se encuentra un individuo con fitness 0 después de 30 generaciones
        else:
            print("Se completaron 30 generaciones sin encontrar un individuo con fitness 0.")