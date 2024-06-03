import base64
import hashlib
import os
import sqlite3
from datetime import datetime
from sqlite3 import Error

import pandas as pd


# _____________________________________________________________________________________________________________________

def obtener_conexion():
    try:
        conexion = sqlite3.connect('Base1')
        return conexion
    except Exception as e:
        print("Error al conectar con la base de datos:", e)
        return None


# _____________________________________________________________________________________________________________________
# IMPORTANTE: TABLA PARA CREAR USUARIOS

def crear_tabla_usuarios():
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            cedula TEXT NOT NULL,
            correo TEXT NOT NULL,
            celular TEXT NOT NULL,
            contrasena TEXT NOT NULL,
            imagen_perfil BLOB
        )
    ''')
    conexion.commit()


def agregar_usuario(nombre, nombre_completo, cedula, correo, celular, contrasena):
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()

        try:
            # Asegúrate de que la tabla esté creada
            crear_tabla_usuarios()

            # Agregar los nuevos campos a la base de datos
            cursor.execute(
                'INSERT INTO usuarios (nombre, nombre_completo, cedula, correo, celular, contrasena) VALUES (?, ?, ?, ?, ?, ?)',
                (nombre, nombre_completo, cedula, correo, celular, hashed_password))

            conexion.commit()
            print("Usuario registrado exitosamente.")
        except Exception as e:
            print(f"Error al registrar usuario: {str(e)}")
            conexion.rollback()


def obtener_usuario_por_nombre(nombre):
    usuario = None
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT nombre, contrasena FROM usuarios WHERE nombre = ?', (nombre,))
        usuario = cursor.fetchone()

    if usuario:
        user_data = {
            'nombre': usuario[0],
            'contrasena': usuario[1]
        }
        return user_data
    else:
        return None


# _____________________________________________________________________________________________________________________
# MODULO DE PERFIL DE USUARIO:
# IMAGENES DE PERFIL:
def actualizar_imagen_perfil_blob(nombre_usuario, nueva_imagen_blob):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('UPDATE usuarios SET imagen_perfil = ? WHERE nombre = ?',
                           (nueva_imagen_blob, nombre_usuario))
            conexion.commit()
        return True  # Indica éxito si la actualización se realizó sin errores
    except Exception as e:
        print("Error al actualizar la imagen de perfil:", e)
        return False  # Indica fallo si hubo algún problema durante la actualización


def obtener_imagen_perfil_blob(nombre_usuario):
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT imagen_perfil FROM usuarios WHERE nombre = ?', (nombre_usuario,))
        imagen = cursor.fetchone()

    if imagen and imagen[0] is not None:  # Verifica si la imagen existe y no es nula
        imagen_base64 = base64.b64encode(imagen[0]).decode('utf-8')
        return imagen_base64
    else:
        imagen_default = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAADIgAdh8pYwAAAABJRU5ErkJggg=='
        return imagen_default


def eliminar_imagen_perfil(nombre_usuario):
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute('UPDATE usuarios SET imagen_perfil = NULL WHERE nombre = ?', (nombre_usuario,))
        conexion.commit()


# <--ACTUALIZAR NOMBRE COMPLETO-->
def actualizar_nombre_completo(nombre_usuario, nuevo_nombre_completo):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('UPDATE usuarios SET nombre_completo = ? WHERE nombre = ?',
                           (nuevo_nombre_completo, nombre_usuario))
            conexion.commit()
        return True
    except Exception as e:
        print("Error al actualizar el nombre completo:", e)
        return False


# <--ACTUALIZAR CEDULA-->
def actualizar_cedula(nombre_usuario, nueva_cedula):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('UPDATE usuarios SET cedula = ? WHERE nombre = ?',
                           (nueva_cedula, nombre_usuario))
            conexion.commit()
        return True
    except Exception as e:
        print("Error al actualizar la cedula:", e)
        return False


# <--ACTUALIZAR CORREO-->
def actualizar_correo(nombre_usuario, nuevo_correo):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('UPDATE usuarios SET correo = ? WHERE nombre = ?',
                           (nuevo_correo, nombre_usuario))
            conexion.commit()
        return True
    except Exception as e:
        print("Error al actualizar el correo:", e)
        return False


# <--ACTUALIZAR NUMERO-->
def actualizar_celular(nombre_usuario, nuevo_celular):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('UPDATE usuarios SET celular = ? WHERE nombre = ?',
                           (nuevo_celular, nombre_usuario))
            conexion.commit()
        return True
    except Exception as e:
        print("Error al actualizar el celular:", e)
        return False


def obtener_datos_usuario(username):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('SELECT id, nombre_completo, cedula, correo, celular FROM usuarios WHERE nombre = ?',
                           (username,))
            usuario = cursor.fetchone()
        return usuario
    except Exception as e:
        # Manejar la excepción apropiadamente
        raise e


# CUIDADO: PARA VACIAR LA TABLA DE USUARIOS
def vaciar_tabla_usuarios():
    try:
        conexion = sqlite3.connect('Base1')
        cursor = conexion.cursor()
        cursor.execute('DELETE FROM usuarios')
        conexion.commit()
        conexion.close()
        print("La tabla usuarios ha sido vaciada.")
    except Exception as e:
        print("Error al vaciar la tabla usuarios:", e)


# vaciar_tabla_usuarios()


# _____________________________________________________________________________________________________________________
def crear_tabla():
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            imagen BLOB,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL
)
        ''')
        conexion.commit()


