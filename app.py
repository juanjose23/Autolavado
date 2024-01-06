import os
from decimal import *
from datetime import *
from flask import *
from flask_mail import *
from flask_cors import *
from werkzeug.security import *
from flask_session import Session
from sqlalchemy import *
from sqlalchemy.orm import *
from utils import *
import requests
import json
import pdfkit
import random
import string

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SESSION_PERMANENT"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER'] = os.getenv("SERVER_EMAIL")
app.config['MAIL_PORT'] = os.getenv("port")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("correo")
app.config['MAIL_PASSWORD'] = os.getenv("clave")
app.secret_key = '123'
mail = Mail(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db_session = scoped_session(sessionmaker(bind=engine))

def insertar_persona(db_session: Session, nombre, correo, celular):
    query = text("INSERT INTO persona (nombre, correo, direccion, celular) VALUES (:nombre, :correo, :direccion, :celular) RETURNING id")
    id_persona = db_session.execute(query, {"nombre": nombre, "correo": correo, "direccion": 'No hay', "celular": celular}).fetchone()
    return id_persona[0]

def insertar_persona_natural(db_session: Session, id_persona, apellidos, tipo):
    query = text("INSERT INTO persona_natural (id_persona, apellido, tipo_persona) VALUES (:id_persona, :apellido, :tipo_persona)")
    db_session.execute(query, {"id_persona": id_persona, "apellido": apellidos, "tipo_persona": tipo})

def insertar_cliente(db_session: Session, id_persona, tipo):
    codigo_cliente = generar_codigo_cliente(id_persona, tipo)
    query = text("INSERT INTO clientes (id_persona, codigo, tipo_cliente, foto, estado) VALUES (:id_persona, :codigo, :tipo_cliente, :foto, :estado)")
    db_session.execute(query, {"id_persona": id_persona, "codigo": codigo_cliente, "tipo_cliente": tipo, "foto": 'No hay', "estado": '1'})
    return codigo_cliente

def update_persona(db_session: Session, id_persona, nombre, correo, celular, direccion):
    query = text("UPDATE persona SET nombre = :nombre, correo = :correo, direccion = :direccion, celular = :celular WHERE id = :id_persona")
    db_session.execute(query, {"id_persona": id_persona, "nombre": nombre, "correo": correo, "direccion": direccion, "celular": celular})
    db_session.commit()

def update_persona_natural(db_session: Session, id_persona, apellidos, tipo):
    query = text("UPDATE persona_natural SET apellido = :apellidos, tipo_persona = :tipo WHERE id_persona = :id_persona")
    db_session.execute(query, {"id_persona": id_persona, "apellidos": apellidos, "tipo": tipo})
    db_session.commit()

def update_cliente(db_session: Session, id_persona, tipo, foto, estado):
    query = text("UPDATE clientes SET tipo_cliente = :tipo, foto = :foto, estado = :estado WHERE id_persona = :id_persona")
    db_session.execute(query, {"id_persona": id_persona, "tipo": tipo, "foto": foto, "estado": estado})
    db_session.commit()

def cambiar_estado_cliente(db_session: Session, id_persona, nuevo_estado):
    query = text("UPDATE clientes SET estado = :nuevo_estado WHERE id_persona = :id_persona")
    db_session.execute(query, {"id_persona": id_persona, "nuevo_estado": nuevo_estado})
    db_session.commit()

def generar_codigo_reservacion(db_session):
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Verificar que el código no exista ya en la base de datos
    query = text("SELECT COUNT(*) FROM reservacion WHERE codigo = :codigo")
    count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]

    while count > 0:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]

    return codigo

def generar_codigo_trabajador(db_session: Session):
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Verificar que el código no exista ya en la base de datos
    query = text("SELECT COUNT(*) FROM trabajador WHERE codigo = :codigo")
    count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]

    while count > 0:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]

    return codigo

