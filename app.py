# CREACIÓN DE LA APLICACIÓN FLASK
import hashlib
import os
import traceback
from decimal import Decimal
from functools import wraps

from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify

from Bases_datos.conexion_sqlite import insertar_producto, agregar_al_carrito_db, obtener_productos_del_carrito, \
    realizar_compra_en_bd, \
    ajustar_cantidad_en_carrito, eliminar_producto_del_carrito, limpiar_carrito, agregar_usuario, crear_tabla_usuarios, \
    obtener_usuario_por_nombre, exportar_datos_excel, importar_datos_excel, actualizar_cantidades_bd, \
    eliminar_producto_db, actualizar_precios_bd, actualizar_categorias_bd, obtener_productos, \
    actualizar_carrito_despues_de_actualizar_categoria, actualizar_carrito_despues_de_actualizar_precio, \
    actualizar_carrito_despues_de_actualizar_inventario, obtener_datos_graficos, \
    obtener_productos_comprados_por_usuario, obtener_productos_vendidos, actualizar_imagen_producto, \
    actualizar_nombre_bd, obtener_imagen_perfil_blob, actualizar_imagen_perfil_blob, eliminar_imagen_perfil, \
    obtener_datos_graficos_productos_vendidos, obtener_usuarios_registrados, buscar_usuarios, \
    actualizar_nombre_completo, actualizar_cedula, actualizar_correo, actualizar_celular, obtener_datos_usuario


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'


first_request = True