def insertar_producto(nombre, categoria, imagen, precio, cantidad):
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO productos (nombre, categoria, imagen, precio, cantidad)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, categoria, sqlite3.Binary(imagen), precio, cantidad))
        conexion.commit()


# Obtener productos con imágenes convertidas a base64
def obtener_productos(busqueda=None, categoria=None):
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        query = "SELECT * FROM productos WHERE 1 = 1"  # Establecer una condición inicial verdadera

        parametros = []  # Lista para almacenar los parámetros para la consulta SQL

        # Si hay una cadena de búsqueda, agregar filtro por nombre
        if busqueda:
            query += " AND (nombre LIKE ? OR id = ?)"
            parametros.extend(['%' + busqueda + '%', busqueda])

        # Si hay una categoría seleccionada, agregar filtro por categoría
        if categoria:
            query += " AND categoria = ?"
            parametros.append(categoria)

        productos = cursor.execute(query, parametros).fetchall()

        categorias = set(producto[2] for producto in productos)
        categorias = list(categorias)

        # Convertir imágenes a base64
        productos_dict = []
        for producto in productos:
            producto_dict = {
                "id": producto[0],
                "nombre": producto[1],
                "categoria": producto[2],
                "imagen": '',  # Establecer un valor predeterminado
                "tipo_imagen": '',  # Establecer un valor predeterminado
                "precio": producto[4],
                "cantidad": producto[5]
            }
            # Verificar si la imagen no es None antes de intentar convertirla a base64
            if producto[3] is not None:
                producto_dict["imagen"] = base64.b64encode(producto[3]).decode('utf-8')  # Convertir bytes a base64
                producto_dict["tipo_imagen"] = obtener_tipo_imagen(producto[3])  # Obtener el tipo de imagen

            productos_dict.append(producto_dict)

        return productos_dict, categorias


def obtener_tipo_imagen(imagen_bytes):
    extensiones_permitidas = {'.jpg', '.jpeg', '.png', '.gif'}
    _, extension = os.path.splitext(imagen_bytes)
    if extension.lower() in extensiones_permitidas:
        return extension.lower()[1:]  # Eliminar el punto inicial
    else:
        return 'jpg'  # Puedes establecer un valor predeterminado o manejarlo según sea necesario


