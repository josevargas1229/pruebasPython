"""
Un programa que hace un archivo de texto
con los numeros del 1 al 100
"""

# Abre el archivo en modo escritura
with open('texto.txt', 'w', encoding='utf-8') as file:
    # Crea una lista de números del 1 al 100
    numeros = list(range(1, 101))

    # Convierte los números a una cadena de texto y los escribe en el archivo
    for numero in numeros:
        file.write(f"{numero}\n")
    # Asegúrate de que el archivo termina con una nueva línea
    file.write("\n")
