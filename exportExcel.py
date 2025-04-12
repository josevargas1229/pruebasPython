import pandas as pd
from sqlalchemy import create_engine
import numpy as np
# Configuración de la conexión a MySQL
DB_USER = 'root'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_NAME = 'bdpos1'

# Crear el motor de conexión
engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

# Función para cargar datos a una tabla específica, verificando columnas
def cargar_datos(df, table_name, columns):
    try:
        # Filtrar el DataFrame solo con las columnas esperadas
        df = df[columns]
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f'Datos insertados en la tabla {table_name} correctamente.')
    except Exception as e:
        print(f'Error al insertar datos en la tabla {table_name}: {e}')

# Columnas esperadas
categorias_columns = ['CategoriaID','Nombre', 'Descripcion', 'Activo']
tipos_columns = ['TipoID','Nombre', 'Activo']
marcas_columns = ['MarcaID','Nombre', 'Activo']
productos_columns = ['ProductoID','CategoriaID', 'TipoID', 'MarcaID', 'UnidadMedidaID', 'Stock', 'StockMinimo']
presentaciones_columns = [
    'PresentacionID',
    'ProductoID',
    'CodigoBarras',
    'Nombre',
    'Descripcion',
    'EquivalenciaEnUnidadesBase'
    ]

# Cargar datos de los archivos Excel
# 1. Categorías (Familias)
df_categorias = pd.read_excel('FAMILIAS.xlsx')
df_categorias.rename(columns={
    'id Familia': 'CategoriaID',
    'Familia': 'Nombre',
    'Activo': 'Activo',
    'Descripcion': 'Descripcion'
}, inplace=True)
df_categorias['Activo'] = True
df_categorias['Descripcion'] = None 
cargar_datos(df_categorias, 'categorias', categorias_columns)

# 2. Tipos (Subfamilias)
df_tipos = pd.read_excel('SUBFAMILIAS.xlsx')
df_tipos.rename(columns={
    'id Sub Familia': 'TipoID',
    'Sub Familia': 'Nombre',
    'Activo': 'Activo'
}, inplace=True)
df_tipos['Activo'] = True
cargar_datos(df_tipos, 'tipos', tipos_columns)

# 3. Marcas
df_marcas = pd.read_excel('MARCAS.xlsx')
df_marcas.rename(columns={
    'id Marca': 'MarcaID',
    'Marca': 'Nombre',
    'Activo': 'Activo'
}, inplace=True)
df_marcas['Activo'] = True
cargar_datos(df_marcas, 'marcas', marcas_columns)

# 4. Productos y Presentaciones
df_productos = pd.read_excel('PRODUCTOS 29 JUN.xlsx')
proveedores_unicos = df_productos['Proveedor'].dropna().unique().tolist()

# Añadir el proveedor "Desconocido" para aquellos productos sin proveedor
proveedores_unicos.append("Desconocido")

# Crear un DataFrame con la estructura para la tabla de proveedores
df_proveedores = pd.DataFrame({
    'ProveedorID': pd.RangeIndex(start=1, stop=len(proveedores_unicos) + 1, step=1),
    'Nombre': proveedores_unicos,
    'Contacto': None,
    'Telefono': None,
    'Email': None,
    'Direccion': None,
    'Ciudad': None,
    'Estado': None,
    'CodigoPostal': None,
    'RFC': None,
    'Notas': None,
    'CondicionesPago': None,
    'FechaRegistro': pd.to_datetime('today'),
    'Activo': 1
})

# Cargar los datos en la tabla proveedores
try:
    df_proveedores.to_sql('proveedores', con=engine, if_exists='append', index=False)
    print("Datos de proveedores insertados correctamente.")
except Exception as e:
    print(f"Error al insertar datos en la tabla proveedores: {e}")

# Renombrar las columnas para que coincidan con las que esperamos
df_productos.rename(columns={
    'id Producto': 'PresentacionID',
    'Codigo': 'CodigoBarras',
    'Descripcion': 'Nombre',
    'Piezas Presentacion1': 'EquivalenciaEnUnidadesBase',
    'Familia': 'CategoriaID',
    'Marca': 'MarcaID',
    'sub Familia': 'TipoID',
    'Precio': 'Precio2',
    'Precio2': 'Precio'
}, inplace=True)