# _____________________________________________________________________________________________________________________
# IMPORTANTE: PARA MODULOS DE TIENDA
def crear_tabla_carrito():
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carrito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                imagen BLOB,
                precio REAL NOT NULL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            )
        ''')
        conexion.commit()


def obtener_cantidad_en_carrito(id_usuario, id_producto):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(cantidad) FROM carrito WHERE id_usuario = ? AND id_producto = ?',
                       (id_usuario, id_producto))
        cantidad_en_carrito = cursor.fetchone()[0]

        if cantidad_en_carrito is None:
            return 0
        else:
            return cantidad_en_carrito

    except Exception as e:
        print(f"Error al obtener cantidad en carrito del usuario {id_usuario} para el producto {id_producto}: {e}")
        return 0


def obtener_cantidad_disponible(id_producto):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute('SELECT cantidad FROM productos WHERE id = ?', (id_producto,))
        cantidad_disponible = cursor.fetchone()[0]

        # Manejar el caso en que cantidad_disponible sea None
        if cantidad_disponible is None:
            return 0
        else:
            return cantidad_disponible

    except Exception as e:
        print(f"Error al obtener cantidad disponible del producto {id_producto}: {e}")
        return 0


def agregar_producto_al_carrito(id_usuario, id_producto, cantidad):
    try:
        conn = sqlite3.connect('Base1')
        cursor = conn.cursor()

        cursor.execute('SELECT nombre, categoria, precio, imagen FROM productos WHERE id = ?', (id_producto,))
        producto_info = cursor.fetchone()
        nombre_producto, categoria_producto, precio_producto, imagen_producto = producto_info

        cursor.execute(
            'INSERT INTO carrito (id_usuario, id_producto, cantidad, nombre, categoria, precio, imagen) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (id_usuario, id_producto, cantidad, nombre_producto, categoria_producto, precio_producto, imagen_producto))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print("Error al agregar producto al carrito:", e)
        return False


def agregar_al_carrito_db(id_usuario, id_producto, cantidad):
    cantidad_disponible = obtener_cantidad_disponible(id_producto)

    if cantidad_disponible > 0:
        cantidad_en_carrito = obtener_cantidad_en_carrito(id_usuario, id_producto)

        if cantidad_en_carrito == 0:
            try:
                agregado_exitosamente = agregar_producto_al_carrito(id_usuario, id_producto, cantidad)
                if agregado_exitosamente:
                    return True, 'Producto agregado al carrito correctamente'
                else:
                    return False, 'Error al agregar producto al carrito'
            except Exception as e:
                print("Error al agregar producto al carrito:", str(e))
                return False, 'Error interno al agregar producto al carrito'
        else:
            return False, 'El producto ya está en el carrito'
    else:
        return False, 'Producto no disponible'


def obtener_productos_del_carrito(id_usuario):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.id, p.nombre, p.categoria, p.imagen, p.precio, c.cantidad
            FROM carrito c
            JOIN productos p ON c.id_producto = p.id
            WHERE c.id_usuario = ?
        ''', (id_usuario,))

        productos_carrito = cursor.fetchall()

        productos_en_carrito = []
        for producto in productos_carrito:
            precio_total = producto[4] * producto[5]  # Calculamos el precio total por producto
            producto_dict = {
                "id": producto[0],
                "nombre": producto[1],
                "categoria": producto[2],
                "imagen": base64.b64encode(producto[3]).decode('utf-8'),  # Convertir bytes a base64
                "tipo_imagen": obtener_tipo_imagen(producto[3]),  # Obtener el tipo de imagen
                "precio": producto[4],
                "cantidad": producto[5],
                "precio_total": precio_total  # Agregamos el precio_total al diccionario del producto
            }
            productos_en_carrito.append(producto_dict)

        conn.close()
        return productos_en_carrito

    except Exception as e:
        print("Error al obtener productos del carrito:", e)
        return []


def ajustar_cantidad_en_carrito(id_usuario, id_producto, nueva_cantidad):
    try:
        # Verificar si la nueva cantidad es válida
        if nueva_cantidad < 0:
            return False, 'La cantidad ingresada es inválida'

        # Obtener la cantidad disponible del producto desde la base de datos
        cantidad_disponible = obtener_cantidad_disponible(id_producto)

        # Verificar si la cantidad disponible es menor a la nueva cantidad
        if cantidad_disponible < nueva_cantidad:
            return False, 'La cantidad excede la disponibilidad'

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            # Obtener el precio unitario del producto
            cursor.execute('SELECT precio FROM productos WHERE id = ?', (id_producto,))
            precio_unitario = cursor.fetchone()[0]

            # Obtener la cantidad actual del producto en el carrito
            cursor.execute('SELECT cantidad FROM carrito WHERE id_usuario = ? AND id_producto = ?',
                           (id_usuario, id_producto))
            cantidad_actual = cursor.fetchone()[0]

            # Calcular el precio total actual del producto en el carrito
            precio_total_actual = precio_unitario * cantidad_actual

            # Calcular el nuevo precio total en función de la nueva cantidad
            nuevo_precio_total = precio_unitario * nueva_cantidad

            # Actualizar la cantidad y el precio total del producto en el carrito
            cursor.execute('''
                UPDATE carrito
                SET cantidad = ?, precio = ?
                WHERE id_usuario = ? AND id_producto = ?
            ''', (nueva_cantidad, nuevo_precio_total, id_usuario, id_producto))

            conexion.commit()

            print(f"Cantidad del producto {id_producto} ajustada a {nueva_cantidad} en el carrito.")
            return True, f'Cantidad ajustada a {nueva_cantidad}'

    except Exception as e:
        print("Error al ajustar la cantidad:", e)
        return False, 'Error interno del servidor'


