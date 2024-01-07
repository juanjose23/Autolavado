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

def insertar_persona(db_session: Session, nombre, correo,direccion, celular):
    query = text("INSERT INTO persona (nombre, correo, direccion, celular) VALUES (:nombre, :correo, :direccion, :celular) RETURNING id")
    id_persona = db_session.execute(query, {"nombre": nombre, "correo": correo, "direccion":direccion, "celular": celular}).fetchone()
    return id_persona[0]

def insertar_persona_natural(db_session: Session, id_persona, apellidos,cedula,fecha_nacimiento,genero, tipo):
    query = text("INSERT INTO persona_natural (id_persona, apellido,cedula,fecha_nacimiento,genero, tipo_persona) VALUES (:id_persona, :apellido,:cedula,:fecha_nacimiento,:genero, :tipo_persona)")
    db_session.execute(query, {"id_persona": id_persona, "apellido": apellidos,"cedula":cedula,"fecha_nacimiento":fecha_nacimiento,"genero":genero, "tipo_persona": tipo})

def insertar_cliente(db_session: Session, id_persona,codigo_cliente, tipo):
 
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

def actualizar_trabajador(db_session, id_trabajador, foto, estado):
    query = text("""
        UPDATE trabajador
        SET  foto = :foto, estado = :estado
        WHERE id = :id_trabajador
    """)

    db_session.execute(query, {"id_trabajador": id_trabajador, "foto": foto, "estado": estado})
    db_session.commit()

def cambiar_estado_trabajador(db_session, id_trabajador, nuevo_estado):
    query = text("""
        UPDATE trabajador
        SET estado = :nuevo_estado
        WHERE id = :id_trabajador
    """)

    db_session.execute(query, {"id_trabajador": id_trabajador, "nuevo_estado": nuevo_estado})
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

def insertar_servicio(db_session: Session, nombre, descripcion, foto,realizacion, estado):
    query = text("""
        INSERT INTO servicios (nombre, descripcion, foto,realizacion, estado)
        VALUES (:nombre, :descripcion, :foto,:realizacion, :estado)
    """)

    db_session.execute(query, {"nombre": nombre, "descripcion": descripcion, "foto": foto,"realizacion":realizacion, "estado": estado})
    db_session.commit()

def update_servicio(db_session: Session, id_servicio, nombre, descripcion, foto,realizacion, estado):
    query = text("""
        UPDATE servicios
        SET nombre = :nombre, descripcion = :descripcion, foto = :foto,realizacion =:realizacion, estado = :estado
        WHERE id = :id_servicio
    """)

    db_session.execute(query, {"id_servicio": id_servicio, "nombre": nombre, "descripcion": descripcion, "foto": foto,"realizacion":realizacion, "estado": estado})
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

def insertar_usuario(db_session: Session, id_persona, usuario, contraseña, estado):
    query = text("""
        INSERT INTO usuario ( id_persona, usuario, contraseña, estado)
        VALUES (:id_persona, :usuario, :contraseña, :estado)
    """)

    db_session.execute(query, { "id_persona": id_persona, "usuario": usuario, "contraseña": contraseña, "estado": estado})
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

def obtener_precioproductos(db_session):
    query=text("SELECT pp.*,p.id AS producto, p.nombre FROM precio pp INNER JOIN producto p ON p.id = pp.id_producto ")
    precios=db_session.execute(query).fetchall()
    return precios
def obtener_productos_sin_precio(db_session):
    query = text("""
SELECT p.*
        FROM producto p
        WHERE NOT EXISTS (
            SELECT 1
            FROM precio pp
            WHERE pp.id_producto = p.id
        )
    """)
    productos_sin_precio = db_session.execute(query).fetchall()
    return productos_sin_precio

def ValidarNumeroCelularExistente(numero):
    query = text("SELECT id FROM persona WHERE celular = :numero")
    exists = db_session.execute(query, {"numero": numero}).scalar()
    return exists

def obtener_serviciossistema(db_session: Session):
    query = text("SELECT *  FROM servicios ")
    result = db_session.execute(query).fetchall()
    return result

def obtener_servicios_sin_precio(db_session):
    query = text("""
        SELECT s.*
        FROM servicios s
        WHERE NOT EXISTS (
            SELECT 1
            FROM precio_servicios pp
            WHERE pp.id_servicios = s.id
        )
    """)
    productos_sin_precio = db_session.execute(query).fetchall()
    return productos_sin_precio