def insertar_trabajador(db_session, id_persona, codigo, foto, estado):
    query = text("""
        INSERT INTO trabajador (id_persona, codigo, foto, estado)
        VALUES (:id_persona, :codigo, :foto, :estado)
    """)

    db_session.execute(query, {"id_persona": id_persona, "codigo": codigo, "foto": foto, "estado": estado})
    db_session.commit()

def actualizar_trabajador(db_session, id_trabajador, id_persona, codigo, foto, estado):
    query = text("""
        UPDATE trabajador
        SET id_persona = :id_persona, codigo = :codigo, foto = :foto, estado = :estado
        WHERE id = :id_trabajador
    """)

    db_session.execute(query, {"id_trabajador": id_trabajador, "id_persona": id_persona, "codigo": codigo, "foto": foto, "estado": estado})
    db_session.commit()

def cambiar_estado_trabajador(db_session, id_trabajador, nuevo_estado):
    query = text("""
        UPDATE trabajador
        SET estado = :nuevo_estado
        WHERE id = :id_trabajador
    """)

    db_session.execute(query, {"id_trabajador": id_trabajador, "nuevo_estado": nuevo_estado})
    db_session.commit()

def insertar_salario(db_session, id_trabajador, salario, estado):
    query = text("""
        INSERT INTO salario (id_trabajador, salario, estado)
        VALUES (:id_trabajador, :salario, :estado)
    """)

    db_session.execute(query, {"id_trabajador": id_trabajador, "salario": salario, "estado": estado})
    db_session.commit()


def cambiar_estado_salario(db_session, id_salario, nuevo_estado):
    query = text("""
        UPDATE salario
        SET estado = :nuevo_estado
        WHERE id = :id_salario
    """)

    db_session.execute(query, {"id_salario": id_salario, "nuevo_estado": nuevo_estado})
    db_session.commit()




def guardar_reservacion(db_session: Session, id_cliente, id_horario, id_servicio,  tipo_pago, fecha, hora, subtotal, observacion, estado):
    codigo=generar_codigo_reservacion()
    query = text("""
        INSERT INTO reservacion (idcliente, idhorario, idservicio, codigo, tipopago, fecha, hora, subtotal, observacion, estado)
        VALUES (:id_cliente, :id_horario, :id_servicio, :codigo, :tipo_pago, :fecha, :hora, :subtotal, :observacion, :estado)
        RETURNING id
    """)
    result = db_session.execute(query, {"id_cliente": id_cliente,"id_horario": id_horario,"id_servicio": id_servicio,"codigo": codigo,"tipo_pago": tipo_pago,"fecha": fecha,"hora": hora,"subtotal": subtotal,"observacion": observacion,"estado": estado})
    id_reservacion = result.fetchone()[0]

    # Devolver el ID de la reservación
    return codigo
def insertar_producto(db_session: Session, nombre, descripcion, logo, estado):
    query = text("""
        INSERT INTO producto (nombre, descripcion, logo, estado)
        VALUES (:nombre, :descripcion, :logo, :estado)
    """)

    db_session.execute(query, {"nombre": nombre, "descripcion": descripcion, "logo": logo, "estado": estado})
    db_session.commit()

# Actualizar producto
def actualizar_producto(db_session: Session, id_producto, nombre, descripcion, logo, estado):
    query = text("""
        UPDATE producto
        SET nombre = :nombre, descripcion = :descripcion, logo = :logo, estado = :estado
        WHERE id = :id_producto
    """)

    db_session.execute(query, {"id_producto": id_producto, "nombre": nombre, "descripcion": descripcion, "logo": logo, "estado": estado})
    db_session.commit()

# Cambiar estado del producto
def cambiar_estado_productos(db_session, id_producto, nuevo_estado):
    # Tu lógica para cambiar el estado del producto aquí
    query = text("UPDATE producto SET estado = :nuevo_estado WHERE id = :id_producto")
    db_session.execute(query, {"id_producto": id_producto, "nuevo_estado": nuevo_estado})
    db_session.commit()
    # Puedes retornar algo si es necesario
    return "Estado del producto cambiado exitosamente"