def eliminar_producto_del_carrito(id_usuario, id_producto):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                DELETE FROM carrito
                WHERE id_producto = ? AND id_usuario = ?
            ''', (id_producto, id_usuario))
            conexion.commit()

            print(f"Producto {id_producto} eliminado del carrito.")

        return True  # Se eliminó exitosamente

    except Exception as e:
        print("Error al eliminar el producto del carrito:", e)
        return False  # Hubo un error al eliminar el producto del carrito


def limpiar_carrito():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM carrito")
            conexion.commit()
            print("Carrito limpiado después de la compra.")
    except Exception as e:
        print("Error al limpiar el carrito:", e)


# _____________________________________________________________________________________________________________________
# FUNCIONES PARA ACTUALIZAR INVENTARIO:

def exportar_datos_excel():
    try:
        with obtener_conexion() as conexion:
            if conexion:
                query = "SELECT * FROM productos;"
                df = pd.read_sql_query(query, conexion)

                excel_file = "Datos_de_Base1.xlsx"
                df.to_excel(excel_file, index=False)

                return excel_file

    except Exception as e:
        print("Error de SQLite al exportar datos:", e)

    return None


def importar_datos_excel(archivo_excel):
    success = False
    try:
        if archivo_excel is None or archivo_excel.filename == '':
            return "No se ha seleccionado ningún archivo."

        df = pd.read_excel(archivo_excel)

        if df.empty:
            return "El archivo está vacío."

        with obtener_conexion() as conexion:
            for index, row in df.iterrows():
                # Verificar si la columna de imagen es None o está vacía
                imagen = row.get('imagen')
                if pd.isnull(imagen) or imagen == '':
                    # Si no hay imagen, asignar None
                    imagen_bytes = None

                # Insertar los datos en la base de datos
                cursor = conexion.cursor()
                cursor.execute('''
                    INSERT INTO productos (nombre, categoria, imagen, precio, cantidad)
                    VALUES (?, ?, ?, ?, ?)
                ''', (row['nombre'], row['categoria'], imagen_bytes, row['precio'], row['cantidad']))

            conexion.commit()

        success = True
        return success
    except pd.errors.ParserError as pe:
        print("Error al analizar el archivo Excel:", pe)
        return success  # Devuelve el valor actual de la bandera success
    except Exception as e:
        print("Error al importar datos:", e)
        return success  # Devuelve el valor actual de la bandera success


def actualizar_cantidades_bd(data):
    try:

        cantidades = data['cantidades']

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            for producto in cantidades:
                cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (producto['cantidad'], producto['id']))

            # Actualizar el carrito después de actualizar el inventario
            for producto in cantidades:
                cursor.execute("UPDATE carrito SET cantidad = 0 WHERE id_producto = ? AND cantidad > ?",
                               (producto['id'], producto['cantidad']))

            conexion.commit()

        return {'message': 'Cantidades actualizadas exitosamente'}
    except Exception as e:
        print('Error en el servidor:', str(e))
        return {'error': str(e)}


def actualizar_precios_bd(data):
    try:
        precios = data['precios']

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            for producto in precios:
                cursor.execute("UPDATE productos SET precio = ? WHERE id = ?", (producto['precio'], producto['id']))

            conexion.commit()

        return {'message': 'Precios actualizados exitosamente'}
    except Exception as e:
        print('Error en el servidor:', str(e))
        return {'error': str(e)}


def actualizar_categorias_bd(product_id, nueva_categoria):
    try:
        # Obtener la categoría actual antes de la actualización
        conexion = sqlite3.connect('Base1')
        cursor = conexion.cursor()

        cursor.execute("SELECT categoria FROM productos WHERE id = ?", (product_id,))
        categoria_anterior = cursor.fetchone()[0]

        # Actualizar la categoría en la tabla de productos
        cursor.execute("UPDATE productos SET categoria = ? WHERE id = ?", (nueva_categoria, product_id))
        conexion.commit()
        conexion.close()

        # Obtener la categoría después de la actualización
        conexion = sqlite3.connect('Base1')
        cursor = conexion.cursor()

        cursor.execute("SELECT categoria FROM productos WHERE id = ?", (product_id,))
        categoria_actual = cursor.fetchone()[0]

        conexion.close()

        # Llamar a la función para actualizar la categoría en el carrito después de actualizar en productos
        resultado_carrito = actualizar_carrito_despues_de_actualizar_categoria(product_id, nueva_categoria)

        print("Categoría anterior en productos:", categoria_anterior)
        print("Categoría actual en productos:", categoria_actual)
        print("Resultado de la actualización del carrito:", resultado_carrito)

        return {'message': 'Categoría actualizada exitosamente'}
    except sqlite3.Error as e:
        print('Error en la base de datos:', str(e))
        return {'message': 'Hubo un error al actualizar la categoría en la base de datos'}


def eliminar_producto_db(producto_id):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conexion.commit()

        return {'message': 'Producto eliminado exitosamente'}
    except Exception as e:
        return {'error': str(e)}


def actualizar_imagen_producto(id_producto, nueva_imagen):
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            UPDATE productos
            SET imagen = ?
            WHERE id = ?
        ''', (sqlite3.Binary(nueva_imagen), id_producto))
        conexion.commit()