def obtener_precios_servicios(db_session):
    query=text("SELECT pp.*,p.id AS producto, p.nombre FROM precio_servicios pp INNER JOIN servicios p ON p.id = pp.id_servicios ")
    precios=db_session.execute(query).fetchall()
    return precios

def ObtenerTrabajadores(db_session:session):
    query=text("""
            SELECT 
                t.id AS trabajador_id, t.codigo, t.foto, t.estado,
                p.id AS persona_id, p.nombre, p.correo, p.direccion, p.celular,
                pn.id AS persona_natural_id, pn.apellido, pn.cedula, pn.fecha_nacimiento, pn.genero, pn.tipo_persona
            FROM trabajador t
            JOIN persona p ON t.id_persona = p.id
            JOIN persona_natural pn ON pn.id_persona = p.id
        """)
    result = db_session.execute(query).fetchall()
    return result
def ObtenerEmpleadoSinUsuario(db_session:session):
    consulta = text("""
           SELECT p.id AS persona_id, p.nombre, p.correo
            FROM persona p
            LEFT JOIN trabajador t ON p.id = t.id_persona
            LEFT JOIN usuario u ON p.id = u.id_persona
            WHERE t.id IS NOT NULL AND u.id IS NULL AND t.estado = 1
        """)
    result=db_session.execute(consulta).fetchall()
    return result

def obtenerusuarios(db_session:session):
    query=text(""" SELECT s.*, p.nombre,pn.apellido FROM usuario s
INNER JOIN persona p ON p.id = s.id_persona
INNER JOIN persona_natural pn ON pn.id =s.id_persona """)
    result=db_session.execute(query).fetchall()
    return result

'''def obtener_cupos_disponibles():
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dia_hoy = datetime.now().strftime('%A')
    fecha_hoy = datetime.now().date()

   

    # Obtiene todos los horarios disponibles para los próximos 7 días
    query_horarios = text("""
        SELECT * FROM horarios
        WHERE estado = 1
    """)
    horarios_disponibles = db_session.execute(query_horarios).fetchall()

    # Lista para almacenar la información de los horarios y cupos disponibles
    horarios_resultado = []

    for horario in horarios_disponibles:
        dia_horario, hora_apertura, hora_cierre = horario[1], horario[2], horario[3]

        # Verifica que el día del horario esté en los próximos 7 días
        if dia_horario not in dias_semana:
            continue

        # Si el estado es 2 (Domingo), omitir ese horario
        if horario[4] == 2:
            continue

        # Calcula la fecha del horario sumando días
        idx_dia_horario = dias_semana.index(dia_horario)
        fecha_horario = fecha_hoy + timedelta(days=(idx_dia_horario - fecha_hoy.weekday() + 7) % 7)

        # Consulta para obtener las reservaciones en el intervalo horario
        query_reservaciones = text("""
            SELECT COUNT(*) FROM reservacion
            WHERE idhorario = :id_horario
            AND fecha = :fecha
            AND hora >= :hora_apertura
            AND hora <= :hora_cierre
        """)
        reservaciones = db_session.execute(query_reservaciones, {
            'id_horario': horario[0],
            'fecha': fecha_horario,
            'hora_apertura': hora_apertura,
            'hora_cierre': hora_cierre
        }).scalar()

        # Calcula la cantidad de cupos disponibles
        duracion_servicio = 2  # Duración del servicio en horas
        cupos_disponibles = (hora_cierre.hour - hora_apertura.hour) // duracion_servicio - reservaciones

        # Almacena la información del horario y cupos disponibles en la lista
        horario_info = {
            "dia": dia_horario,
            "fecha": fecha_horario,
            "hora_apertura": hora_apertura,
            "hora_cierre": hora_cierre,
            "cupos_disponibles": cupos_disponibles
        }
        horarios_resultado.append(horario_info)

  

    # Retorna la lista de horarios y cupos disponibles
    return horarios_resultado '''

