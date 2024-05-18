"""
En este script trabajamos con la libreria Matplotlib.
En concreto, trabajamos con subplots.

Los subplots nos permiten trabajar con múltiples
ejes en una misma figura. De esta forma, podemos
graficar varias funciones en ejes distintos.

"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("./data/avocado.csv")
atlanta = df[ df["region"] == "Atlanta" ]

precio = atlanta["AveragePrice"]
"""
-Rolling, aplica una ventana deslizante de n muestras
-Mean, aplica la media a los datos
-Con esto reducimos la oscilacion entre los datos
-min_periods, aplica la media a partir del primer valor
sin esto, tendríamos que esperar a que pasen las primeras
30 muestras para que pueda empezar a promediar
"""
precio_promediado = precio.rolling(30,min_periods=1).mean()

volumen = atlanta["Total Volume"]

bolsasAguacate = atlanta["Total Bags"]
sbolsas = atlanta["Small Bags"]
lbolsas = atlanta["Large Bags"]
xlbolsas = atlanta["XLarge Bags"]
#El subplot divide la pantalla de la figura
#(filas,columnas,index(posicion))
plt.subplot(2,2,1)
#titulo del grafico
plt.title("Precio Aguacate")
#datos a mostrar
plt.plot(precio,label="Precio",color="green")
plt.plot(precio_promediado,label="Precio Promediado",color="orange")
plt.legend()

plt.subplot(2,2,2)
plt.title("Volumen de Aguacates")
plt.plot(volumen,label="Volumen Total", color="red")
plt.legend()

plt.subplot(2,2,3)
plt.title("Bolsas Totales de Aguacates")
plt.plot(bolsasAguacate,label="Bolsas Totales", color="blue")
plt.legend()

plt.subplot(2,2,4)
plt.title("Bolsas por Tamaño")
plt.plot(sbolsas,label="Bolsas - S", color="black")
plt.plot(lbolsas,label="Bolsas - L", color="cyan")
plt.plot(xlbolsas,label="Bolsas - XL", color="yellow")
plt.legend()

#Espacia los diferentes elementos para que no se sobrepongan
plt.tight_layout()
plt.show()