def actualizar_nombre_bd(data):
    try:
        nombres_actualizados = data.get('nombres')

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            for producto in nombres_actualizados:
                producto_id = producto.get('id')
                nuevo_nombre = producto.get('nombre')
                cursor.execute("UPDATE productos SET nombre = ? WHERE id = ?", (nuevo_nombre, producto_id))
            conexion.commit()

        return {'message': 'Nombres actualizados exitosamente'}
    except Exception as e:
        print('Error en el servidor:', str(e))
        return {'error': str(e)}


# _____________________________________________________________________________________________________________________
# ESTAS FUNCIONES VIENEN A LA PAR CON LO DE ARRIBA, SON PARA ACTUALIZAR EL CARRITO EN LA BASE DE DATOS PARA FUTURAS COMPRAS

def actualizar_carrito_despues_de_actualizar_categoria(product_id, nueva_categoria):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            # Actualizar la categoría en el carrito basado en el cambio en los productos
            cursor.execute("UPDATE carrito SET categoria = ? WHERE id_producto = ?", (nueva_categoria, product_id))

            conexion.commit()

        return {'message': 'Carrito actualizado después de actualizar categoría'}
    except Exception as e:
        print('Error al actualizar el carrito después de actualizar categoría:', str(e))
        return {'error': 'Error interno del servidor'}


def actualizar_carrito_despues_de_actualizar_precio(product_id, nuevo_precio):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE carrito SET precio = (SELECT precio * cantidad FROM carrito WHERE id_producto = ?) WHERE id_producto = ?",
                (product_id, product_id))
            conexion.commit()
        return {'message': 'Carrito actualizado después de actualizar el precio en productos'}
    except Exception as e:
        print('Error al actualizar el carrito después de actualizar el precio:', str(e))
        return {'error': 'Error interno al actualizar el carrito después de actualizar el precio'}


def actualizar_carrito_despues_de_actualizar_inventario(data):
    try:
        productos_actualizados = data.get('productos', [])

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            for producto in productos_actualizados:
                id_producto = producto.get('id')
                nueva_cantidad = producto.get('nueva_cantidad')

                # Si la cantidad disponible se reduce, ajustar el carrito si la cantidad supera la nueva disponibilidad
                if nueva_cantidad is not None:
                    cursor.execute("UPDATE carrito SET cantidad = 0 WHERE id_producto = ? AND cantidad > ?",
                                   (id_producto, nueva_cantidad))

            conexion.commit()

        return {'message': 'Carrito actualizado después de actualizar inventario'}
    except Exception as e:
        print('Error al actualizar el carrito después de actualizar inventario:', str(e))
        return {'error': 'Error interno del servidor'}