def obtener_cupos_disponibles():
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    fecha_hoy = datetime.now().date()

    # Obtiene todos los horarios disponibles para los próximos 7 días
    query_horarios = text("""
        SELECT * FROM horarios
        WHERE estado = 1
    """)
    horarios_disponibles = db_session.execute(query_horarios).fetchall()

    # Lista para almacenar la información de los horarios y cupos disponibles
    horarios_resultado = []

    for horario in horarios_disponibles:
        dia_horario, hora_apertura, hora_cierre = horario[1], horario[2], horario[3]

        # Si el estado es 2 (Domingo), omitir ese horario
        if horario[4] == 2:
            continue

        # Calcula la fecha del horario sumando días
        idx_dia_horario = dias_semana.index(dia_horario)
        fecha_horario = fecha_hoy + timedelta(days=(idx_dia_horario - fecha_hoy.weekday() + 7) % 7)

        # Calcula la cantidad de cupos disponibles
        duracion_servicio = 1.40  # Duración del servicio en horas
        total_minutos = (hora_cierre.hour - hora_apertura.hour) * 60 + (hora_cierre.minute - hora_apertura.minute)
        cupos_disponibles = int(total_minutos / (duracion_servicio * 60))

        # Almacena la información del horario y cupos disponibles en la lista
        horario_info = {
            "dia": dia_horario,
            "fecha": fecha_horario,
            "hora_apertura": hora_apertura,
            "hora_cierre": hora_cierre,
            "cupos_disponibles": cupos_disponibles
        }

        # Verifica si el horario es para el día actual
        if fecha_horario == fecha_hoy:
            # Añade información adicional para el día actual
            horario_info["dia_actual"] = True
            horario_info["cupos_hoy"] = obtener_cupos_hoy(horario, fecha_hoy)

        horarios_resultado.append(horario_info)

    # Retorna la lista de horarios y cupos disponibles
    return horarios_resultado


def obtener_cupos_hoy(horario, fecha_hoy):
    # Supongamos que tienes una tabla 'reservas' con un campo 'fecha_reserva' y 'id_horario'
    # que almacena las reservas realizadas por día.
    # Esta función debería contar cuántas reservas hay para el día actual y el horario dado.

    id_horario = horario[0]  # Supongamos que el ID del horario está en la posición 0 del resultado de la consulta
    fecha_actual_str = fecha_hoy.strftime('%Y-%m-%d')

    # Consulta para obtener la cantidad de reservas para el día actual y el horario actual
    query_reservas_hoy = text("""
        SELECT COUNT(*) FROM reservacion
        WHERE fecha = :fecha_actual
        AND idhorario = :id_horario
    """)

    # Ejecutar la consulta con los parámetros necesarios
    cupos_hoy = db_session.execute(query_reservas_hoy, {"fecha_actual": fecha_actual_str, "id_horario": id_horario}).scalar()

    return cupos_hoy
def mostrar_fechas_y_horas_reservas():
    # Obtener la fecha de hoy
    fecha_hoy = datetime.now().date()

    # Calcular la fecha hasta la cual deseas mostrar las reservas (7 días en el futuro)
    fecha_fin = fecha_hoy + timedelta(days=7)

    # Consultar las reservas dentro del rango de fechas
    query_reservas = text("""
        SELECT fecha, hora
        FROM reservacion
        WHERE fecha BETWEEN :fecha_hoy AND :fecha_fin
    """)

    # Ejecutar la consulta con los parámetros necesarios
    result = db_session.execute(query_reservas, {"fecha_hoy": fecha_hoy, "fecha_fin": fecha_fin}).fetchall()

    # Mostrar las fechas y horas de las reservas
    fechas_horas_reservas = [(reserva[0].strftime("%Y-%m-%d"), reserva[1].strftime("%H:%M:%S")) for reserva in result]

    return fechas_horas_reservas

def actualizar_horarios_con_reservas(horarios, reservas):
    for reserva in reservas:
        fecha_reserva, hora_reserva = reserva
        for horario in horarios:
            if fecha_reserva == horario["fecha"]:
                # Encuentra la hora de la reserva en la lista de horas_cupos
                if hora_reserva in horario["horas_cupos"]:
                    # Ajusta las horas_cupos y los cupos disponibles
                    ajustar_cupos_con_reserva(horario, hora_reserva)
    
    return horarios  # Retorna la lista de horarios actualizada