def with_username(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            username = session['user_id']

            return func(username=username, *args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrapper


# _____________________________________________________________________________________________________________________
# INICIO DE SESION

@app.route('/registro_usuario', methods=['POST'])
def registro_usuario():
    nuevo_usuario = request.form.get('nombre')
    nombre_completo = request.form.get('nombre_completo')
    cedula = request.form.get('cedula')
    correo = request.form.get('correo')
    celular = request.form.get('celular')
    nueva_contrasena = request.form.get('contrasena')

    # Verificar que los campos no estén vacíos
    if not all([nuevo_usuario, nombre_completo, cedula, correo, celular, nueva_contrasena]):
        return jsonify({'success': False, 'message': 'Por favor completa todos los campos'})

    try:
        crear_tabla_usuarios()
        agregar_usuario(nuevo_usuario, nombre_completo, cedula, correo, celular, nueva_contrasena)
        return jsonify({'success': True, 'message': 'Usuario registrado exitosamente'})
    except Exception as e:
        print(f"Error al registrar usuario: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al registrar usuario'})


# _____________________________________________________________________________________________________________________
# RUTA DE LA PAGINA DE INICIO
@app.route('/')
def login():
    return render_template('login.html')


# _____________________________________________________________________________________________________________________
# RUTA PARA EL MANEJO DE LOS DATOS DE INICIO DE SESIÓN
@app.before_request
def load_session():
    global first_request
    if first_request:
        user_id = session.get('user_id')
        if user_id:
            user_data = obtener_usuario_por_nombre(user_id)
            if user_data:
                session['user_data'] = user_data
            else:
                session.pop('user_id')
        first_request = False


@app.route('/login', methods=['POST', 'GET'])
def login_post():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            print(f"Datos recibidos - Usuario: {username}, Contraseña: {password}")

            # Obtener datos del usuario por su nombre de la base de datos
            user_data = obtener_usuario_por_nombre(username)

            if user_data:
                stored_password = user_data['contrasena']
                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                if hashed_password == stored_password:
                    session['user_id'] = username
                    session['message'] = f"Bienvenido, {username}!"
                    print("Redirigiendo al index...")

                    return redirect(url_for('index'))

            return render_template('login.html', error="Usuario o contraseña incorrectos")
        except Exception as e:
            print("Error:", e)
            return "Internal Server Error"
    else:
        return render_template('login.html')


# Función para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/clear_session_message', methods=['POST'])
def clear_session_message():
    session.pop('message', None)
    return '', 204  # Respuesta vacía con código de estado 204 para indicar éxito


# _____________________________________________________________________________________________________________________
# RUTA DE LA PAGINA LUEGO DEL INICIO DE SESIÓN EXITOSO

@app.route('/index')
def index():
    if 'user_id' in session:
        username = session['user_id']
        imagen_base64 = obtener_imagen_perfil_blob(username)
        return render_template('index.html', username=username, imagen_base64=imagen_base64)
    else:
        return redirect(url_for('login'))


def obtener_id_de_usuario_actual():
    return session.get('user_id')


# _____________________________________________________________________________________________________________________
@app.route('/perfil_de_usuario', methods=['GET', 'POST'])
@with_username
def mostrar_perfil(username):
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('login'))

    imagen_base64 = obtener_imagen_perfil_blob(username)
    datos_usuario = obtener_datos_usuario(username)  # Obtener los datos del usuario

    return render_template('perfil_usuario.html', username=username, imagen_base64=imagen_base64,
                           datos_usuario=datos_usuario)


@app.route('/actualizar_imagen', methods=['POST'])
@with_username
def actualizar_imagen(username):
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        if imagen:
            imagen_actualizada = imagen.read()
            exito_imagen = actualizar_imagen_perfil_blob(username, imagen_actualizada)
            if exito_imagen:
                return jsonify({'success': True, 'message': 'Imagen actualizada correctamente'})

    return jsonify({'success': False, 'message': 'Error al actualizar la imagen'})


@app.route('/eliminar_imagen_perfil', methods=['POST'])
def eliminar_imagen():
    try:
        data = request.get_json()  # Obtener los datos JSON del cuerpo de la solicitud
        if data and 'username' in data:
            username = data['username']
            eliminar_imagen_perfil(username)  # Llama a la función para eliminar la imagen de perfil
            return jsonify({'success': True, 'message': 'Imagen eliminada correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Datos incorrectos para eliminar la imagen'})
    except Exception as e:
        print("Error al eliminar la imagen de perfil:")
        traceback.print_exc()  # Imprimir la traza completa de la excepción
        return jsonify({'success': False, 'message': 'Error al eliminar la imagen de perfil'})


@app.route('/actualizar_datos_usuario', methods=['POST'])
@with_username
def actualizar_datos_usuario(username):
    nuevo_nombre_completo = request.form.get('nuevo_nombre_completo')
    nueva_cedula = request.form.get('nueva_cedula')
    nuevo_correo = request.form.get('nuevo_correo')
    nuevo_celular = request.form.get('nuevo_celular')

    exito_nombre_completo = actualizar_nombre_completo(username, nuevo_nombre_completo)
    exito_cedula = actualizar_cedula(username, nueva_cedula)
    exito_correo = actualizar_correo(username, nuevo_correo)
    exito_celular = actualizar_celular(username, nuevo_celular)

    if exito_nombre_completo and exito_cedula and exito_correo and exito_celular:
        return jsonify({'success': True, 'message': 'Datos actualizados correctamente'})
    else:
        return jsonify({'success': False, 'message': 'Error al actualizar los datos del usuario'})


# _____________________________________________________________________________________________________________________
# RUTA PARA EL FORMULARIO DE REGISTRO DE PRODUCTO

@app.route('/registrar_producto', methods=['POST'])
def registrar_producto():
    try:
        action = request.form['action']
        print("Datos del formulario:", request.form)
        print("Imagen del formulario:", request.files['imagen'].filename if 'imagen' in request.files else '')

        if action == 'registrar':
            # Obtener los datos del formulario
            nombre = request.form['nombre']
            categoria = request.form['categoria']
            imagen = request.files['imagen'].read() if 'imagen' in request.files else b''  # Lee la imagen como bytes
            precio = float(request.form['precio'])
            cantidad = int(request.form['cantidad'])

            # Llamamos a la función para insertar el producto en la base de datos
            insertar_producto(nombre, categoria, imagen, precio, cantidad)

        # Redirigir al formulario después de registrar el producto o a la página de inicio
        return redirect(url_for('registro_producto'))

    except Exception as e:
        print("Error al registrar producto:", e)
        return "Internal Server Error"


# _____________________________________________________________________________________________________________________
# DIRECCION A CARRITO DE COMPRAS Y CALCULAR LA SUMATORIA DE PRECIOS

@app.route('/carrito_compras')
@with_username
def mostrar_carrito(username):
    try:
        idUsuario = session.get('user_id')

        if idUsuario is None:
            return "Usuario no autenticado"

        productos_carrito = obtener_productos_del_carrito(idUsuario)
        imagen_base64 = obtener_imagen_perfil_blob(username)
        productos_carrito = [
            {
                **producto,
                'precio': Decimal(str(producto['precio'])),
                'precio_total': Decimal(str(producto['precio_total']))
            }
            for producto in productos_carrito
        ]

        # Calcular el precio total del carrito
        sum_precios_totales = sum(producto['precio_total'] for producto in productos_carrito)

        suma_total_precios = sum_precios_totales

        return render_template('carrito_compras.html', productos=productos_carrito, total=sum_precios_totales,
                               suma_total=suma_total_precios, username=username, imagen_base64=imagen_base64)
    except Exception as e:
        print("Error al mostrar el carrito:", e)


# _____________________________________________________________________________________________________________________
# RUTA PARA AGREGAR PRODUCTOS AL CARRITO

@app.route('/agregar_al_carrito/<int:idProducto>', methods=['POST'])
def agregar_al_carrito(idProducto):
    try:
        idUsuario = session.get('user_id')  # Obtener el idUsuario de la sesión

        # Lógica para obtener los datos del producto, por ejemplo, la cantidad
        cantidad = request.json.get('cantidad')  # Ejemplo de cómo obtener la cantidad desde la solicitud

        # Llamar a la función de la base de datos para agregar el producto al carrito
        agregado_exitosamente, mensaje = agregar_al_carrito_db(idUsuario, idProducto, cantidad)

        if agregado_exitosamente:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Mensaje de error específico'})
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500


# _____________________________________________________________________________________________________________________
# PARA AJUSTAR LA CANTIDAD DE PRODUCTOS EN EL CARRITO ANTES DE REALIZAR LA COMPRA

@app.route('/ajustar_cantidad/<int:idProducto>', methods=['POST'])
def ajustar_cantidad(idProducto):
    try:
        data = request.json
        nueva_cantidad = int(data.get('cantidad'))
        idUsuario = session.get('user_id')  # Obtener el idUsuario de la sesión

        if idUsuario is None:
            return jsonify({'error': 'Usuario no autenticado'}), 401  # 401 para indicar falta de autenticación

        exito, mensaje = ajustar_cantidad_en_carrito(idUsuario, idProducto, nueva_cantidad)

        if exito:
            return jsonify({'message': mensaje}), 200
        else:
            return jsonify({'error': mensaje}), 400

    except Exception as e:
        print("Error al ajustar la cantidad:", e)
        return jsonify({'error': 'Error interno del servidor'}), 500


# _____________________________________________________________________________________________________________________
# PARA ELIMINAR PRODUCTOS DEL CARRITO

@app.route('/eliminar_del_carrito/<int:idProducto>', methods=['DELETE'])
def eliminar_del_carrito(idProducto):
    try:
        idUsuario = session.get('user_id')  # Obtener el idUsuario de la sesión

        if idUsuario is None:
            return jsonify({'error': 'Usuario no autenticado'}), 401  # 401 para indicar falta de autenticación

        exito_eliminacion = eliminar_producto_del_carrito(idUsuario, idProducto)

        if exito_eliminacion:
            return jsonify({'message': f'Producto {idProducto} eliminado del carrito'}), 200
        else:
            return jsonify({'error': 'Error al eliminar el producto del carrito'}), 500

    except Exception as e:
        print("Error en la ruta de eliminación del carrito:", e)
        return jsonify({'error': 'Error interno del servidor'}), 500


# _____________________________________________________________________________________________________________________
# PARA ACTUALIZAR INVENTARIO

@app.route('/gestion_inventario')
@with_username
def gestion_inventario(username):
    try:
        # Obtener productos desde la base de datos
        productos, categorias = obtener_productos()

        busqueda = request.args.get('busqueda')
        categoria = request.args.get('categoria')

        productos, categorias = obtener_productos(busqueda=busqueda, categoria=categoria)
        imagen_base64 = obtener_imagen_perfil_blob(username)

        # Renderizar la plantilla con la lista de productos
        return render_template('gestion_inventario.html', inventario=productos, productos=productos,
                               categorias=categorias, username=username, imagen_base64=imagen_base64)

    except Exception as e:
        print(f"Error en la ruta /gestion_inventario:")
        traceback.print_exc()  # Imprimir la traza completa de la excepción
        raise


@app.route('/exportar_excel', methods=['GET'])
def descargar_excel():
    excel_file = exportar_datos_excel()
    if excel_file:
        return send_file(excel_file, as_attachment=True)
    else:
        return "Error al exportar datos."


@app.route('/importar_excel', methods=['POST'])
def importar_excel():
    archivo_excel = request.files['archivo_excel']
    success = importar_datos_excel(archivo_excel)
    return jsonify(success=success)


@app.route('/actualizar_cantidades', methods=['POST'])
def actualizar_cantidades():
    data = request.get_json()
    resultado = actualizar_cantidades_bd(data)  # Llama a tu función para actualizar las cantidades
    print(resultado)
    print(data)

    # Llama a la función para actualizar el carrito después de la actualización del inventario
    resultado_carrito = actualizar_carrito_despues_de_actualizar_inventario(data)
    print(resultado_carrito)

    return jsonify(resultado)


@app.route('/actualizar_precios', methods=['POST'])
def actualizar_precios():
    try:
        data = request.get_json()
        resultado = actualizar_precios_bd(data)
        print(resultado)

        if resultado.get('message') == 'Precios actualizados exitosamente':
            precios_actualizados = data.get('precios', [])

            for producto in precios_actualizados:
                product_id = producto.get('id')
                nuevo_precio = producto.get('precio')

                resultado_carrito = actualizar_carrito_despues_de_actualizar_precio(product_id, nuevo_precio)
                print(resultado_carrito)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/actualizar_categorias', methods=['POST'])
def actualizar_categorias():
    try:
        data = request.get_json()

        productId = data['productId']
        nuevaCategoria = data['nuevaCategoria']

        resultado_actualizacion = actualizar_categorias_bd(productId, nuevaCategoria)

        # Llamar a la función para actualizar la categoría en el carrito después de actualizar en productos
        resultado_carrito = actualizar_carrito_despues_de_actualizar_categoria(productId, nuevaCategoria)

        print(resultado_actualizacion)
        print(resultado_carrito)

        return jsonify({'message': 'Categoría actualizada exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/actualizar_imagen_productos', methods=['POST'])
def actualizar_producto():
    id_producto = request.form['id_producto']
    nuevas_imagenes = request.files.getlist('nuevas_imagenes')

    for imagen in nuevas_imagenes:
        nueva_imagen = imagen.read()
        actualizar_imagen_producto(id_producto, nueva_imagen)

    return render_template('gestion_inventario.html')


@app.route('/obtener_categorias', methods=['GET'])
def obtener_categorias():
    try:
        productos, categorias = obtener_productos()
        print("Categorías obtenidas:", categorias)  # Mensaje de depuración
        return jsonify({'categorias': categorias})
    except Exception as e:
        print('Error en el servidor al obtener categorías:', str(e))
        return jsonify({'error': str(e)})


@app.route('/eliminar_producto', methods=['POST'])
def eliminar_producto():
    data = request.get_json()
    producto_id = data.get('productoId')
    resultado = eliminar_producto_db(producto_id)
    return jsonify(resultado)


@app.route('/actualizar_nombres', methods=['POST'])
def actualizar_nombres():
    try:
        data = request.get_json()
        resultado = actualizar_nombre_bd(data)  # Llamada a la función con los datos JSON
        print(resultado)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)})