# _____________________________________________________________________________________________________________________
# IMPORTANTE: TABLA PARA PRODUCTOS COMPRADOS
def crear_tabla_productos_comprados():
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos_comprados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                nombre_producto TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                precio_total REAL NOT NULL,
                fecha_compra DATE NOT NULL,
                hora_compra TIME NOT NULL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            )
        ''')
        conexion.commit()


def realizar_compra_en_bd(id_usuario):
    try:
        # Obtener los productos en el carrito del usuario actual
        productos_en_carrito = obtener_productos_del_carrito(id_usuario)

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            total_precio_compra = 0  # Inicializar el total del precio de la compra

            for producto in productos_en_carrito:
                id_producto = producto['id']
                nombre_producto = producto['nombre']
                cantidad = producto['cantidad']
                precio_unitario = producto['precio']

                # Verificar si la cantidad está disponible
                cantidad_disponible = obtener_cantidad_disponible(id_producto)

                if cantidad <= cantidad_disponible:
                    # Calcular el precio total y almacenar los datos en la tabla de productos comprados
                    precio_total = precio_unitario * cantidad
                    total_precio_compra += precio_total  # Sumar al total de la compra

                    # Obtener la fecha y hora por separado
                    fecha_actual = datetime.now()
                    fecha_compra = fecha_actual.strftime("%Y-%m-%d")
                    hora_compra = fecha_actual.strftime("%H:%M:%S")

                    cursor.execute(
                        'INSERT INTO productos_comprados (id_usuario, id_producto, nombre_producto, cantidad, precio_unitario, precio_total, fecha_compra, hora_compra) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        (
                            id_usuario, id_producto, nombre_producto, cantidad, precio_unitario, precio_total,
                            fecha_compra, hora_compra)
                    )
                    # Restar la cantidad comprada del carrito
                    cursor.execute('''
                        UPDATE carrito
                        SET cantidad = cantidad - ?
                        WHERE id_producto = ?
                    ''', (cantidad, id_producto))

                    # Actualizar la cantidad disponible en la tabla de productos
                    cursor.execute('''
                        UPDATE productos
                        SET cantidad = cantidad - ?
                        WHERE id = ?
                    ''', (cantidad, id_producto))

                    print(
                        f"Producto {nombre_producto} comprado: {cantidad} unidades, precio por unidad: {precio_unitario}.")

                else:
                    print(f"No hay suficientes unidades de {nombre_producto} para completar la compra.")

            print(f"Total de la compra: ${total_precio_compra}")  # Mostrar el total de la compra
            conexion.commit()

        limpiar_carrito()
        return True

    except Exception as e:
        print(f"Error al realizar la compra: {e}")
        return False


def obtener_productos_comprados_por_usuario(id_usuario):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT id_producto, nombre_producto, cantidad, precio_unitario, precio_total, fecha_compra, hora_compra
                FROM productos_comprados
                WHERE id_usuario = ?
            ''', (id_usuario,))
            productos_comprados = cursor.fetchall()
            return productos_comprados

    except Exception as e:
        print(f"Error al obtener productos comprados por el usuario: {e}")
        return None


# _____________________________________________________________________________________________________________________
# PRODUCTOS VENDIDOS
def obtener_productos_vendidos():
    try:
        conexion = sqlite3.connect('Base1')
        cursor = conexion.cursor()

        query = '''
            SELECT id, id_usuario ,nombre_producto, cantidad, precio_unitario, precio_total, fecha_compra, hora_compra
            FROM productos_comprados
        '''

        cursor.execute(query)
        productos_vendidos = cursor.fetchall()

        conexion.close()
        return productos_vendidos

    except Exception as e:
        print(f"Error al obtener productos vendidos: {str(e)}")
        return []