def insertar_precio(db_session: Session, id_producto, precio, estado):
    query = text("""
        INSERT INTO precio (id_producto, precio, estado)
        VALUES (:id_producto, :precio, :estado)
    """)

    db_session.execute(query, {"id_producto": id_producto, "precio": precio, "estado": estado})
    db_session.commit()


def cambiar_estado_precio(db_session: Session, id_precio, nuevo_estado):
    query = text("""
        UPDATE precio
        SET estado = :nuevo_estado
        WHERE id = :id_precio
    """)

    db_session.execute(query, {"id_precio": id_precio, "nuevo_estado": nuevo_estado})
    db_session.commit()

def insertar_horario(db_session: Session, dia, hora_apertura, hora_cierre, estado):
    query = text("""
        INSERT INTO horarios (dia, hora_apertura, hora_cierre, estado)
        VALUES (:dia, :hora_apertura, :hora_cierre, :estado)
    """)

    db_session.execute(query, {"dia": dia, "hora_apertura": hora_apertura, "hora_cierre": hora_cierre, "estado": estado})
    db_session.commit()

def update_horario(db_session: Session, id_horario, dia, hora_apertura, hora_cierre, estado):
    query = text("""
        UPDATE horarios
        SET dia = :dia, hora_apertura = :hora_apertura, hora_cierre = :hora_cierre, estado = :estado
        WHERE id = :id_horario
    """)

    db_session.execute(query, {"id_horario": id_horario, "dia": dia, "hora_apertura": hora_apertura, "hora_cierre": hora_cierre, "estado": estado})
    db_session.commit()

def cambiar_estado_horario(db_session: Session, id_horario, nuevo_estado):
    query = text("""
        UPDATE horarios
        SET estado = :nuevo_estado
        WHERE id = :id_horario
    """)

    db_session.execute(query, {"id_horario": id_horario, "nuevo_estado": nuevo_estado})
    db_session.commit()

def insertar_servicio(db_session: Session, nombre, descripcion, foto, estado):
    query = text("""
        INSERT INTO servicios (nombre, descripcion, foto, estado)
        VALUES (:nombre, :descripcion, :foto, :estado)
    """)

    db_session.execute(query, {"nombre": nombre, "descripcion": descripcion, "foto": foto, "estado": estado})
    db_session.commit()

def update_servicio(db_session: Session, id_servicio, nombre, descripcion, foto, estado):
    query = text("""
        UPDATE servicios
        SET nombre = :nombre, descripcion = :descripcion, foto = :foto, estado = :estado
        WHERE id = :id_servicio
    """)

    db_session.execute(query, {"id_servicio": id_servicio, "nombre": nombre, "descripcion": descripcion, "foto": foto, "estado": estado})
    db_session.commit()

def cambiar_estado_servicio(db_session: Session, id_servicio, nuevo_estado):
    query = text("""
        UPDATE servicios
        SET estado = :nuevo_estado
        WHERE id = :id_servicio
    """)

    db_session.execute(query, {"id_servicio": id_servicio, "nuevo_estado": nuevo_estado})
    db_session.commit()

def insertar_precio_servicio(db_session: Session, id_servicio, precio, estado):
    query = text("""
        INSERT INTO precio_servicios (id_servicios, precio, estado)
        VALUES (:id_servicio, :precio, :estado)
    """)

    db_session.execute(query, {"id_servicio": id_servicio, "precio": precio, "estado": estado})
    db_session.commit()

def update_precio_servicio(db_session: Session, id_precio_servicio, id_servicio, precio, estado):
    query = text("""
        UPDATE precio_servicios
        SET id_servicios = :id_servicio, precio = :precio, estado = :estado
        WHERE id = :id_precio_servicio
    """)

    db_session.execute(query, {"id_precio_servicio": id_precio_servicio, "id_servicio": id_servicio, "precio": precio, "estado": estado})
    db_session.commit()