# Mapear nombres a IDs para CategoriaID, TipoID y MarcaID
categorias_dict = pd.read_sql("SELECT CategoriaID, Nombre FROM categorias", con=engine).set_index('Nombre')['CategoriaID'].to_dict()
tipos_dict = pd.read_sql("SELECT TipoID, Nombre FROM tipos", con=engine).set_index('Nombre')['TipoID'].to_dict()
marcas_dict = pd.read_sql("SELECT MarcaID, Nombre FROM marcas", con=engine).set_index('Nombre')['MarcaID'].to_dict()

# Asignar los valores mapeados a las columnas de IDs
df_productos['CategoriaID'] = df_productos['CategoriaID'].map(categorias_dict)
df_productos['TipoID'] = df_productos['TipoID'].map(tipos_dict)
df_productos['MarcaID'] = df_productos['MarcaID'].map(marcas_dict)
df_productos['UnidadMedidaID'] = 3  # Asignación fija para UnidadMedidaID

# Calcular el stock total agrupando por CategoriaID, TipoID y MarcaID
df_stock = df_productos.groupby(['CategoriaID', 'TipoID', 'MarcaID'], as_index=False)['Existencia P1'].sum()
df_stock.rename(columns={'Existencia P1': 'Stock'}, inplace=True)

# Preparar DataFrame de productos único para la tabla productos
df_productos_unique = df_stock.copy()
df_productos_unique['UnidadMedidaID'] = 3  # Asignar el valor fijo de UnidadMedidaID aquí
df_productos_unique['StockMinimo'] = 0  # Asignar un valor fijo o según lo que necesites
df_productos_unique = df_productos_unique.reset_index(drop=True)
# Añadir ID incremental desde 1 en df_productos
df_productos_unique['ProductoID'] = pd.RangeIndex(start=1, stop=len(df_productos_unique) + 1, step=1)

# Preparar DataFrame para la tabla presentaciones, asignando el ProductoID de df_productos_unique
df_presentaciones = df_productos.merge(df_productos_unique[['CategoriaID', 'TipoID', 'MarcaID', 'UnidadMedidaID', 'ProductoID']],
                                    on=['CategoriaID', 'TipoID', 'MarcaID', 'UnidadMedidaID'],
                                    how='left')
# Añadir ProductoID en df_presentaciones
df_presentaciones = df_presentaciones[['PresentacionID', 'ProductoID', 'CodigoBarras', 'Nombre', 'EquivalenciaEnUnidadesBase']].drop_duplicates()
print(df_productos_unique.head())
# Ahora cargar los datos de productos
cargar_datos(df_productos_unique[['ProductoID','CategoriaID', 'TipoID', 'MarcaID', 'UnidadMedidaID', 'Stock', 'StockMinimo']], 'productos', productos_columns)

# Identificar duplicados en la columna CodigoBarras
duplicados_codigos = df_presentaciones[df_presentaciones.duplicated(['CodigoBarras'], keep=False)]

# Guardar duplicados en un archivo para revisión
duplicados_codigos.to_excel('duplicados_codigos_barras.xlsx', index=False)
print("Archivo con códigos de barras duplicados creado: duplicados_codigos_barras.xlsx")

# Crear un sufijo único para los duplicados en CodigoBarras
df_presentaciones['CodigoBarras'] = np.where(
    df_presentaciones.duplicated('CodigoBarras', keep=False),
    df_presentaciones['CodigoBarras'] + "_" + df_presentaciones.groupby('CodigoBarras').cumcount().astype(str),
    df_presentaciones['CodigoBarras']
)
# Ahora cargar los datos a la tabla presentaciones
df_presentaciones['Descripcion'] = None
print(df_presentaciones.head())
cargar_datos(df_presentaciones, 'presentaciones', presentaciones_columns)
df_precios = df_productos[['PresentacionID', 'Precio']].copy()

# Asignar valores a cantidad mínima y máxima
df_precios['CantidadMinima'] = 0
df_precios['CantidadMaxima'] = 1

# Añadir un ID incremental para PrecioID
df_precios['PrecioID'] = pd.RangeIndex(start=1, stop=len(df_precios) + 1, step=1)

# Reordenar columnas para que coincidan con la estructura de la tabla precios
df_precios = df_precios[['PrecioID', 'PresentacionID', 'CantidadMinima', 'CantidadMaxima', 'Precio']]

# Cargar los datos en la tabla precios
try:
    df_precios.to_sql('precios', con=engine, if_exists='append', index=False)
    print("Datos de precios insertados correctamente.")
except Exception as e:
    print(f"Error al insertar datos en la tabla precios: {e}")
print("Importación de datos completada.")