# _____________________________________________________________________________________________________________________
# PARA BUSQUEDA DE PRODUCTOS

@app.route('/productos')
@with_username
def mostrar_productos(username):
    try:
        busqueda = request.args.get('busqueda')
        categoria = request.args.get('categoria')
        imagen_base64 = obtener_imagen_perfil_blob(username)

        productos, categorias = obtener_productos(busqueda=busqueda, categoria=categoria)
        return render_template('productos.html', productos=productos, categorias=categorias, username=username,
                               imagen_base64=imagen_base64)
    except Exception as e:
        return f"Error: {str(e)}"


# _____________________________________________________________________________________________________________________
# PRODUCTOS VENDIDOS

@app.route('/productos_vendidos.html')
@with_username
def productos_vendidos_y_graficos(username):
    try:
        # Obtener datos de productos vendidos
        productos_vendidos = obtener_productos_vendidos()

        # Obtener datos de gráficos
        usuarios_gastos, total_gastos = obtener_datos_graficos_productos_vendidos()

        imagen_base64 = obtener_imagen_perfil_blob(username)

        if productos_vendidos and usuarios_gastos and total_gastos:
            # Puedes pasar ambos conjuntos de datos a la plantilla y decidir qué mostrar dentro de la plantilla
            return render_template('productos_vendidos.html',
                                   productos_comprados=productos_vendidos,
                                   usuarios_gastos=usuarios_gastos, total_gastos=total_gastos,
                                   username=username, imagen_base64=imagen_base64)
        else:
            return "No existen productos vendidos...", 500

    except Exception as e:
        return f"Error: {str(e)}", 500