def cambiar_estado_precio_servicio(db_session: Session, id_precio_servicio, nuevo_estado):
    query = text("""
        UPDATE precio_servicios
        SET estado = :nuevo_estado
        WHERE id = :id_precio_servicio
    """)

    db_session.execute(query, {"id_precio_servicio": id_precio_servicio, "nuevo_estado": nuevo_estado})
    db_session.commit()

def insertar_tipo_venta(db_session: Session, nombre, descripcion, estado):
    query = text("""
        INSERT INTO tipo_venta (nombre, descripcion, estado)
        VALUES (:nombre, :descripcion, :estado)
    """)

    db_session.execute(query, {"nombre": nombre, "descripcion": descripcion, "estado": estado})
    db_session.commit()

def update_tipo_venta(db_session: Session, id_tipo_venta, nombre, descripcion, estado):
    query = text("""
        UPDATE tipo_venta
        SET nombre = :nombre, descripcion = :descripcion, estado = :estado
        WHERE id = :id_tipo_venta
    """)

    db_session.execute(query, {"id_tipo_venta": id_tipo_venta, "nombre": nombre, "descripcion": descripcion, "estado": estado})
    db_session.commit()

def cambiar_estado_tipo_venta(db_session: Session, id_tipo_venta, nuevo_estado):
    query = text("""
        UPDATE tipo_venta
        SET estado = :nuevo_estado
        WHERE id = :id_tipo_venta
    """)

    db_session.execute(query, {"id_tipo_venta": id_tipo_venta, "nuevo_estado": nuevo_estado})
    db_session.commit()

def insertar_venta(db_session: Session, id_tipo, id_cliente, codigo, tipo_pago, fecha, descuento, total, estado):
    query = text("""
        INSERT INTO venta (id_tipo, id_cliente, codigo, tipo_pago, fecha, descuento, total, estado)
        VALUES (:id_tipo, :id_cliente, :codigo, :tipo_pago, :fecha, :descuento, :total, :estado)
    """)

    db_session.execute(query, {"id_tipo": id_tipo, "id_cliente": id_cliente, "codigo": codigo, "tipo_pago": tipo_pago,
                               "fecha": fecha, "descuento": descuento, "total": total, "estado": estado})
    db_session.commit()


def cambiar_estado_venta(db_session: Session, id_venta, nuevo_estado):
    query = text("""
        UPDATE venta
        SET estado = :nuevo_estado
        WHERE id = :id_venta
    """)

    db_session.execute(query, {"id_venta": id_venta, "nuevo_estado": nuevo_estado})
    db_session.commit()


def insertar_detalle_venta(db_session: Session, id_venta, id_servicio, precio_unitario, cantidad, subtotal):
    query = text("""
        INSERT INTO detalle_venta (id_venta, id_servicio, precio_unitario, cantidad, subtotal)
        VALUES (:id_venta, :id_servicio, :precio_unitario, :cantidad, :subtotal)
    """)

    db_session.execute(query, {"id_venta": id_venta, "id_servicio": id_servicio, "precio_unitario": precio_unitario, "cantidad": cantidad, "subtotal": subtotal})
    db_session.commit()

def update_detalle_venta(db_session: Session, id_detalle_venta, id_venta, id_servicio, precio_unitario, cantidad, subtotal):
    query = text("""
        UPDATE detalle_venta
        SET id_venta = :id_venta, id_servicio = :id_servicio, precio_unitario = :precio_unitario,
        cantidad = :cantidad, subtotal = :subtotal
        WHERE id = :id_detalle_venta
    """)

    db_session.execute(query, {"id_detalle_venta": id_detalle_venta, "id_venta": id_venta, "id_servicio": id_servicio,
                               "precio_unitario": precio_unitario, "cantidad": cantidad, "subtotal": subtotal})
    db_session.commit()