def ajustar_cupos_con_reserva(horario, hora_reserva):
    # Encuentra la posición de la hora_reserva en la lista de horas_cupos
    index_hora_reserva = horario["horas_cupos"].index(hora_reserva)
    
    # Calcula la duración del servicio en minutos
    duracion_servicio = 1 * 60 + 40  # Supongamos que la duración es 1 hora y 40 minutos
    
    # Ajusta las horas_cupos eliminando la hora_reserva y sumando la duración del servicio
    horario["horas_cupos"] = horario["horas_cupos"][:index_hora_reserva] + \
                             [hora_reserva + timedelta(minutes=duracion_servicio * i) for i in range(1, horario["cupos_disponibles"] + 1)] + \
                             horario["horas_cupos"][index_hora_reserva + 1:]
    
    # Ajusta los cupos disponibles restando 1
    horario["cupos_disponibles"] -= 1
from flask_mail import Message

def enviar_correo_con_contraseña(nombre,nombre_usuario, correo_destino, contraseña):
    cuerpo = f'''
    Estimado(a) {nombre},

    Aquí tienes las credenciales para acceder a tu cuenta:
    Usuarios:{nombre_usuario}
    Contraseña: {contraseña}

    Por favor, asegúrate de cambiar tu contraseña una vez que hayas iniciado sesión en tu cuenta.

    Si tienes alguna pregunta o necesitas asistencia adicional, no dudes en contactarnos.

    ¡Gracias y ten un excelente día!

    Atentamente,
    Lavacar ASOCATIE
    '''

    asunto = 'Asignación de credenciales - Acceso a cuenta'
    remitente = 'ingsoftwar123@gmail.com'
    destinatario = [correo_destino]

    msg = Message(asunto, sender=remitente, recipients=destinatario)
    msg.body = cuerpo
    mail.send(msg)

def BuscarPorIdPersona(db_session: Session, id):
    query = text("""
            SELECT p.nombre, pn.apellido,p.correo
            FROM persona p
            JOIN persona_natural pn ON p.id = pn.id_persona
            WHERE pn.id = :id
        """)

    resultado = db_session.execute(query, {"id": id}).fetchone()
    return resultado
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

            id_persona = insertar_persona(db_session, nombre, correo,"En direccion", celular)
            insertar_persona_natural(db_session, id_persona, apellidos,null,null,null, tipo)
            codigo = generar_codigo_cliente(nombre,id_persona,celular)
            codigo_cliente=insertar_cliente(db_session, id_persona,codigo, tipo)

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
        id_persona = insertar_persona(db_session, nombre,"No hay","En direccion", celular)
        codigo = generar_codigo_cliente(nombre,id_persona,celular)
        codigo_cliente=insertar_cliente(db_session, id_persona,codigo,"Cliente no registrado")

        db_session.commit()

        return jsonify({"codigo_cliente": codigo_cliente}), 200
        
    return 'null', 400



@app.route('/')
def index():
    horarios_resultado = obtener_cupos_disponibles()
    reservas = mostrar_fechas_y_horas_reservas()

    # Crear la lista de horarios
    lista_horarios = []

    for horario in horarios_resultado:
        horario_info = {
            "dia": horario["dia"],
            "fecha": horario["fecha"],
            "hora_apertura": horario["hora_apertura"],
            "hora_cierre": horario["hora_cierre"],
            "cupos_disponibles": horario["cupos_disponibles"],
            "horas_cupos": horario.get("horas_cupos", []).copy()  # Usar get para manejar la ausencia de 'horas_cupos'
        }

    lista_horarios.append(horario_info)

    # Actualizar la lista de horarios con las reservas
    lista_horarios_actualizada = actualizar_horarios_con_reservas(lista_horarios, reservas)

    # Imprimir la lista actualizada de horarios
    print("Lista de horarios actualizada:")
    print(lista_horarios_actualizada)
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
    carpeta_destino = 'static/img/productos'
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
    Precios=obtener_precioproductos(db_session);
    productos=obtener_productos_sin_precio(db_session)
    return render_template("precioproducto.html",productos=productos,Precios=Precios)

@app.route('/CrearPrecio',methods=['GET','POST'])
def crearprecioproducto():
    idproducto=request.form.get('idproducto')
    precio=request.form.get('precio')
    estado=request.form.get('estado')
    insertar_precio(db_session,idproducto,precio,estado)
    flash("Se ha registrado correctamente el precio","success")
    return redirect('/precioproducto')