# _____________________________________________________________________________________________________________________
# REALIZAR COMPRA

@app.route('/realizar_compra', methods=['POST'])
def realizar_compra():
    try:
        # Suponiendo que tienes el ID de usuario disponible en la variable id_usuario
        idUsuario = session.get('user_id')  # Obtener el ID de usuario actual (cámbialo según tu lógica)

        # Llama a la función almacenada en la base de datos para realizar la compra para un usuario específico
        exito_compra = realizar_compra_en_bd(idUsuario)

        if exito_compra:
            # Si la compra fue exitosa, actualiza los datos para mostrar en el carrito
            productos_carrito = obtener_productos_del_carrito(idUsuario)

            # Calcula el precio total de la compra
            total_precio_compra = sum(producto['precio_total'] for producto in productos_carrito)

            # Limpia el carrito después de una compra exitosa para el usuario específico
            limpiar_carrito(idUsuario)

            # Renderiza el HTML con los datos actualizados
            return render_template('carrito_compras.html', productos=productos_carrito, total=total_precio_compra)

        else:
            return "Error en la compra"

    except Exception as e:
        print("Error al realizar la compra:", e)
        return "Error en la compra"


# _____________________________________________________________________________________________________________________
# GRAFIAS

@app.route('/grafico_pastel')
@with_username
def graficos(username):
    labels_pastel, data_pastel, fechas_barras, precios_totales_barras, nombres_barras, cantidades_barras = obtener_datos_graficos()
    imagen_base64 = obtener_imagen_perfil_blob(username)

    if labels_pastel and data_pastel and fechas_barras and precios_totales_barras and nombres_barras and cantidades_barras:
        return render_template('graficos.html',
                               nombres_barras=nombres_barras, cantidades_barras=cantidades_barras,
                               labels_pastel=labels_pastel, data_pastel=data_pastel,
                               fechas_barras=fechas_barras, precios_totales_barras=precios_totales_barras,
                               username=username, imagen_base64=imagen_base64)
    else:
        return "Error interno en el servidor", 500