def insertar_venta_servicios(db_session: Session, id_venta, id_reservacion, subtotal):
    query = text("""
        INSERT INTO venta_servicios (id_venta, id_reservacion, subtotal)
        VALUES (:id_venta, :id_reservacion, :subtotal)
    """)

    db_session.execute(query, {"id_venta": id_venta, "id_reservacion": id_reservacion, "subtotal": subtotal})
    db_session.commit()

def update_venta_servicios(db_session: Session, id_venta_servicios, id_venta, id_reservacion, subtotal):
    query = text("""
        UPDATE venta_servicios
        SET id_venta = :id_venta, id_reservacion = :id_reservacion, subtotal = :subtotal
        WHERE id = :id_venta_servicios
    """)

    db_session.execute(query, {"id_venta_servicios": id_venta_servicios, "id_venta": id_venta,
                               "id_reservacion": id_reservacion, "subtotal": subtotal})
    db_session.commit()

def insertar_grupo_usuarios(db_session: Session, nombre, descripcion, estado):
    query = text("""
        INSERT INTO grupo_usuarios (nombre, descripcion, estado)
        VALUES (:nombre, :descripcion, :estado)
    """)

    db_session.execute(query, {"nombre": nombre, "descripcion": descripcion, "estado": estado})
    db_session.commit()

def update_grupo_usuarios(db_session: Session, id_grupo_usuarios, nombre, descripcion, estado):
    query = text("""
        UPDATE grupo_usuarios
        SET nombre = :nombre, descripcion = :descripcion, estado = :estado
        WHERE id = :id_grupo_usuarios
    """)

    db_session.execute(query, {"id_grupo_usuarios": id_grupo_usuarios, "nombre": nombre, "descripcion": descripcion, "estado": estado})
    db_session.commit()

def cambiar_estado_grupo_usuarios(db_session: Session, id_grupo_usuarios, nuevo_estado):
    query = text("""
        UPDATE grupo_usuarios
        SET estado = :nuevo_estado
        WHERE id = :id_grupo_usuarios
    """)

    db_session.execute(query, {"id_grupo_usuarios": id_grupo_usuarios, "nuevo_estado": nuevo_estado})
    db_session.commit()

def insertar_usuario(db_session: Session, id_grupo, id_persona, usuario, contraseña, estado):
    query = text("""
        INSERT INTO usuario (id_grupo, id_persona, usuario, contraseña, estado)
        VALUES (:id_grupo, :id_persona, :usuario, :contraseña, :estado)
    """)

    db_session.execute(query, {"id_grupo": id_grupo, "id_persona": id_persona, "usuario": usuario, "contraseña": contraseña, "estado": estado})
    db_session.commit()

def update_usuario(db_session: Session, id_usuario, id_grupo, id_persona, usuario, contraseña, estado):
    query = text("""
        UPDATE usuario
        SET id_grupo = :id_grupo, id_persona = :id_persona, usuario = :usuario, contraseña = :contraseña, estado = :estado
        WHERE id = :id_usuario
    """)

    db_session.execute(query, {"id_usuario": id_usuario, "id_grupo": id_grupo, "id_persona": id_persona,
                               "usuario": usuario, "contraseña": contraseña, "estado": estado})
    db_session.commit()

def cambiar_estado_usuario(db_session: Session, id_usuario, nuevo_estado):
    query = text("""
        UPDATE usuario
        SET estado = :nuevo_estado
        WHERE id = :id_usuario
    """)

    db_session.execute(query, {"id_usuario": id_usuario, "nuevo_estado": nuevo_estado})
    db_session.commit()


def cambiar_estado_reservacion(db_session: Session, id_reservacion, nuevo_estado):
    query = text("""
        UPDATE reservacion
        SET estado = :nuevo_estado
        WHERE id = :id_reservacion
    """)

    db_session.execute(query, {"id_reservacion": id_reservacion, "nuevo_estado": nuevo_estado})
    db_session.commit()

def obtener_servicios_activos(db_session: Session):
    query = text('SELECT s.id, s.descripcion, s.nombre, ps.precio FROM servicios s LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios WHERE s.estado = 1 and ps.estado = 1')
    result = db_session.execute(query).fetchall()
    return result