# _____________________________________________________________________________________________________________________
# GRAFICAS:
def obtener_datos_graficos():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            # Obtener datos para el gráfico de pastel
            cursor.execute('SELECT categoria, SUM(cantidad) FROM productos GROUP BY categoria')
            resultados_pastel = cursor.fetchall()
            labels_pastel = [resultado[0] for resultado in resultados_pastel]
            data_pastel = [resultado[1] for resultado in resultados_pastel]

            # Obtener datos para el gráfico de barras
            cursor.execute('SELECT fecha_compra, SUM(precio_total) FROM productos_comprados GROUP BY fecha_compra')
            resultados_barras = cursor.fetchall()
            fechas_barras = [str(resultado[0]) for resultado in resultados_barras]
            precios_totales_barras = [resultado[1] for resultado in resultados_barras]

            # obtener datos para el grafico de barras productos
            cursor.execute('SELECT nombre_producto, SUM(cantidad) FROM productos_comprados GROUP BY nombre_producto')
            resultados_barras_pro = cursor.fetchall()
            nombres_barras = [resultado[0] for resultado in resultados_barras_pro]
            cantidades_barras = [resultado[1] for resultado in resultados_barras_pro]

            return labels_pastel, data_pastel, fechas_barras, precios_totales_barras, nombres_barras, cantidades_barras

    except Error as e:
        print(f"Error en la aplicación: {str(e)}")
        return None, None, None, None


def obtener_datos_graficos_productos_vendidos():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            # Obtener datos para el nuevo gráfico de barras (total de gastos por usuario)
            cursor.execute('SELECT id_usuario, SUM(precio_total) FROM productos_comprados GROUP BY id_usuario')
            resultados_gastos = cursor.fetchall()
            usuarios_gastos = [resultado[0] for resultado in resultados_gastos]
            total_gastos = [resultado[1] for resultado in resultados_gastos]

            print(resultados_gastos)

            return usuarios_gastos, total_gastos


    except Error as e:
        print(f"Error en la aplicación: {str(e)}")
        return None, None


# _____________________________________________________________________________________________________________________
# REGISTRO DE CLIENTES
def registrar_cliente(nombre, correo, telefono, direccion):
    if nombre and correo and telefono:
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()
                cursor.execute('INSERT INTO clientes (nombre, correo, telefono, direccion) VALUES (?, ?, ?, ?)',
                               (nombre, correo, telefono, direccion))
                conexion.commit()
                return True

        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    return False


# _____________________________________________________________________________________________________________________
# PARA REGISTRO DE USUARIOS:

def obtener_usuarios_registrados():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute('SELECT id, nombre, nombre_completo, cedula, correo, celular, imagen_perfil FROM usuarios')
            usuarios = cursor.fetchall()
        return usuarios
    except Exception as e:
        raise e


def buscar_usuarios(busqueda=None):
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            query = "SELECT * FROM usuarios WHERE 1 = 1"  # Establecer una condición inicial verdadera

            parametros = []  # Lista para almacenar los parámetros para la consulta SQL

            # Si hay una cadena de búsqueda, agregar filtro por nombre o cualquier campo que desees buscar
            if busqueda:
                query += " AND (nombre LIKE ? OR nombre_completo LIKE ? OR correo LIKE ?)"  # Expandir según los campos deseados
                busqueda_param = '%' + busqueda + '%'
                parametros.extend(
                    [busqueda_param, busqueda_param, busqueda_param])  # Agregar la búsqueda a los parámetros

            cursor.execute(query, parametros)
            usuarios = cursor.fetchall()

            # Convertir la información de los usuarios a una lista de diccionarios
            usuarios_dict = []
            for usuario in usuarios:
                usuario_dict = {
                    "id": usuario[0],
                    "nombre": usuario[1],
                    "nombre_completo": usuario[2],
                    "cedula": usuario[3],
                    "correo": usuario[4],
                    "celular": usuario[5]
                    # Agrega más campos si son necesarios
                }
                usuarios_dict.append(usuario_dict)

            return usuarios_dict
    except Exception as e:
        print(f"Error al buscar usuarios: {str(e)}")
        return []


# _____________________________________________________________________________________________________________________
# CREACION DE TABLAS

crear_tabla_usuarios()
crear_tabla()
crear_tabla_carrito()
crear_tabla_productos_comprados()