@app.route('/CambiarPrecio/<int:id>',methods=['GET','POST'])
def cambiaprecioproducto(id):
    idproducto=request.form.get('idproducto')
    precio=request.form.get('precio')
    estado=request.form.get('estado')
    print("Id producto",idproducto)
    print("Precio nuevo",precio)
    print("estado:",estado)

    print("Precio que pasa hacer inactivo:",id)

    insertar_precio(db_session,idproducto,precio,estado)

    cambiar_estado_precio(db_session,id,2)
    flash("Se ha registrado correctamente el precio","success")
    return redirect('/precioproducto')

@app.route('/CambiarPrecioestado/<int:id>',methods=['GET','POST'])
def cambiaprecioproductoestado(id):
   
    cambiar_estado_precio(db_session,id,2)
    flash("Se ha desactivado  correctamente el precio","success")
    return redirect('/precioproducto')

@app.route('/servicios')
def servicios():
    servicios=obtener_serviciossistema(db_session)
    return render_template("servicios.html" ,servicios=servicios)

@app.route("/crearservicio", methods=["POST"])
def crearservicios():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    estado = request.form.get('estado')
    realizacion=request.form.get('realizacion')
    archivo = request.files['foto']
    carpeta_destino = 'static/img/servicios'
    logo = guardar_imagen(archivo, carpeta_destino)
    insertar_servicio(db_session,nombre,descripcion,logo,realizacion,estado)
    flash("Se ha registrado correctamente el servicios", "success")
    return redirect('/servicios')


@app.route('/actualizar_servicios/<int:servicio_id>', methods=['POST', 'GET'])
def actualizar_servicio(servicio_id):
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    estado = request.form.get('estado')
    realizacion=request.form.get('realizacion')
    archivo = request.files['foto']
    logos = request.form.get('logos')

    if archivo:
        carpeta_destino = 'static/img/servicios'
        logo = guardar_imagen(archivo, carpeta_destino)

        # Suponiendo que 'logos' es la ruta del archivo antiguo almacenada en la base de datos
        try:
            os.remove(logos)
        except Exception as e:
            print(f"No se pudo eliminar la imagen anterior: {e}")

        update_servicio(db_session, servicio_id, nombre, descripcion, logo,realizacion, estado)
        flash("Se ha actualizado correctamente el servicio", "success")
        return redirect(url_for('servicios'))

    update_servicio(db_session, servicio_id, nombre, descripcion, logos,realizacion, estado)
    flash("Se ha actualizado correctamente el servicio", "success")
    return redirect(url_for('servicios'))

@app.route('/eliminar_servicio/<int:servicio_id>', methods=['POST', 'GET'])
def eliminar_servicio(servicio_id):
    cambiar_estado_servicio(db_session,servicio_id,2)
    flash("se ha desactivado el servicio", "success")
    return redirect("/servicios")

@app.route("/precio_servicios",methods=['GET','POST'])
def preciosservicios():
    servicios=obtener_servicios_sin_precio(db_session)
    Preciosservicios=obtener_precios_servicios(db_session)
    return render_template("preciosservicios.html", servicios= servicios, Preciosservicios= Preciosservicios)
@app.route('/CrearServiciosPrecios',methods=['GET','POST'])
def crearprecioservicios():
    idproducto=request.form.get('idproducto')
    precio=request.form.get('precio')
    estado=request.form.get('estado')
    insertar_precio_servicio(db_session,idproducto,precio,estado)
    flash("Se ha registrado correctamente el precio","success")
    return redirect('/precio_servicios')

@app.route('/CambiarServicios/<int:id>',methods=['GET','POST'])
def cambiaprecioservicios(id):
    idproducto=request.form.get('idproducto')
    precio=request.form.get('precio')
    estado=request.form.get('estado')
    print("Precio que pasa hacer inactivo:",id)

    insertar_precio_servicio(db_session,idproducto,precio,estado)

    cambiar_estado_precio_servicio(db_session,id,2)
    flash("Se ha registrado correctamente el precio","success")
    return redirect('/precio_servicios')

@app.route('/CambiarServiciosestado/<int:id>',methods=['GET','POST'])
def cambiaprecioproductoestadoservcios(id):
   
    cambiar_estado_precio_servicio(db_session,id,2)
    flash("Se ha desactivado  correctamente el precio","success")
    return redirect('/precio_servicios')