def consultar_servicios(db_session: Session, filtro_id=None):
    query = text("""
        SELECT s.nombre, s.descripcion, ps.precio
        FROM servicios s
        LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios
        WHERE s.estado = 1 AND ps.estado = 1
        AND (s.id = :filtro_id OR :filtro_id IS NULL)
    """)
    
    result = db_session.execute(query, {"filtro_id": filtro_id}).fetchall()
    return result

def obtener_productos(db_session):
    query = text("SELECT * FROM producto")
    productos = db_session.execute(query).fetchall()
    return productos


@cross_origin()
@app.route('/api/InsertarCliente', methods=['POST'])
def api_InsertarCliente():
    if request.method == 'POST':
        try:
            data = request.get_json()
            nombre = data['nombre']
            correo = data['correo']
            celular = data['celular']
            apellidos = data['apellidos']
            tipo = data['tipo']

            id_persona = insertar_persona(db_session, nombre, correo, celular)
            insertar_persona_natural(db_session, id_persona, apellidos, tipo)
            codigo_cliente=insertar_cliente(db_session, id_persona, tipo)

            db_session.commit()
            return jsonify({"codigo_cliente": codigo_cliente}), 200

        except Exception as e:
            print(f"Error: {str(e)}")
            db_session.rollback()
            return 'null', 400

        finally:
            db_session.close()

    return 'null', 400


@cross_origin()
@app.route('/api/InsertarClienteObligatorio', methods=['GET', 'POST'])
def insertar_usuarios():
    request_data = request.get_json()

    if request.method == 'POST':

        request_data = request.get_json()
        nombre = request_data['nombre']
        celular = request_data['celular']
        id_persona = insertar_persona(db_session, nombre,"No hay", celular)
        codigo_cliente=insertar_cliente(db_session, id_persona,"Cliente no registrado")

        db_session.commit()

        return jsonify({"codigo_cliente": codigo_cliente}), 200
        
    return 'null', 400

def ValidarNumeroCelularExistente(numero):
    query = text("SELECT id FROM persona WHERE celular = :numero")
    exists = db_session.execute(query, {"numero": numero}).scalar()
    return exists

@app.route('/')
def index():
    return render_template('index.html')


    
@cross_origin()
@app.route('/api/gethorarios', methods=['GET'])
def obtener_horarios():
    try:
        query = text('SELECT * FROM horarios')
        result = db_session.execute(query).fetchall()
        print(result)
        # Devolver los resultados en formato JSON
        result = db_session.execute(query).fetchall()
        resenas = []
        for resultado in result:
            resena = {
                "dia": resultado.dia,
                "hora_apertura": resultado.hora_apertura.strftime('%H:%M:%S') if isinstance(resultado.hora_apertura, time) else resultado.hora_apertura,
                "hora_cierre": resultado.hora_cierre.strftime('%H:%M:%S') if isinstance(resultado.hora_cierre, time) else resultado.hora_cierre,
                "estado": resultado.estado
            }
            resenas.append(resena)
        # Devolver los resultados en formato JSON
        return jsonify(resenas)
        

    except Exception as error:
        # Manejar errores y devolver una respuesta apropiada
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al obtener los horarios'}), 500

@cross_origin()
@app.route('/api/getservicios', methods=['GET'])
def obtener_servicios():
    try:
        result  = obtener_servicios_activos(db_session)
        servicios = []
        for row in result:
            servicio = {
                "id":row.id,
                "descripcion":row.descripcion,
                "nombre": row.nombre,
                "precio": row.precio
            }
            servicios.append(servicio)
        return jsonify(servicios)
    except Exception as error:
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al obtener los servicios'}), 500