# _____________________________________________________________________________________________________________________
# VISUALIZAR PRODUCTOS COMPRADOS

@app.route('/productos_comprados')
@with_username
def mostrar_productos_comprados(username):
    try:
        id_usuario = obtener_id_de_usuario_actual()
        productos_comprados = obtener_productos_comprados_por_usuario(id_usuario)
        imagen_base64 = obtener_imagen_perfil_blob(username)

        if productos_comprados is not None:
            return render_template('productos_comprados.html', productos_comprados=productos_comprados,
                                   username=username, imagen_base64=imagen_base64)
        else:
            return "No se pudieron obtener los productos comprados", 500

    except Exception as e:
        print(f"Error al mostrar productos comprados: {e}")
        return "Error al mostrar productos comprados", 500


# _____________________________________________________________________________________________________________________
# VISUALIZAR DATOS DE CLIENTES CON COMPRAS

@app.route('/usuarios_registrados')
@with_username
def usuarios_registrados(username):
    try:
        imagen_base64 = obtener_imagen_perfil_blob(username)
        usuarios = obtener_usuarios_registrados()
        return render_template('usuarios_registrados.html', usuarios=usuarios, username=username,
                               imagen_base64=imagen_base64)
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/buscar_usuarios_en_tiempo_real', methods=['GET'])
def buscar_usuarios_en_tiempo_real():
    try:
        busqueda = request.args.get('busqueda')

        # Llamar a la función de la base de datos para obtener usuarios filtrados por la búsqueda
        usuarios = buscar_usuarios(busqueda=busqueda)

        # Convertir la lista de usuarios a un formato JSON y enviarla al cliente
        return jsonify(usuarios=usuarios)

    except Exception as e:
        print(f"Error al buscar usuarios en tiempo real: {str(e)}")
        return jsonify(error="Error al buscar usuarios en tiempo real")


