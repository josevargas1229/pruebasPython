"""Python para ciencia de datos
En esta script empezamos a aprender sobre
las librerias pandas, numpy y Matplotlib.
Los instalamos y realizamos un ejercicio
tomando en cuenta el dataset de 
avocados.csv
"""
#Importamos las librerias
import pandas as pd
#import numpy as np
from matplotlib import pyplot as plt

#Leemos el csv
df = pd.read_csv("./data/avocado.csv")
#print(df.head(5))
#Seleccionamos solamente la región de Chicago
chicago=df[df["region"]=="Chicago"]

#Hacemos que el índice sea por fecha,
#en vez del por defecto que nos da pandas
chicago=chicago.set_index("Date")
#Ordenamos por la fecha
chicago=chicago.sort_values(by="Date")
#print(chicago.head(5))

#Grafico
#Numero de muestras
MAX_SAMPLE = 100

#Seleccionamos la cantidad de muestras
precio=chicago["AveragePrice"][:MAX_SAMPLE]
cantidad=chicago["Total Volume"][:MAX_SAMPLE]
#prepara el gráfico
plt.plot(precio,label="Precio Medio")
plt.plot(cantidad,label="Volumen total")
#Agregamos un título
plt.title("Precio de los aguacates vs tiempo")
#Leyenda para el eje X
plt.xlabel("Fecha")
#Rotas los valores del eje X
plt.xticks(rotation=90)
#Leyenda para el eje Y
plt.ylabel("Precio en $")
#Pone una leyenda en base al label en el .plot()
plt.legend()
#muestra el gráfico
plt.show()