@cross_origin()
@app.route('/api/getserviciosdescripcion', methods=['POST'])
def obtener_servicios_descripcion():
    try:
        # Obtener el filtro de la solicitud JSON
        filtro = request.json.get('filtro', None)

        # Intentar convertir el filtro a un entero, o dejarlo como None si no se puede
        try:
            filtro_id = int(filtro)
        except ValueError:
            filtro_id = None

        # Llamar a la función de consulta de servicios
        result = consultar_servicios(db_session, filtro_id)

        # Transformar los resultados en un formato JSON
        servicios = []
        for row in result:
            servicio = {
                "nombre": row.nombre,
                "descripcion": row.descripcion,
                "precio": row.precio
            }
            servicios.append(servicio)

        # Devolver los servicios como una respuesta JSON
        return jsonify(servicios)

    except Exception as error:
        # Registrar el error para una mejor gestión
        app.logger.error('Error en la función obtener_servicios_descripcion: %s', str(error))
        # Devolver una respuesta de error al cliente
        return jsonify({'error': 'Ocurrió un error al obtener los servicios con descripción'}), 500


@cross_origin()  
@app.route('/api/validarnumerocelular', methods=['POST'])
def validar_numero_celular():
    try:
        numero_celular = request.json.get('numero_celular')
        existe = ValidarNumeroCelularExistente(numero_celular)
        return jsonify({'existe': existe})

    except Exception as error:
       
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al validar el número de celular'}), 500


@cross_origin()  
@app.route('/api/reservacion', methods=['POST'])
def validar_numero_celulars():
    try:
        numero_celular = request.json.get('numero_celular')
        existe = ValidarNumeroCelularExistente(numero_celular)
        return jsonify({'existe': existe})

    except Exception as error:
       
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al validar el número de celular'}), 500


@app.route('/inicio',methods=['GET','POST'])
def inicio():

    return render_template("index.html")

@app.route('/productos',methods=['GET','POST'])
def productos():
    productos = obtener_productos(db_session)
  
    return render_template('productos.html',productos=productos)

@app.route('/CrearProducto', methods=['POST'])
def crear_producto():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
   
    estado = request.form.get('estado')
    archivo = request.files['logo']
    carpeta_destino = 'static/productos'
    logo = guardar_imagen(archivo, carpeta_destino)
    insertar_producto(db_session, nombre, descripcion, logo, estado)
    flash("Se ha registrado correctamente el producto","success")
    return redirect('/productos')


@app.route('/ActualizarProducto', methods=['POST'])
def actualizar_productos():
    id_producto = request.form.get('id')
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    estado=request.form.get('estado')
    archivo = request.files['logo']
    logos=request.form.get('logos')
  
    if archivo:
        carpeta_destino = 'static/img/productos'
        logo = guardar_imagen(archivo, carpeta_destino)
      
        try:
            os.remove(logos)
        except Exception as e:
                print(f"No se pudo eliminar la imagen anterior: {e}")
       
        actualizar_producto(db_session, id_producto, nombre, descripcion, logo, estado)
        flash("Se ha actualizado correctamente el producto", "success")
        return redirect('/productos')
    else:
            # Si no se proporcionó un archivo o la extensión no es permitida, solo actualizar la información sin cambiar la imagen
        actualizar_producto(db_session, id_producto, nombre, descripcion,logos, estado)
        flash("Se ha actualizado correctamente el producto ", "success")
        return redirect('/productos')
  
 
  


@app.route('/CambiarEstadoProducto', methods=['POST'])
def cambiar_estado_producto():
    id_producto = request.form.get('id')
  
    nuevo_estado = request.form.get('estado')
   
    cambiar_estado_productos(db_session, id_producto, nuevo_estado)
    flash("Se ha desactivado el producto","success")
    return redirect('/productos')

@app.route('/precioproducto',methods=['GET','POST'])
def precioproducto():
    return render_template("preciosproductos.html")

@app.route('/CrearPrecio',methods=['GET','POST'])
def crearprecioproducto():
    return redirect('/precioproducto')

@app.route('/CambiarPrecio',methods=['GET','POST'])
def cambiaprecioproducto():
    return redirect('/precioproducto')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)