# _____________________________________________________________________________________________________________________
# RUTAS DE LAS PAGINAS

@app.route('/pagina_inicio')
def pagina_inicio():
    return render_template('login.html')


@app.route('/registro_producto')
@with_username
def registro_producto(username):
    imagen_base64 = obtener_imagen_perfil_blob(username)
    return render_template('registro_producto.html', username=username, imagen_base64=imagen_base64)


@app.route('/login_pagina')
def login_pagina():
    return render_template('login.html')


@app.route('/registro_usuarios', methods=['POST'])
def registro_usuarios():
    return render_template('registro_usuarios.html', methods=['GET'])


@app.route('/registro_usuarios')
def registros_usuarios():
    return (render_template('registro_usuarios.html', methods=['GET']))


# _____________________________________________________________________________________________________________________
# DESCARGAR PLANTILLA PARA IMPORTAR DATOS :)

@app.route('/descargar_plantilla_excel', methods=['GET'])
def descargar_plantilla_excel():
    enlace_excel = "https://docs.google.com/spreadsheets/d/1YrjpJ6ts2xRJGVCo2QV9VubBvLIae_0B/edit?usp=drive_link&ouid=114657658400728418247&rtpof=true&sd=true"

    return f"""
        <a class="btn boton-btn" href="{enlace_excel}" download>
            Plantilla para Importar Datos <i class="fas fa-upload ml-2"></i>
        </a>
        """


# _____________________________________________________________________________________________________________________

# EJECUCIÓN DE LA APLICACIÓN
if __name__ == '__main__':
    app.run(debug=True)