@app.route('/trabajador',methods=['GET','POST'])
def trabajador():
    trabajadores = ObtenerTrabajadores(db_session)
    return render_template("trabajador.html",trabajadores=trabajadores)

@app.route('/crear_trabajador',methods=['POST'])
def crear_trabajador():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    cedula = request.form.get('cedula')
    fecha = request.form.get('fecha_nacimiento')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion')
    genero = request.form.get('genero')
    celular = request.form.get('celular')
    estado = request.form.get('estado')
    codigo= generar_codigo_trabajador(db_session)
    archivo = request.files['foto']
    carpeta_destino = 'static/img/trabajadores'
    logo = guardar_imagen(archivo, carpeta_destino)
    IdPersona=insertar_persona(db_session,nombre,correo,direccion,celular)
    insertar_persona_natural(db_session,IdPersona,apellido,cedula,fecha,genero,"Persona Natural")
    insertar_trabajador(db_session,IdPersona,codigo,logo,estado)
    flash("Se ha registrado con exito","success")
    return redirect('/trabajador')

@app.route('/actualizar_trabajador/<int:id>',methods=['POST'])
def actualizar_trabajadors(id):
    persona=request.form.get('persona')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion')
    celular = request.form.get('celular')
    estado = request.form.get('estado')
    archivo = request.files['foto']
    logos=request.form.get('logos')
    if archivo:
        carpeta_destino = 'static/img/trabajadores'
        logo = guardar_imagen(archivo, carpeta_destino)
        try:
            os.remove(logos)
        except Exception as e:
            print(f"No se pudo eliminar la imagen anterior: {e}")

        update_persona(db_session,persona,nombre,correo,celular,direccion)
        update_persona_natural(db_session,persona,apellido,"Persona Natural")
        print(id)
        actualizar_trabajador(db_session,id,logo,estado)
        flash("Se ha actualizado con exito ","success")
        return redirect('/trabajador')
    else:
        update_persona(db_session,persona,nombre,correo,celular,direccion)
        update_persona_natural(db_session,persona,apellido,"Persona Natural")
        actualizar_trabajador(db_session,id,logos,estado)
        flash("Se ha actualizado con exito ","success")
        return redirect('/trabajador')
    
@app.route('/eliminar_trabajador/<int:id>',methods=['POST'])
def eliminar_trabajadors(id):
    cambiar_estado_trabajador(db_session,id,2)
    flash("Se ha desactivado correctamente el trabajador","success")
    return redirect('/trabajador')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404  

@app.route("/usuarios",methods=['GET','POST'])
def usuarios():
    trabajador=ObtenerEmpleadoSinUsuario(db_session)
    usuarios=obtenerusuarios(db_session)
    return render_template("usuarios.html",trabajador=trabajador,usuarios=usuarios)

@app.route("/crearusuarios", methods=['GET', 'POST'])
def crear_usuario():
    id = request.form.get('idpersona')
    contraseña = generar_contraseña()
    hashed_password = generate_password_hash(contraseña)
    persona = BuscarPorIdPersona(db_session, id)
    
   
    if persona:
        nombre, apellido, correo = persona
        nombres = nombre + ' ' + apellido
        usuario = generar_nombre_usuario(nombre, apellido, id)
        enviar_correo_con_contraseña(nombres, usuario, correo, contraseña)
        insertar_usuario(db_session, id, usuario, hashed_password, 0)

   
        flash("Se ha agregado correctamente el usuario!", "success")
        flash("Se ha enviado un correo correctamente con la contraseña para su acceso a la plataforma", "info")
        return redirect('/usuarios')
    else:
        return redirect('/usuarios')
    
@app.route("/verificar_usuarios",methods=['GET','POST'])
def verificar_usuarios():
    id = request.form.get('id')
    cambiar_estado_usuario(db_session,id,1)
    flash("Se ha activado correctamente!", "success")
    return redirect('/usuarios')

@app.route("/eliminar_usuario",methods=['GET','POST'])
def eliminar_usuarios():
    id = request.form.get('id')
    cambiar_estado_usuario(db_session,id,2)
    flash("Se ha desactivado correctamente!", "success")
    return redirect('/usuarios')

@app.route("/login",methods=['GET','POST'])
def login():
    return render_template("login.html") 
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)