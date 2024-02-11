from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from decimal import *
import datetime
from datetime import *
from flask import *
from flask_mail import *
from flask_cors import *
from werkzeug.security import *
from flask_session import Session
from sqlalchemy import *
from sqlalchemy.orm import *
from utils import *
from flask import session
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pytz import timezone
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
from io import BytesIO
import pdfkit
import random
import string
import locale
import pickle
import arrow

# Configura el locale a español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')


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
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
engine = create_engine(os.getenv("DATABASE_URL"))
db_session = scoped_session(sessionmaker(bind=engine))


def insertar_persona(db_session: Session, nombre, correo, direccion, celular):
    # Preparar y ejecutar una consulta SQL
    query = text(
        "INSERT INTO persona (nombre, correo, direccion, celular) VALUES (:nombre, :correo, :direccion, :celular) RETURNING id")
    result = db_session.execute(query, {
                                "nombre": nombre, "correo": correo, "direccion": direccion, "celular": celular})

    # Obtener el ID de la nueva persona
    id_persona = result.fetchone()[0]

    # Hacer commit para persistir la nueva persona en la base de datos
    db_session.commit()
    db_session.close() 

    # Retornar el ID de la nueva persona
    return id_persona


def insertar_persona_natural(db_session: Session, id_persona, apellidos, cedula, fecha_nacimiento, genero, tipo):
    query = text("INSERT INTO persona_natural (id_persona, apellido,cedula,fecha_nacimiento,genero, tipo_persona) VALUES (:id_persona, :apellido,:cedula,:fecha_nacimiento,:genero, :tipo_persona)")
    db_session.execute(query, {"id_persona": id_persona, "apellido": apellidos, "cedula": cedula,
                       "fecha_nacimiento": fecha_nacimiento, "genero": genero, "tipo_persona": tipo})
    db_session.commit()
    db_session.close() 

def obtener_id_cliente_por_celular(db_session, numero_celular):
    query = text("SELECT clientes.id FROM clientes JOIN persona ON clientes.id_persona = persona.id WHERE persona.celular = :celular")
    result = db_session.execute(query, {"celular": numero_celular})
    id_cliente = result.fetchone()
    db_session.close() 
    return id_cliente[0] if id_cliente else None

def insertar_cliente(db_session: Session, id_persona, codigo_cliente, tipo, foto):

    query = text("INSERT INTO clientes (id_persona, codigo, tipo_cliente, foto, estado) VALUES (:id_persona, :codigo, :tipo_cliente, :foto, :estado)")
    db_session.execute(query, {"id_persona": id_persona, "codigo": codigo_cliente,
                       "tipo_cliente": tipo, "foto": foto, "estado": '1'})
    db_session.commit()
    db_session.close() 
    return codigo_cliente


def update_persona(db_session: Session, id_persona, nombre, correo, celular, direccion):
    query = text(
        "UPDATE persona SET nombre = :nombre, correo = :correo, direccion = :direccion, celular = :celular WHERE id = :id_persona")
    db_session.execute(query, {"id_persona": id_persona, "nombre": nombre,
                       "correo": correo, "direccion": direccion, "celular": celular})
    db_session.commit()
    db_session.close() 


def update_persona_natural(db_session: Session, id_persona, apellidos, tipo):
    query = text(
        "UPDATE persona_natural SET apellido = :apellidos, tipo_persona = :tipo WHERE id_persona = :id_persona")
    db_session.execute(
        query, {"id_persona": id_persona, "apellidos": apellidos, "tipo": tipo})
    db_session.commit()
    db_session.close() 


def update_cliente(db_session: Session, id_persona, tipo, foto, estado):
    query = text(
        "UPDATE clientes SET tipo_cliente = :tipo, foto = :foto, estado = :estado WHERE id = :id_persona")
    db_session.execute(
        query, {"id_persona": id_persona, "tipo": tipo, "foto": foto, "estado": estado})
    db_session.commit()
    db_session.close() 

def cambiar_estado_cliente(db_session: Session, id_persona, nuevo_estado):
    query = text(
        "UPDATE clientes SET estado = :nuevo_estado WHERE id = :id_persona")
    db_session.execute(
        query, {"id_persona": id_persona, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close() 


def generar_codigo_reservacion(db_session):
    # Obtener el último ID de la tabla reservacion
    query_last_id = text("SELECT MAX(id) FROM reservacion")
    last_id = db_session.execute(query_last_id).fetchone()[0]

    # Calcular el nuevo ID
    new_id = last_id + 1 if last_id else 1

    # Generar el código R-ID
    codigo = f"R-{new_id}"

    # Verificar que el código no exista ya en la base de datos
    query = text("SELECT COUNT(*) FROM reservacion WHERE codigo = :codigo")
    count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]

    while count > 0:
        # Si existe, recalcular el nuevo ID y el código
        new_id += 1
        codigo = f"R-{new_id}"
        count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]
    db_session.close() 
    return codigo


def generar_codigo_trabajador(db_session: Session):
    codigo = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=8))

    # Verificar que el código no exista ya en la base de datos
    query = text("SELECT COUNT(*) FROM trabajador WHERE codigo = :codigo")
    count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]

    while count > 0:
        codigo = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=8))
        count = db_session.execute(query, {"codigo": codigo}).fetchone()[0]
    db_session.close()     
    return codigo


def insertar_trabajador(db_session, id_persona, codigo, foto, estado):
    query = text("""
        INSERT INTO trabajador (id_persona, codigo, foto, estado)
        VALUES (:id_persona, :codigo, :foto, :estado)
    """)

    db_session.execute(query, {"id_persona": id_persona,
                       "codigo": codigo, "foto": foto, "estado": estado})
    db_session.commit()
    db_session.close() 


def actualizar_trabajador(db_session, id_trabajador, foto, estado):
    query = text("""
        UPDATE trabajador
        SET  foto = :foto, estado = :estado
        WHERE id = :id_trabajador
    """)

    db_session.execute(
        query, {"id_trabajador": id_trabajador, "foto": foto, "estado": estado})
    db_session.commit()
    db_session.close() 


def cambiar_estado_trabajador(db_session, id_trabajador, nuevo_estado):
    query = text("""
        UPDATE trabajador
        SET estado = :nuevo_estado
        WHERE id = :id_trabajador
    """)

    db_session.execute(
        query, {"id_trabajador": id_trabajador, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close() 
def obtener_id_y_precio_servicio(db_session, nombre_servicio):
    try:
        # Realizar la consulta SQL utilizando text
        query = text("""
            SELECT s.id AS id_servicio, ps.precio
            FROM servicios s
            JOIN precio_servicios ps ON s.id = ps.id_servicios
            WHERE s.nombre = :nombre_servicio AND ps.estado = 1
            ORDER BY ps.fecha_registro DESC
            LIMIT 1
        """)

        resultado = db_session.execute(query, {"nombre_servicio": nombre_servicio}).fetchone()
        db_session.close() 
        if resultado:
            # Retornar el id y el precio
            return {"id_servicio": resultado[0], "precio": float(resultado[1])}
        else:
            return None

    except Exception as e:
        print(f"Error al obtener el servicio: {e}")
        return None

def insertar_reservacion(db_session,idcliente,idservicio,idevento_calendar,codigo,fecha,hora_inicio,hora_fin,subtotal,estado):
    try:
        # Preparar y ejecutar una consulta SQL
        query = text("""
            INSERT INTO reservacion 
            (idcliente, idservicio, idevento_calendar, codigo, fecha, hora_inicio, hora_fin, subtotal, estado) 
            VALUES 
            (:idcliente, :idservicio, :idevento_calendar, :codigo, :fecha, :hora_inicio, :hora_fin, :subtotal, :estado) 
            RETURNING id
        """)
        result = db_session.execute(
            query,
            {
                "idcliente": idcliente,
                "idservicio": idservicio,
                "idevento_calendar": idevento_calendar,
                "codigo": codigo,
                "fecha": fecha,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "subtotal": subtotal,
                "estado": estado
            }
        )

        # Obtener el ID de la nueva reservación
        id_reservacion = result.fetchone()[0]

        # Hacer commit para persistir la nueva reservación en la base de datos
        db_session.commit()
        db_session.close() 

        # Retornar el ID de la nueva reservación
        return id_reservacion

    except Exception as error:
        # Manejar cualquier error que pueda ocurrir durante la inserción
        print(f"Error al insertar reservación: {error}")
        db_session.rollback()
        db_session.close()
        return None


def insertar_producto(db_session: Session, nombre, descripcion, logo, tipo, estado):
    query = text("""
        INSERT INTO producto (nombre, descripcion, logo, tipo, estado)
        VALUES (:nombre, :descripcion, :logo, :tipo, :estado)
    """)

    db_session.execute(query, {
        "nombre": nombre, "descripcion": descripcion, "logo": logo, "tipo": tipo, "estado": estado
    })
    db_session.commit()
    db_session.close() 

# Actualizar producto
def actualizar_producto(db_session: Session, id_producto, nombre, descripcion, logo, tipo, estado):
    query = text("""
        UPDATE producto
        SET nombre = :nombre, descripcion = :descripcion, logo = :logo, tipo = :tipo, estado = :estado
        WHERE id = :id_producto
    """)

    db_session.execute(query, {
        "id_producto": id_producto, "nombre": nombre, "descripcion": descripcion, 
        "logo": logo, "tipo": tipo, "estado": estado
    })
    db_session.commit()
    db_session.close() 

# Cambiar estado del producto


def cambiar_estado_productos(db_session, id_producto, nuevo_estado):
    # Tu lógica para cambiar el estado del producto aquí
    query = text(
        "UPDATE producto SET estado = :nuevo_estado WHERE id = :id_producto")
    db_session.execute(
        query, {"id_producto": id_producto, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close() 
    # Puedes retornar algo si es necesario
    return "Estado del producto cambiado exitosamente"


def insertar_precio(db_session: Session, id_producto, precio, estado):
    fecha_actual = datetime.now().date()
    query = text("""
        INSERT INTO precio (id_producto, precio, fecha_registro, estado)
        VALUES (:id_producto, :precio,:fecha_registro, :estado)
    """)

    db_session.execute(query, {"id_producto": id_producto, "precio": precio,
                       "fecha_registro": fecha_actual, "estado": estado})
    db_session.commit()
    db_session.close() 


def cambiar_estado_precio(db_session: Session, id_precio, nuevo_estado):
    query = text("""
        UPDATE precio
        SET estado = :nuevo_estado
        WHERE id = :id_precio
    """)

    db_session.execute(
        query, {"id_precio": id_precio, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close() 


def insertar_horario(db_session: Session, dia, hora_apertura, hora_cierre, estado):
    query = text("""
        INSERT INTO horarios (dia, hora_apertura, hora_cierre, estado)
        VALUES (:dia, :hora_apertura, :hora_cierre, :estado)
    """)

    db_session.execute(query, {"dia": dia, "hora_apertura": hora_apertura,
                       "hora_cierre": hora_cierre, "estado": estado})
    db_session.commit()
    db_session.close() 


def update_horario(db_session: Session, id_horario, dia, hora_apertura, hora_cierre, estado):
    query = text("""
        UPDATE horarios
        SET dia = :dia, hora_apertura = :hora_apertura, hora_cierre = :hora_cierre, estado = :estado
        WHERE id = :id_horario
    """)

    db_session.execute(query, {"id_horario": id_horario, "dia": dia,
                       "hora_apertura": hora_apertura, "hora_cierre": hora_cierre, "estado": estado})
    db_session.commit()
    db_session.close()

def cambiar_estado_horario(db_session: Session, id_horario, nuevo_estado):
    query = text("""
        UPDATE horarios
        SET estado = :nuevo_estado
        WHERE id = :id_horario
    """)

    db_session.execute(
        query, {"id_horario": id_horario, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close()


def insertar_servicio(db_session: Session, nombre, descripcion, foto, realizacion, estado):
    query = text("""
        INSERT INTO servicios (nombre, descripcion, foto,realizacion, estado)
        VALUES (:nombre, :descripcion, :foto,:realizacion, :estado)
    """)

    db_session.execute(query, {"nombre": nombre, "descripcion": descripcion,
                       "foto": foto, "realizacion": realizacion, "estado": estado})
    db_session.commit()
    db_session.close() 


def update_servicio(db_session: Session, id_servicio, nombre, descripcion, foto, realizacion, estado):
    query = text("""
        UPDATE servicios
        SET nombre = :nombre, descripcion = :descripcion, foto = :foto,realizacion =:realizacion, estado = :estado
        WHERE id = :id_servicio
    """)

    db_session.execute(query, {"id_servicio": id_servicio, "nombre": nombre,
                       "descripcion": descripcion, "foto": foto, "realizacion": realizacion, "estado": estado})
    db_session.commit()
    db_session.close() 


def cambiar_estado_servicio(db_session: Session, id_servicio, nuevo_estado):
    query = text("""
        UPDATE servicios
        SET estado = :nuevo_estado
        WHERE id = :id_servicio
    """)

    db_session.execute(
        query, {"id_servicio": id_servicio, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close() 


def insertar_precio_servicio(db_session: Session, id_servicio, precio, estado):
    fecha_actual = datetime.now().date()
    query = text("""
        INSERT INTO precio_servicios (id_servicios, precio, fecha_registro, estado)
        VALUES (:id_servicio, :precio,:fecha_registro, :estado)
    """)

    db_session.execute(query, {"id_servicio": id_servicio, "precio": precio,
                       "fecha_registro": fecha_actual, "estado": estado})
    db_session.commit()
    db_session.close() 


def update_precio_servicio(db_session: Session, id_precio_servicio, id_servicio, precio, estado):
    query = text("""
        UPDATE precio_servicios
        SET id_servicios = :id_servicio, precio = :precio, estado = :estado
        WHERE id = :id_precio_servicio
    """)

    db_session.execute(query, {"id_precio_servicio": id_precio_servicio,
                       "id_servicio": id_servicio, "precio": precio, "estado": estado})
    db_session.commit()
    db_session.close() 


def cambiar_estado_precio_servicio(db_session: Session, id_precio_servicio, nuevo_estado):
    query = text("""
        UPDATE precio_servicios
        SET estado = :nuevo_estado
        WHERE id = :id_precio_servicio
    """)

    db_session.execute(
        query, {"id_precio_servicio": id_precio_servicio, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close() 


def insertar_movimiento_inventario(db_session, id_lote, tipo_movimiento, cantidad):
    # Obtener la fecha y hora actual
    fecha_actual = datetime.now()

    # Consulta para insertar el movimiento y actualizar la fecha
    query = text("""
        INSERT INTO movimiento_inventario (id_lote, tipo_movimiento, cantidad, fecha_movimiento)
        VALUES (:id_lote, :tipo_movimiento, :cantidad, :fecha_movimiento)
    """)

    # Ejecutar la consulta
    db_session.execute(query, {
        "id_lote": id_lote,
        "tipo_movimiento": tipo_movimiento,
        "cantidad": cantidad,
        "fecha_movimiento": fecha_actual
    })

    # Commit los cambios en la sesión
    db_session.commit()
    db_session.close() 


def obtener_movimientos_por_lote(db_session):
    query = text("""
        SELECT lp.numero_lote, mi.tipo_movimiento, mi.cantidad, mi.fecha_movimiento
        FROM lote_producto lp
        LEFT JOIN movimiento_inventario mi ON lp.id = mi.id_lote
    """)

    result = db_session.execute(query).fetchall()
    db_session.close() 
    return result


def actualizar_estado_lotes(db_session: Session):
    fecha_actual = date.today()

    # Inicializar estadísticas
    estadisticas = {
        'por_vencerse': 0,
        'vencidos': 0,
        'sin_cantidad': 0
    }

    # Actualizar estado a 1 (Por vencerse) o 3 (Por vencerse largo) para los lotes que tienen fecha de vencimiento próxima
    query_por_vencer = text("""
        UPDATE lote_producto
        SET estado = CASE 
            WHEN fecha_vencimiento IS NOT NULL AND fecha_vencimiento >= :fecha_actual THEN 
                CASE 
                    WHEN fecha_vencimiento < :fecha_proxima THEN 3  -- Por vencerse largo
                    ELSE  1 -- Por vencerse
                END
            ELSE 1 -- Otro estado (si es necesario)
        END
        WHERE estado NOT IN (2, 4)
    """)

    # Definir la fecha límite para considerar como "por vencerse largo"
    # Puedes ajustar el número de días según tus necesidades
    fecha_proxima = fecha_actual + timedelta(days=30)

    result_por_vencer = db_session.execute(
        query_por_vencer, {"fecha_actual": fecha_actual, "fecha_proxima": fecha_proxima})
    db_session.commit()
    estadisticas['por_vencerse'] = result_por_vencer.rowcount

    # Actualizar estado a 2 (Vencido) para los lotes que ya han vencido
    query_vencidos = text("""
        UPDATE lote_producto
        SET estado = 2
        WHERE fecha_vencimiento IS NOT NULL
        AND fecha_vencimiento < :fecha_actual
        AND estado NOT IN (2, 4)
    """)
    result_vencidos = db_session.execute(
        query_vencidos, {"fecha_actual": fecha_actual})
    db_session.commit()
    estadisticas['vencidos'] = result_vencidos.rowcount

    # Actualizar estado a 4 (Sin cantidad) para los lotes que no tienen cantidad disponible
    query_sin_cantidad = text("""
        UPDATE lote_producto
        SET estado = 4
        WHERE cantidad <= 0
        AND estado NOT IN (2, 4)
    """)
    result_sin_cantidad = db_session.execute(query_sin_cantidad)
    db_session.commit()
    estadisticas['sin_cantidad'] = result_sin_cantidad.rowcount
    db_session.close() 
    return estadisticas


def generar_codigo_venta(db_session: Session):
    # Obtener el último ID de venta desde la base de datos
    query = text("SELECT MAX(id) FROM venta")
    resultado = db_session.execute(query).scalar()
    db_session.close() 
    # Generar el código de venta basado en el último ID
    nuevo_id_venta = resultado + 1 if resultado else 1
    codigo_venta = f'V-{nuevo_id_venta}'

    return codigo_venta


def insertar_venta(db_session, id_tipo, id_cliente, codigo, descuento, total, estado):
    fecha_actual = datetime.now().date()
    query = text("""
        INSERT INTO venta (id_tipo, id_cliente, codigo, fecha, descuento, total, estado)
        VALUES (:id_tipo, :id_cliente, :codigo, :fecha, :descuento, :total, :estado)
        RETURNING id
    """)

    result = db_session.execute(query, {
        'id_tipo': id_tipo,
        'id_cliente': id_cliente,
        'codigo': codigo,
        'fecha': fecha_actual,
        'descuento': descuento,
        'total': total,
        'estado': estado
    })

    # Recuperar el ID de la venta recién insertada
    id_venta = result.fetchone()[0]
    db_session.commit()
    db_session.close() 

    return id_venta


def insertar_venta_producto(db_session: Session, id_venta, id_producto, precio, cantidad, subtotal):
    query = text("""
        INSERT INTO venta_productos (id_venta, id_producto,precio_unitario, cantidad, subtotal)
        VALUES (:id_venta, :id_producto,:precio_unitario, :cantidad, :subtotal)
    """)

    db_session.execute(query, {"id_venta": id_venta, "id_producto": id_producto,
                       "precio_unitario": precio, "cantidad": cantidad, "subtotal": subtotal})
    db_session.commit()
    db_session.close() 


def insertar_detalle_venta(db_session: Session, id_venta, id_servicio, precio_unitario, cantidad, subtotal):
    query = text("""
        INSERT INTO detalle_venta (id_venta, id_servicio, precio_unitario,cantidad, subtotal)
        VALUES (:id_venta, :id_servicio, :precio_unitario,:cantidad, :subtotal)
    """)

    db_session.execute(query, {"id_venta": id_venta, "id_servicio": id_servicio,
                       "precio_unitario": precio_unitario, "cantidad": cantidad, "subtotal": subtotal})
    db_session.commit()
    db_session.close() 

def insertar_detalle_venta_cita(db_session, id_venta, id_reserva, precio_unitario, subtotal):
    try:
        # Definir la consulta SQL con text
        consulta = text("""
            INSERT INTO detalle_venta_cita (id_venta, id_reserva, precio_unitario, subtotal)
            VALUES (:id_venta, :id_reserva, :precio_unitario, :subtotal)
        """)

        # Ejecutar la consulta con los valores proporcionados
        db_session.execute(consulta, {
            'id_venta': id_venta,
            'id_reserva': id_reserva,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal
        })

        # Confirmar la transacción
        db_session.commit()
        db_session.close()
    except Exception as e:
        print(f"Error al insertar en la tabla detalle_venta_cita: {e}")


def cambiar_estado_reservacion(db_session: Session, id_reservacion: int, nuevo_estado: int):
    try:
        # Definir la consulta SQL con text
        consulta = text("""
            UPDATE reservacion
            SET estado = :nuevo_estado
            WHERE id = :id_reservacion
        """)

        # Ejecutar la consulta con los valores proporcionados
        db_session.execute(
            consulta, {'id_reservacion': id_reservacion, 'nuevo_estado': nuevo_estado})

        # Confirmar la transacción
        db_session.commit()

        # Cerrar la sesión (si se va a cerrar, depende del contexto de la aplicación)
        db_session.close()

    except Exception as e:
        print(f'Error al cambiar el estado de la reservación: {str(e)}')


def cambiar_estado_venta(db_session: Session, id_venta, nuevo_estado):
    query = text("""
        UPDATE venta
        SET estado = :nuevo_estado
        WHERE id = :id_venta
    """)

    db_session.execute(query, {"id_venta": id_venta,
                       "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close()


def obtener_info_lote_mas_antiguo(db_session: Session, id_producto):
    query = text("""
    SELECT id, cantidad
    FROM lote_producto
    WHERE id_producto = :id_producto AND cantidad > 0 AND (estado = 1 OR estado = 3)
    ORDER BY fecha_registro ASC
    LIMIT 1
""")

    result = db_session.execute(query, {"id_producto": id_producto}).fetchone()

    if result:
        id_lote, cantidad = result
        db_session.close()
        return {"id_lote": id_lote, "cantidad": int(cantidad)}
    else:
        return None


def restar_cantidad_lote(db_session: Session, id_lote, cantidad_restar):
    query = text("""
        UPDATE lote_producto
        SET cantidad = cantidad - :cantidad_restar
        WHERE id = :id_lote 
    """)

    db_session.execute(
        query, {"id_lote": id_lote, "cantidad_restar": cantidad_restar})
    db_session.commit()
    db_session.close()


def insertar_usuario(db_session: Session, id_persona,rol, usuario, contraseña, estado):
    query = text("""
        INSERT INTO usuario ( id_persona,rol, usuario, contraseña, estado)
        VALUES (:id_persona,:rol, :usuario, :contraseña, :estado)
    """)

    db_session.execute(query, {"id_persona": id_persona,"rol":rol,
                       "usuario": usuario, "contraseña": contraseña, "estado": estado})
    db_session.commit()
    db_session.close()

def cambiar_rol_usuario_por_id(db_session: Session, id_usuario, nuevo_rol):
    query = text("""
        UPDATE usuario
        SET rol = :nuevo_rol
        WHERE id = :id_usuario
    """)

    db_session.execute(query, {"id_usuario": id_usuario, "nuevo_rol": nuevo_rol})
    db_session.commit()
    db_session.close()

def actualizar_contraseña(db_session: Session, id_usuario, nueva_contraseña):
    query = text("""
        UPDATE usuario
        SET contraseña = :nueva_contraseña
        WHERE id = :id_usuario
    """)

    db_session.execute(
        query, {"nueva_contraseña": nueva_contraseña, "id_usuario": id_usuario})
    
    db_session.commit()
    db_session.close()

def cambiar_estado_usuario(db_session: Session, id_usuario, nuevo_estado):
    query = text("""
        UPDATE usuario
        SET estado = :nuevo_estado
        WHERE id = :id_usuario
    """)

    db_session.execute(
        query, {"id_usuario": id_usuario, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close()


def cambiar_estado_reservacion(db_session: Session, id_reservacion, nuevo_estado):
    query = text("""
        UPDATE reservacion
        SET estado = :nuevo_estado
        WHERE id = :id_reservacion
    """)

    db_session.execute(
        query, {"id_reservacion": id_reservacion, "nuevo_estado": nuevo_estado})
    db_session.commit()
    db_session.close()


def obtener_servicios_activos(db_session: Session):
    query = text('SELECT s.id, s.descripcion, s.nombre, s.realizacion, ps.precio FROM servicios s LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios WHERE s.estado = 1 and ps.estado = 1')
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
    db_session.close()
    return result


def obtener_productos(db_session):
    query = text("SELECT * FROM producto WHERE estado = 1 AND tipo IN(1,3)")
    productos = db_session.execute(query).fetchall()
    db_session.close()
    return productos
def obtener_todos_productos(db_session):
    query = text("SELECT * FROM producto ")
    productos = db_session.execute(query).fetchall()
    db_session.close()
    return productos


def obtener_precioproductos(db_session):
    query = text(
        "SELECT pp.*,p.id AS producto, p.nombre, p.logo FROM precio pp INNER JOIN producto p ON p.id = pp.id_producto")
    precios = db_session.execute(query).fetchall()
    db_session.close()
    return precios


def obtener_productos_ventas(db_session):
    query = text("""
        SELECT p.id AS producto_id, p.nombre AS producto_nombre, pp.precio, SUM(l.cantidad) AS cantidad_total
        FROM producto p
        INNER JOIN precio pp ON p.id = pp.id_producto
        INNER JOIN lote_producto l ON p.id = l.id_producto
        WHERE l.cantidad > 0 AND  (l.estado = 1 OR l.estado = 3) AND p.tipo IN(1,3)
        GROUP BY p.id, p.nombre, pp.precio
    """)

    productos = db_session.execute(query).fetchall()

    # Utilizamos un diccionario para almacenar la información de cada producto
    productos_agrupados = defaultdict(list)

    for producto in productos:
        productos_agrupados[producto.producto_id].append({
            'nombre': producto.producto_nombre,
            'precio': producto.precio,
            'cantidad_total': producto.cantidad_total
        })

    # Convertimos la estructura en una lista de tuplas para mantener la estructura original
    productos_resultado = [
        (producto_id, producto_info)
        for producto_id, producto_info in productos_agrupados.items()
    ]
    db_session.close()
    return productos_resultado
def obtener_productos_consumibless(db_session):
    query = text("""
        SELECT p.id AS producto_id, p.nombre AS producto_nombre, SUM(l.cantidad) AS cantidad_total
        FROM producto p
        INNER JOIN lote_producto l ON p.id = l.id_producto
        WHERE l.cantidad > 0 AND  (l.estado = 1 OR l.estado = 3)AND p.tipo IN(2,3)
        GROUP BY p.id, p.nombre
    """)

    productos = db_session.execute(query).fetchall()

    # Utilizamos un diccionario para almacenar la información de cada producto
    productos_agrupados = defaultdict(list)

    for producto in productos:
        productos_agrupados[producto.producto_id].append({
            'nombre': producto.producto_nombre,
            'cantidad_total': producto.cantidad_total
        })

    # Convertimos la estructura en una lista de tuplas para mantener la estructura original
    productos_resultado = [
        (producto_id, producto_info)
        for producto_id, producto_info in productos_agrupados.items()
    ]
    db_session.close()
    return productos_resultado


def obtener_tipo_venta(db_session):
    query = text("""SELECT * FROM tipo_venta WHERE estado = 1""")
    ventas = db_session.execute(query).fetchall()
    db_session.close()
    return ventas


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


def obtener_ventas(db_session):
    query = text("""
	SELECT
    v.id AS venta_id,
    v.codigo,
    v.fecha,
    v.descuento,
    v.total AS totales,
    v.estado AS venta_estado,
    tv.nombre AS tipo_venta_nombre,
    p.nombre AS persona_nombre,
   
    dv.id AS detalle_venta_id,
    s.nombre AS servicio_nombre,
    p2.nombre AS producto_nombre,
    dv.precio_unitario AS precio_unitario_detalle_venta,
    dv.cantidad AS cantidad_detalle_venta,
    dv.subtotal AS subtotal_detalle_venta,
    vp.id AS venta_producto_id,
    vp.precio_unitario AS precio_unitario_producto,
    vp.cantidad AS cantidad_venta_producto,
    vp.subtotal AS subtotal_venta_producto,
    vc.precio_unitario AS precios,
    vc.subtotal AS subtotalcita,
    s2.nombre AS citas
FROM
    venta v
JOIN tipo_venta tv ON v.id_tipo = tv.id
JOIN clientes c ON v.id_cliente = c.id
JOIN persona p ON c.id_persona = p.id
LEFT JOIN detalle_venta dv ON v.id = dv.id_venta
LEFT JOIN servicios s ON dv.id_servicio = s.id
LEFT JOIN venta_productos vp ON v.id = vp.id_venta
LEFT JOIN detalle_venta_cita vc ON v.id=vc.id_venta
LEFT JOIN reservacion r ON vc.id_reserva = r.id
LEFT JOIN servicios s2 ON r.idservicio = s2.id
LEFT JOIN producto p2 ON vp.id_producto = p2.id
ORDER BY
    v.id DESC
   
""")
    ventas = db_session.execute(query).fetchall()
    db_session.close() 
    return ventas


def obtener_reservacion(db_session: Session):
    query = text("""SELECT r.*, p.nombre AS cliente,s.nombre AS servicio, p.celular,tv.nombre AS metodo
FROM reservacion r
INNER JOIN clientes c ON c.id = r.idcliente
INNER JOIN servicios s ON s.id = r.idservicio
LEFT JOIN tipo_venta tv ON tv.id=r.id_metodo_pago
LEFT JOIN persona p ON c.id_persona = p.id
""")
    result = db_session.execute(query).fetchall()
    db_session.close() 
    return result


def obtener_reservacion_hoy(db_session: Session):
    # Obtener la fecha actual
    fecha_actual = datetime.now().date()

    query = text("""
        SELECT r.*, p.nombre AS cliente, s.nombre AS servicio, p.celular,id_metodo_pago
        FROM reservacion r
        INNER JOIN clientes c ON c.id = r.idcliente
        INNER JOIN servicios s ON s.id = r.idservicio
        LEFT JOIN persona p ON c.id_persona = p.id
        WHERE r.estado IN(1,5) AND r.fecha = :fecha_actual    ORDER BY r.hora_inicio
    """)

    result = db_session.execute(
        query, {"fecha_actual": fecha_actual}).fetchall()
    db_session.close() 
    return result
def obtener_reservacion_hoy_admin(db_session: Session):
    # Obtener la fecha actual
    fecha_actual = datetime.now().date()

    query = text("""
        SELECT r.*, p.nombre AS cliente, s.nombre AS servicio, p.celular
        FROM reservacion r
        INNER JOIN clientes c ON c.id = r.idcliente
        INNER JOIN servicios s ON s.id = r.idservicio
        LEFT JOIN persona p ON c.id_persona = p.id
        WHERE r.estado = 1 AND r.fecha = :fecha_actual    ORDER BY r.hora_inicio
    """)

    result = db_session.execute(
        query, {"fecha_actual": fecha_actual}).fetchall()
    db_session.close() 
    return result
def obtener_reservacion_hoy_admin_estado(db_session: Session):
    # Obtener la fecha actual
    fecha_actual = datetime.now().date()

    query = text("""
        SELECT r.*, p.nombre AS cliente, s.nombre AS servicio, p.celular
        FROM reservacion r
        INNER JOIN clientes c ON c.id = r.idcliente
        INNER JOIN servicios s ON s.id = r.idservicio
        LEFT JOIN persona p ON c.id_persona = p.id
        WHERE r.estado = 5    ORDER BY r.hora_inicio
    """)

    result = db_session.execute(
        query, {"fecha_actual": fecha_actual}).fetchall()
    db_session.close() 
    return result


def obtener_cantidad_reservaciones_hoy(db_session):
    try:
        # Definir la consulta SQL con text
        consulta = text("""
            SELECT COUNT(*) AS cantidad_reservaciones
            FROM reservacion
            WHERE fecha = CURRENT_DATE
                AND estado IN(1,5);
        """)

        # Ejecutar la consulta y obtener el resultado
        resultado = db_session.execute(consulta).fetchone()

        # Obtener la cantidad de reservaciones del resultado
        cantidad_reservaciones = resultado[0]  # Usar el índice numérico
        db_session.close() 
        return cantidad_reservaciones
    except Exception as e:
        # Manejar la excepción según tus necesidades
        print(f"Error al obtener la cantidad de reservaciones: {e}")
        return None


def actualizar_estados(db_session):
    # Obtén la fecha y hora actuales
    now = datetime.now()

    # Calcula la hora hace 20 minutos
    hace_20_minutos = now - timedelta(minutes=20)

    # Actualiza los estados directamente en la base de datos
    db_session.execute(text("""
        UPDATE reservacion
        SET estado = 3
        WHERE fecha = :fecha
          AND hora_inicio <= :hora_20_min_atras
          AND estado = 1
    """), {
        'fecha': now.date(),
        'hora_20_min_atras': hace_20_minutos.strftime("%H:%M:%S")
    })
    db_session.commit()
    db_session.close() 

def actualizar_estados_pasados(db_session):
    # Obtén la fecha y hora actuales
    now = datetime.now()

    # Actualiza los estados directamente en la base de datos
    db_session.execute(text("""
        UPDATE reservacion
        SET estado = 3
        WHERE fecha < :fecha_actual
          AND estado = 1
    """), {'fecha_actual': now.date()})
    db_session.commit()
    db_session.close() 


def ValidarNumeroCelularExistente(numero):
    query = text("SELECT id FROM persona WHERE celular = :numero")
    exists = db_session.execute(query, {"numero": numero}).scalar()
    db_session.close() 
    return exists


def obtener_serviciossistema(db_session: Session):
    query = text("SELECT *  FROM servicios ")
    result = db_session.execute(query).fetchall()
    db_session.close()
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
    db_session.close()
    return productos_sin_precio


def obtener_precios_servicios(db_session):
    query = text(
        "SELECT pp.*,p.id AS producto, p.nombre FROM precio_servicios pp INNER JOIN servicios p ON p.id = pp.id_servicios ")
    precios = db_session.execute(query).fetchall()
    db_session.close() 
    return precios


def ObtenerTrabajadores(db_session: Session):
    query = text("""
            SELECT 
                t.id AS trabajador_id, t.codigo, t.foto, t.estado,
                p.id AS persona_id, p.nombre, p.correo, p.direccion, p.celular,
                pn.id AS persona_natural_id, pn.apellido, pn.cedula, pn.fecha_nacimiento, pn.genero, pn.tipo_persona
            FROM trabajador t
            JOIN persona p ON t.id_persona = p.id
            JOIN persona_natural pn ON pn.id_persona = p.id
        """)
    result = db_session.execute(query).fetchall()
    db_session.close() 
    return result


def ObtenerEmpleadoSinUsuario(db_session: Session):
    consulta = text("""
           SELECT p.id AS persona_id, p.nombre, p.correo
            FROM persona p
            LEFT JOIN trabajador t ON p.id = t.id_persona
            LEFT JOIN usuario u ON p.id = u.id_persona
            WHERE t.id IS NOT NULL AND u.id IS NULL AND t.estado = 1
        """)
    result = db_session.execute(consulta).fetchall()
    db_session.close() 
    return result


def obtener_info_persona(id_persona):
    # Declarar la consulta SQL como texto
    consulta_sql = text(
        'SELECT p.nombre, pn.apellido,t.id AS id_trabajador, t.foto FROM persona p JOIN persona_natural pn ON p.id = pn.id_persona JOIN trabajador t ON p.id = t.id_persona WHERE p.id = :id_persona')

    # Ejecutar la consulta
    result = db_session.execute(consulta_sql, {'id_persona': id_persona})

    # Obtener los resultados
    datos = result.fetchone()
    db_session.close()
    return datos


def mostra_clientes(db_session: Session):
    query = text("""
         SELECT
            c.id,
            p.id AS id_persona,
            p.nombre,
            p.correo,
            p.direccion,
            p.celular,
            pn.id AS id_persona_natural,
            pn.apellido,
            pn.cedula,
            pn.fecha_nacimiento,
            pn.genero,
            pn.tipo_persona,
            c.id AS id_cliente,
            c.codigo,
            c.tipo_cliente,
            c.foto,
            c.estado
        FROM
            clientes c
		LEFT JOIN
            persona p ON c.id_persona = p.id
        LEFT JOIN
            persona_natural pn ON p.id = pn.id_persona
     
    """)
    result = db_session.execute(query).fetchall()
    db_session.close()
    return result


def obtenerusuarios(db_session: Session):
    query = text(""" SELECT s.*, p.nombre,pn.apellido FROM usuario s
INNER JOIN persona p ON p.id = s.id_persona
INNER JOIN persona_natural pn ON pn.id =s.id_persona """)
    result = db_session.execute(query).fetchall()
    db_session.close()
    return result


def horariosistema(db_session: Session):
    query = text(""" SELECT * FROM horarios ORDER BY id ASC """)
    result = db_session.execute(query).fetchall()
    db_session.close()
    return result


def actualizar_horario(db_session: Session, horario_id, hora_apertura, hora_cierre, estado):
    # Consulta SQL para actualizar el horario
    query = text("""
        UPDATE horarios
        SET  hora_apertura = :hora_apertura, hora_cierre = :hora_cierre, estado = :estado
        WHERE id = :horario_id
    """)

    # Ejecutamos la consulta con los parámetros proporcionados
    result = db_session.execute(query, {
        "horario_id": horario_id,

        "hora_apertura": hora_apertura,
        "hora_cierre": hora_cierre,
        "estado": estado
    })

    # Verificamos si se realizó la actualización correctamente
    if result.rowcount > 0:
        # Se actualizó al menos una fila, lo cual indica éxito
        db_session.commit()
        db_session.close()
        return True
    else:
        # No se encontró el horario con el ID proporcionado
        return False


def cambiar_estado_horario(db_session: Session, horario_id, nuevo_estado):
    # Consulta SQL para cambiar el estado del horario
    query = text("""
        UPDATE horarios
        SET estado = :nuevo_estado
        WHERE id = :horario_id
    """)

    # Ejecutamos la consulta con los parámetros proporcionados
    result = db_session.execute(query, {
        "horario_id": horario_id,
        "nuevo_estado": nuevo_estado
    })

    # Verificamos si se realizó la actualización correctamente
    if result.rowcount > 0:
        # Se actualizó al menos una fila, lo cual indica éxito
        db_session.commit()
        db_session.close()
        return True
    else:
        # No se encontró el horario con el ID proporcionado
        return False


def obtener_cupos_disponibles():
    dias_semana = ['Lunes', 'Martes', 'Miércoles',
                   'Jueves', 'Viernes', 'Sábado', 'Domingo']
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
        fecha_horario = fecha_hoy + \
            timedelta(days=(idx_dia_horario - fecha_hoy.weekday() + 7) % 7)

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
        cupos_disponibles = (
            hora_cierre.hour - hora_apertura.hour) // duracion_servicio - reservaciones

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
    db_session.close()
    return horarios_resultado


def obtener_cupos_hoy(horario, fecha_hoy):

    id_horario = horario[0]
    fecha_actual_str = fecha_hoy.strftime('%Y-%m-%d')

    query_reservas_hoy = text("""
        SELECT COUNT(*) FROM reservacion
        WHERE fecha = :fecha_actual
        AND idhorario = :id_horario
    """)

    cupos_hoy = db_session.execute(query_reservas_hoy, {
                                   "fecha_actual": fecha_actual_str, "id_horario": id_horario}).scalar()
    db_session.close()
    return cupos_hoy


def mostrar_fechas_y_horas_reservas():

    fecha_hoy = datetime.now().date()

    fecha_fin = fecha_hoy + timedelta(days=7)

    query_reservas = text("""
        SELECT fecha, hora
        FROM reservacion
        WHERE fecha BETWEEN :fecha_hoy AND :fecha_fin
    """)

    result = db_session.execute(
        query_reservas, {"fecha_hoy": fecha_hoy, "fecha_fin": fecha_fin}).fetchall()

    # Mostrar las fechas y horas de las reservas
    fechas_horas_reservas = [(reserva[0].strftime(
        "%Y-%m-%d"), reserva[1].strftime("%H:%M:%S")) for reserva in result]
    db_session.close() 
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

def generar_pdf(nombre, nombre_usuario, contraseña):
    # Configurar el tamaño del gráfico y el fondo
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#e6f7ff')  # Color de fondo

    # Desactivar ejes y bordes
    ax.axis('off')
    ax.set_frame_on(False)

    # Agregar texto al gráfico con estilo
    contenido_pdf = f'''
    Estimado(a) {nombre},

    Aquí tienes las credenciales para acceder a tu cuenta:

    +--------------------------------+
    | Usuario:    {nombre_usuario}   |
    | Contraseña: {contraseña}       |
    +--------------------------------+

    Por favor, asegúrate de cambiar tu contraseña una vez que hayas iniciado sesión en tu cuenta.

    Si tienes alguna pregunta o necesitas asistencia adicional, no dudes en contactarnos.

    ¡Gracias y ten un excelente día!
    '''

    ax.text(0.5, 0.5, contenido_pdf, ha='center', va='center', fontsize=12, color='#333333', fontweight='bold')

    # Crear un buffer para almacenar el PDF
    pdf_buffer = BytesIO()

    # Guardar el gráfico como PDF en el buffer
    with matplotlib.backends.backend_pdf.PdfPages(pdf_buffer, keep_empty=False) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    
    pdf_buffer.seek(0)
    plt.close(fig)

    return pdf_buffer.getvalue()


def enviar_correo_con_codigo(nombre, correo_destino, contraseña):
    cuerpo = f'''
    Estimado(a) {nombre},

Recientemente solicitaste recuperar tu contraseña para tu cuenta de Lavacar ASOCATIE.

Tu nueva contraseña es: {contraseña}

Por favor, inicia sesión en tu cuenta con esta contraseña y luego cámbiala a una que sea más fácil de recordar y segura.

Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.

¡Gracias y ten un excelente día!

Atentamente,
Lavacar ASOCATIE
    '''

    asunto = 'Recuperacion de contraseña - Acceso a cuenta'
    remitente = 'ingsoftwar123@gmail.com'
    destinatario = [correo_destino]

    msg = Message(asunto, sender=remitente, recipients=destinatario)
    msg.body = cuerpo
    mail.send(msg)


def enviar_reporte_por_venta(nombre, correo_destino):
    cuerpo = f'''
    Estimado(a) {nombre},
    A continuación se encuentra adjuntado el reporte correspondiente a la venta realizada el dia de hoy\n
    Atentamente,
    Lavacar ASOCATIE '''

    asunto = 'Reporte del dia - Reporte de venta'
    remitente = 'ingsoftwar123@gmail.com'
    destinatario = [correo_destino]

    msg = Message(asunto, sender=remitente, recipients=destinatario)
    msg.body = cuerpo

    # Adjuntar el archivo PDF
    # Cambia esto por la ruta correcta
    pdf_file_path = '/static/pdf/report/ventas.pdf'
    with app.open_resource(pdf_file_path) as pdf_file:
        msg.attach(pdf_file_path, 'application/pdf', pdf_file.read())

    # Enviar el correo
    mail.send(msg)


def BuscarPorIdPersona(db_session: Session, id):
    query = text("""
            SELECT p.nombre, pn.apellido,p.correo
            FROM persona p
            JOIN persona_natural pn ON p.id = pn.id_persona
            WHERE pn.id = :id
        """)

    resultado = db_session.execute(query, {"id": id}).fetchone()
    db_session.close()
    return resultado


def obtener_info_lotes_valor():
    query = text("""
       SELECT 
    p.id, 
    p.nombre,
    p.tipo, 
    lp.id AS lote, 
    lp.numero_lote, 
    lp.fecha_vencimiento,
    lp.cantidad, 
    COALESCE(lp.estado, 0) AS estado_lote,
    COALESCE(pr.precio, 0) AS precio,
    COALESCE(lp.cantidad * pr.precio, 0) AS valor_lote
FROM 
    producto p
INNER JOIN 
    lote_producto lp ON p.id = lp.id_producto
LEFT JOIN 
    precio pr ON p.id = pr.id_producto AND pr.estado = 1;

    """)

    results = db_session.execute(query).fetchall()

    lotes = []
    for result in results:
        id_producto, nombre_producto,tipo, lote, numero_lote, fecha_vencimiento, cantidad_lote, estado_lote, precio, valor_lote = result

        lote = {
            'id_producto': id_producto,
            'nombre_producto': nombre_producto,
            'tipo':tipo,
            'lote': lote,
            'numero_lote': numero_lote,
            'fecha_vencimiento': fecha_vencimiento,
            'cantidad_lote': cantidad_lote,
            'estado_lote': estado_lote,
            'precio': precio,

            'valor_lote': valor_lote
        }

        lotes.append(lote)
    db_session.close()     
    return lotes


def obtener_datos_sucursal():
    query = text(""" SELECT * FROM sucursal """)
    result = db_session.execute(query).first()
    db_session.close() 
    return result


@app.context_processor
def agregar_datos_sucursal():
    return dict(datos_sucursal=obtener_datos_sucursal())

@app.context_processor
def agregar_notificaciones():
    return dict(notificaciones=obtener_notificaciones(db_session))
@app.context_processor
def agregar_notificacion():
    return dict(numero=contar_notificaciones_estado_1(db_session))
@app.context_processor
def agregar_notificacion():
    return dict(numeros=contar_notificaciones_lista(db_session))
@app.context_processor
def agregar_notificaciones():
    return dict(lista=mostrar_lista(db_session))

def before_request():
 
    estadisticas_resultantes = actualizar_estado_lotes(db_session)
    print(f"Estadísticas de los lotes: {estadisticas_resultantes}")
    actualizar_estados(db_session)
    actualizar_estados_pasados(db_session)

  


@app.route("/recuperar", methods=['GET', 'POST'])
def recuperar_contraseña():
    return render_template("recuperar.html")


@app.route("/enviar_codigo", methods=['GET', 'POST'])
def recuperar_contraseñas():
    if request.method == "POST":
        usuario = request.form['correo']
        result = db_session.execute(
            text("SELECT id,id_persona FROM usuario WHERE usuario = :usuario"),
            {"usuario": usuario}
        )
        usuario_db = result.fetchone()
        if usuario_db:

            persona = BuscarPorIdPersona(db_session, usuario_db[1])
            nombre, apellido, correo = persona
            nombres = nombre + ' ' + apellido
            contraseña = generar_contraseña()
            enviar_correo_con_codigo(nombres, correo, contraseña)
            hashed_password = generate_password_hash(contraseña)
            actualizar_contraseña(db_session, usuario_db[0], hashed_password)
            flash("Se ha enviado tu nueva contraseña a tu correo electronico", "success")
            return redirect('/login')
        else:
            flash("No se ha encontrado el nombre del usuario", "error")

    return redirect('/recuperar')
@cross_origin()
@app.route('/api_InsertarCliente', methods=['POST'])
def api_InsertarCliente():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(data)
            nombre = data['nombre']
            apellidos = data['apellidos']
            correo = data['correo']
            celular = data['celular']
            tipo = data['tipo']

            id_persona = insertar_persona(db_session, nombre, correo,"En direccion", celular)
            print(id_persona)
            insertar_persona_natural(db_session, id_persona, apellidos, None, None, None, tipo)
            codigo = generar_codigo_cliente(nombre,id_persona,celular)
            print(codigo)
            codigo_cliente=insertar_cliente(db_session, id_persona,codigo,"Normal","No hay")
            print(codigo_cliente)

            db_session.commit()
            return codigo_cliente

        except Exception as e:
            print(f"Error: {str(e)}")
            db_session.rollback()
            return 'null', 400

        finally:
           db_session.close()

@cross_origin()
@app.route('/api/InsertarClienteObligatorio', methods=['GET', 'POST'])
def insertar_usuarios():
    request_data = request.get_json()

    if request.method == 'POST':

        request_data = request.get_json()
        nombre = request_data['nombre']
        print(nombre)
        celular = request_data['celular']
        id_persona = insertar_persona(db_session, nombre,"No hay","En direccion", celular)
        fecha_hoy = datetime.now()
        fecha_nacimiento_formato = fecha_hoy.strftime("%d/%m/%Y")
        insertar_persona_natural(db_session,id_persona,"Actualizar","cedula",fecha_nacimiento_formato,"O","Natural")
        codigo = generar_codigo_cliente(nombre,id_persona,celular)
        codigo_cliente=insertar_cliente(db_session, id_persona,codigo,"Cliente no registrado","No hay")

        db_session.commit()

        return jsonify({"codigo_cliente": codigo_cliente}), 200

    return 'null', 400


@app.route('/')
@login_required
def index():
    actualizar_estado_lotes(db_session)
    return render_template('index.html')


def obtener_horariosAtencion(db_session):
    try:
        query = text(
            "SELECT dia, hora_apertura, hora_cierre, estado FROM horarios")
        rows = db_session.execute(query).fetchall()
        # Devolver los resultados en formato JSON
        # Ejecutar consulta SQL

        # Procesar los resultados
        for dia, hora_apertura, hora_cierre, estado in rows:
            if estado == 1:
                # Convertir las horas a formato de 12 horas y determinar AM o PM
                apertura = datetime.strptime(hora_apertura.strftime(
                    '%H:%M:%S'), '%H:%M:%S').strftime('%I:%M %p')
                cierre = datetime.strptime(hora_cierre.strftime(
                    '%H:%M:%S'), '%H:%M:%S').strftime('%I:%M %p')
                print(f"{dia}: {apertura} a {cierre}")
            elif estado == 2:
                print(f"{dia}: *CERRADO*")

        return jsonify(rows)

    except Exception as error:
        # Manejar errores y devolver una respuesta apropiada
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al obtener los horarios'}), 500


@cross_origin()
@app.route('/api/obtenerHorariosSucursalesUbicaciones', methods=['GET'])
def obtenerHorariosSucursalesUbicaciones():

    sucursales
    horariosAtencion = obtener_horariosAtencion(db_session)

    return true


@cross_origin()
@app.route('/api/getservicios', methods=['GET'])
def obtener_servicios():
    try:
        result = obtener_servicios_activos(db_session)
        servicios = []
        for row in result:
            servicio = {
                "id": row.id,
                "descripcion": row.descripcion,
                "nombre": row.nombre,
                "precio": row.precio,
                "realizacion": row.realizacion.strftime('%H:%M:%S')
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
        app.logger.error(
            'Error en la función obtener_servicios_descripcion: %s', str(error))
        # Devolver una respuesta de error al cliente
        return jsonify({'error': 'Ocurrió un error al obtener los servicios con descripción'}), 500


@cross_origin()
@app.route('/api/validarnumerocelular', methods=['POST'])
def validar_numero_celular():
    try:
        numero_celular = request.json.get('numero_celular')
        existe = ValidarNumeroCelularExistente(numero_celular)
        return jsonify({'existe': existe}), 200

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


def obtener_nombre_dia_actual():
    # Obtener el nombre del día actual en inglés
    dia_actual = datetime.now().strftime("%A")
    nombre_dia_actual = dia_actual.capitalize()
    return nombre_dia_actual


def obtener_horario_actual():
    dia_actual = datetime.now().strftime("%A")  # Obtener el nombre del día actual
    nombre_dia_actual = dia_actual.capitalize()
    print(nombre_dia_actual)
    query = text(
        "SELECT hora_apertura, hora_cierre FROM horarios WHERE dia = :dia")
    result = db_session.execute(query, {"dia":  nombre_dia_actual})
    horario_actual = result.fetchone()
    return horario_actual


def generar_bloques_disponibles_para_semana():
    # Obtener el nombre del día actual en español con la primera letra en mayúscula
    dia_actual = obtener_nombre_dia_actual()

    # Obtener el horario del día actual desde la base de datos
    horario_actual = obtener_horario_actual()
    print(horario_actual)
    if horario_actual:
        hora_apertura = horario_actual[0]
        hora_cierre = horario_actual[1]

        # Convertir la hora de apertura y cierre a objetos datetime.time
        hora_aperturas = hora_apertura.strftime("%H:%M")
        hora_cierres = hora_cierre.strftime("%H:%M")
        print(hora_aperturas)
        print(hora_cierres)
        # Resto del código...
    else:
        print(
            f"No se encontró un horario para el día {dia_actual} en la base de datos.")


@app.route('/inicio', methods=['GET', 'POST'])
@login_required
def inicio():

    bloques_disponibles = generar_bloques_disponibles_para_semana()
# Imprimir los bloques disponibles generados
    if bloques_disponibles:
        for bloque in bloques_disponibles:
            print(
                f"Hora Inicio: {bloque['hora_inicio']}, Hora Fin: {bloque['hora_fin']}")
    else:
        print("No se encontró el horario para el día actual en la base de datos.")
    actualizar_estado_lotes(db_session)
    return render_template("index.html")


@app.route('/productos', methods=['GET', 'POST'])
@login_required
@role_required([1,2])
def productos():
    productos = obtener_todos_productos(db_session)
    print(productos)
    return render_template('productos.html', productos=productos)


@app.route('/CrearProducto', methods=['POST'])
def crear_producto():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    tipo=request.form.get('uso')
    estado = request.form.get('estado')
    archivo = request.files['logo']
    carpeta_destino = 'static/img/productos'
    logo = guardar_imagen(archivo, carpeta_destino)
    insertar_producto(db_session, nombre, descripcion, logo,tipo, estado)
    flash("Se ha registrado correctamente el producto", "success")
    generar_pdf_productos(db_session)
    return redirect('/productos')


@app.route('/ActualizarProducto', methods=['POST', 'GET'])
def actualizar_productos():
    print("Productos")
    id_producto = request.form.get('id')
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    tipo=request.form.get('uso')
    estado = request.form.get('estado')
    archivo = request.files['logo']
    logos = request.form.get('logos')
    print(id_producto)
    print(estado)

    try:
        if archivo:
            carpeta_destino = 'static/img/productos'
            logo = guardar_imagen(archivo, carpeta_destino)
            try:
                os.remove(logos)
            except FileNotFoundError:
                print(f"La imagen anterior no existe: {logos}")
            except Exception as e:
                print(f"No se pudo eliminar la imagen anterior: {e}")

            actualizar_producto(db_session, id_producto, nombre, descripcion, logo,tipo, estado)
        else:
            # Si no se proporcionó un archivo, solo actualizar la información sin cambiar la imagen
            actualizar_producto(db_session, id_producto, nombre, descripcion, logos,tipo, estado)

        # Mensaje de éxito y generación del PDF (se ejecuta en ambos casos)
        flash("Se ha actualizado correctamente el producto", "success")
        generar_pdf_productos(db_session)
        return redirect('/productos')

    except Exception as e:
        print(f"Error en la actualización del producto: {e}")
        flash("Ha ocurrido un error durante la actualización del producto", "error")
        return redirect('/productos')

@app.route('/CambiarEstadoProducto', methods=['POST'])
def cambiar_estado_producto():
    id_producto = request.form.get('id')
    nuevo_estado = request.form.get('estado')
    cambiar_estado_productos(db_session, id_producto, nuevo_estado)
    generar_pdf_productos(db_session)
    flash("Se ha desactivado el producto", "success")
    return redirect('/productos')


@app.route('/precioproducto', methods=['GET', 'POST'])
@role_required([1,2])
@login_required
def precioproducto():
    Precios = obtener_precioproductos(db_session)
    productos = obtener_productos_sin_precio(db_session)
    return render_template("precioproducto.html", productos=productos, Precios=Precios)


@app.route('/CrearPrecio', methods=['GET', 'POST'])
def crearprecioproducto():
    idproducto = request.form.get('idproducto')
    precio = request.form.get('precio')
    estado = request.form.get('estado')
    insertar_precio(db_session, idproducto, precio, estado)
    flash("Se ha registrado correctamente el precio", "success")
    return redirect('/precioproducto')


@app.route('/CambiarPrecio/<int:id>', methods=['GET', 'POST'])
def cambiaprecioproducto(id):
    idproducto = request.form.get('idproducto')
    precio = request.form.get('precio')
    estado = request.form.get('estado')
    insertar_precio(db_session, idproducto, precio, estado)
    cambiar_estado_precio(db_session, id, 2)
    flash("Se ha registrado correctamente el precio", "success")
    return redirect('/precioproducto')


@app.route('/CambiarPrecioestado/<int:id>', methods=['GET', 'POST'])
def cambiaprecioproductoestado(id):

    cambiar_estado_precio(db_session, id, 2)
    flash("Se ha desactivado  correctamente el precio", "success")
    return redirect('/precioproducto')


@app.route('/servicios')
@login_required
@role_required([1,2])
def servicios():
    servicios = obtener_serviciossistema(db_session)
    return render_template("servicios.html", servicios=servicios)


@app.route("/crearservicio", methods=["POST"])
def crearservicios():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    estado = request.form.get('estado')
    realizacion = request.form.get('realizacion')
    archivo = request.files['foto']
    carpeta_destino = 'static/img/servicios'
    logo = guardar_imagen(archivo, carpeta_destino)
    insertar_servicio(db_session, nombre, descripcion,
                      logo, realizacion, estado)
    generar_pdf_servicios(db_session)
    flash("Se ha registrado correctamente el servicios", "success")
    return redirect('/servicios')


@app.route('/actualizar_servicios/<int:servicio_id>', methods=['POST', 'GET'])
def actualizar_servicio(servicio_id):
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    estado = request.form.get('estado')
    realizacion = request.form.get('realizacion')
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

        update_servicio(db_session, servicio_id, nombre,
                        descripcion, logo, realizacion, estado)
        flash("Se ha actualizado correctamente el servicio, recuerda de actualizar el PDF para los usuarios del BOT!", "success")
        return redirect(url_for('servicios'))

    update_servicio(db_session, servicio_id, nombre,
                    descripcion, logos, realizacion, estado)
    flash("Se ha actualizado correctamente el servicio, recuerda de actualizar el PDF para los usuarios del BOT!", "success")
    generar_pdf_servicios(db_session)
    return redirect(url_for('servicios'))


@app.route('/eliminar_servicio/<int:servicio_id>', methods=['POST', 'GET'])
def eliminar_servicio(servicio_id):
    cambiar_estado_servicio(db_session, servicio_id, 2)
    flash("se ha desactivado el servicio", "success")
    generar_pdf_servicios(db_session)
    return redirect("/servicios")


@app.route("/precio_servicios", methods=['GET', 'POST'])
@login_required
@role_required([1,2])
def preciosservicios():
    servicios = obtener_servicios_sin_precio(db_session)
    Preciosservicios = obtener_precios_servicios(db_session)
    return render_template("preciosservicios.html", servicios=servicios, Preciosservicios=Preciosservicios)


@app.route('/CrearServiciosPrecios', methods=['GET', 'POST'])
def crearprecioservicios():
    idproducto = request.form.get('idproducto')
    precio = request.form.get('precio')
    estado = request.form.get('estado')
    insertar_precio_servicio(db_session, idproducto, precio, estado)
    flash("Se ha registrado correctamente el precio", "success")
    return redirect('/precio_servicios')


@app.route('/CambiarServicios/<int:id>', methods=['GET', 'POST'])
def cambiaprecioservicios(id):
    idproducto = request.form.get('idproducto')
    precio = request.form.get('precio')
    estado = request.form.get('estado')

    insertar_precio_servicio(db_session, idproducto, precio, estado)

    cambiar_estado_precio_servicio(db_session, id, 2)
    flash("Se ha registrado correctamente el precio", "success")
    return redirect('/precio_servicios')


@app.route('/CambiarServiciosestado/<int:id>', methods=['GET', 'POST'])
def cambiaprecioproductoestadoservcios(id):

    cambiar_estado_precio_servicio(db_session, id, 2)
    flash("Se ha desactivado  correctamente el precio", "success")
    return redirect('/precio_servicios')


@app.route('/trabajador', methods=['GET', 'POST'])
@login_required
@role_required([1])
def trabajador():
    trabajadores = ObtenerTrabajadores(db_session)
    return render_template("trabajador.html", trabajadores=trabajadores)


@app.route('/crear_trabajador', methods=['POST'])
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
    codigo = generar_codigo_trabajador(db_session)
    archivo = request.files['foto']
    carpeta_destino = 'static/img/trabajadores'
    logo = guardar_imagen(archivo, carpeta_destino)
    IdPersona = insertar_persona(
        db_session, nombre, correo, direccion, celular)
    insertar_persona_natural(
        db_session, IdPersona, apellido, cedula, fecha, genero, "Persona Natural")
    insertar_trabajador(db_session, IdPersona, codigo, logo, estado)
    flash("Se ha registrado con exito", "success")
    return redirect('/trabajador')


@app.route('/actualizar_trabajador/<int:id>', methods=['POST'])
def actualizar_trabajadors(id):
    persona = request.form.get('persona')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    direccion = request.form.get('direccion')
    celular = request.form.get('celular')
    estado = request.form.get('estado')
    archivo = request.files['foto']
    logos = request.form.get('logos')
    if archivo:
        carpeta_destino = 'static/img/trabajadores'
        logo = guardar_imagen(archivo, carpeta_destino)
        try:
            os.remove(logos)
        except Exception as e:
            print(f"No se pudo eliminar la imagen anterior: {e}")

        update_persona(db_session, persona, nombre, correo, celular, direccion)
        update_persona_natural(db_session, persona,
                               apellido, "Persona Natural")

        actualizar_trabajador(db_session, id, logo, estado)
        flash("Se ha actualizado con exito ", "success")
        return redirect('/trabajador')
    else:
        update_persona(db_session, persona, nombre, correo, celular, direccion)
        update_persona_natural(db_session, persona,
                               apellido, "Persona Natural")
        actualizar_trabajador(db_session, id, logos, estado)
        flash("Se ha actualizado con exito ", "success")
        return redirect('/trabajador')


@app.route('/eliminar_trabajador/<int:id>', methods=['POST'])
def eliminar_trabajadors(id):
    cambiar_estado_trabajador(db_session, id, 2)
    flash("Se ha desactivado correctamente el trabajador", "success")
    return redirect('/trabajador')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('403.html'), 403

@app.route("/usuarios", methods=['GET', 'POST'])
@login_required
@role_required([1])
def usuarios():
    trabajador = ObtenerEmpleadoSinUsuario(db_session)
    usuarios = obtenerusuarios(db_session)
    return render_template("usuarios.html", trabajador=trabajador, usuarios=usuarios)


@app.route("/crearusuarios", methods=['GET', 'POST'])
def crear_usuario():
    id = request.form.get('idpersona')
    rol = request.form.get('rol')
    contraseña = generar_contraseña()
    hashed_password = generate_password_hash(contraseña)
    persona = BuscarPorIdPersona(db_session, id)

    if persona:
        nombre, apellido, correo = persona
        nombres = nombre + ' ' + apellido
        usuario = generar_nombre_usuario(nombre, apellido, id)
        pdf_content = generar_pdf(nombres, usuario, contraseña)
        insertar_usuario(db_session, id, rol, usuario, hashed_password, 0)

        flash("Se ha agregado correctamente el usuario!", "success")

        # Devolver el PDF como respuesta HTTP
        pdf_file = BytesIO(pdf_content)
        pdf_file.seek(0)  # Asegurar que el cursor esté al principio del archivo

        return send_file(
            pdf_file,
            download_name="credenciales.pdf",
            as_attachment=True,
            mimetype="application/pdf"
        )

    else:
        flash("No se encontró la persona", "error")
        return redirect('/usuarios')


@app.route("/verificar_usuarios", methods=['GET', 'POST'])
def verificar_usuarios():
    id = request.form.get('id')
    cambiar_estado_usuario(db_session, id, 1)
    flash("Se ha activado correctamente!", "success")
    return redirect('/usuarios')


@app.route("/eliminar_usuario", methods=['GET', 'POST'])
def eliminar_usuarios():
    id = request.form.get('id')
    cambiar_estado_usuario(db_session, id, 2)
    flash("Se ha desactivado correctamente!", "success")
    return redirect('/usuarios')


@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route("/validar", methods=['GET', 'POST'])
def validar():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        # Consulta SQL para buscar al usuario en la base de datos
        result = db_session.execute(
            text("SELECT * FROM usuario WHERE usuario = :usuario"),
            {"usuario": usuario}
        )
        db_session.close() 
        usuario_db = result.fetchone()

        if usuario_db and check_password_hash(usuario_db[4], contraseña):
            # Contraseña válida, iniciar sesión

            session['usuario_id'] = usuario_db[0]
            datos = obtener_info_persona(usuario_db[1])
            nombre, apellido,idtrabajador, foto = datos
            session['rol']=usuario_db[2]
            session['nombre'] = nombre
            session['apellido'] = apellido
            session['id_trabajador']=idtrabajador
            session['foto'] = foto
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Credenciales incorrectas. Por favor, inténtalo de nuevo.', 'error')
    return redirect('/login')


@app.route('/cambiar_contraseña', methods=['GET', 'POST'])
def cambiar_contraseña():
    id = request.form.get('id')
    contraseña = request.form.get('contraseña_actual')
    contraseña_nueva = request.form.get('contraseña_nueva')
    result = db_session.execute(
        text("SELECT * FROM usuario WHERE id = :id"),
        {"id": id}
    )
    db_session.close() 
    
    usuario_db = result.fetchone()

    if usuario_db and check_password_hash(usuario_db[3], contraseña):
        hashed_password = generate_password_hash(contraseña_nueva)

        actualizar_contraseña(db_session, id, hashed_password)
        flash('Inicio de sesión exitoso', 'success')
        return redirect(url_for('inicio'))
    else:
        flash('Credenciales incorrectas. Por favor, inténtalo de nuevo.', 'error')

    return redirect('/inicio')


@app.route('/logout')
@login_required
def logout():
    # Cerrar sesión
    session.pop('usuario_id', None)
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('inicio'))


@app.route("/horario", methods=['GET', 'POST'])
@login_required
@role_required([1,2])
def horario():
    horario = horariosistema(db_session)
    return render_template("horario.html", horario=horario)


@app.route('/CambiarHorario/<int:horario_id>', methods=['POST'])
def cambiar_horario(horario_id):
    if request.method == 'POST':
        # Obtener datos del formulario
        hora_apertura = request.form['horaapertura']
        hora_cierre = request.form['horacierre']
        estado = request.form['estado']
        actualizar_horario(db_session, horario_id,
                           hora_apertura, hora_cierre, estado)
        flash('Se ha actualizado el horario', 'info')
        return redirect(url_for('horario'))

    else:
        return "Método no permitido", 405


@app.route('/Cambiarhorarioestado/<int:horario_id>', methods=['POST'])
def cambiar_horarios(horario_id):
    if request.method == 'POST':

        cambiar_estado_horario(db_session, horario_id, 2)
        flash('Se ha actualizado el horario', 'info')
        return redirect(url_for('horario'))

    else:
        return "Método no permitido", 405


@app.route("/lotes", methods=['GET', 'POST'])
@login_required
@role_required([1,2,3])
def lotes():
    productos = obtener_productos(db_session)
    lotes = obtener_info_lotes_valor()

    return render_template("lote.html", productos=productos, lotes=lotes)

def insertar_solicitud_producto(db_session, id_trabajador, fecha_solicitud, motivo):
    query = text("""
    INSERT INTO solicitud_producto (id_trabajador, fecha_solicitud, motivo, estado)
    VALUES (:id_trabajador, :fecha_solicitud, :motivo, 1)
    RETURNING id;
    """)
    result = db_session.execute(query, {'id_trabajador': id_trabajador, 'fecha_solicitud': fecha_solicitud, 'motivo': motivo})
    id_solicitud = result.fetchone()[0]
    db_session.commit()
    db_session.close() 
    return id_solicitud

def actualizar_solicitud_producto(db_session, id_solicitud, id_trabajador, fecha_solicitud, motivo):
    query = text("""
    UPDATE solicitud_producto
    SET id_trabajador = :id_trabajador, fecha_solicitud = :fecha_solicitud, motivo = :motivo
    WHERE id = :id_solicitud;
    """)
    db_session.execute(query, {'id_trabajador': id_trabajador, 'fecha_solicitud': fecha_solicitud, 'motivo': motivo, 'id_solicitud': id_solicitud})
    db_session.commit()
    db_session.close() 

def cambiar_estado_solicitud(db_session, id_solicitud, nuevo_estado):
    query = text("""
    UPDATE solicitud_producto
    SET estado = :nuevo_estado
    WHERE id = :id_solicitud;
    """)
    db_session.execute(query, {'nuevo_estado': nuevo_estado, 'id_solicitud': id_solicitud})
    db_session.commit()
    db_session.close() 
def obtener_productos_consumibles(db_session):
    query = text("""
    SELECT id, nombre, descripcion, logo, tipo, estado
    FROM producto
    WHERE tipo IN (2, 3);
    """)
    result = db_session.execute(query)
    productos_consumibles = result.fetchall()
    db_session.close() 
    return productos_consumibles
def obtener_solicitudes_con_trabajador(db_session):
    query = text("""
        SELECT sp.id AS solicitud_id, 
               t.codigo AS trabajador_codigo,
               p.nombre AS trabajador_nombre,
               sp.fecha_solicitud,
               sp.motivo,
               sp.estado
        FROM solicitud_producto sp
        JOIN trabajador t ON sp.id_trabajador = t.id
        JOIN persona p ON t.id_persona = p.id;
    """)
    result = db_session.execute(query)
    solicitudes_con_trabajador = result.fetchall()
    db_session.close() 
    return solicitudes_con_trabajador
def obtener_solicitudes_(db_session):
    query = text("""
        SELECT sp.id AS solicitud_id, 
               t.codigo AS trabajador_codigo,
               p.nombre AS trabajador_nombre,
               sp.fecha_solicitud,
               sp.motivo,
               sp.estado
        FROM solicitud_producto sp
        JOIN trabajador t ON sp.id_trabajador = t.id
        JOIN persona p ON t.id_persona = p.id WHERE sp.estado = 1;
    """)
    result = db_session.execute(query)
    solicitudes_con_trabajador = result.fetchall()
    db_session.close() 
    return solicitudes_con_trabajador
def insertar_detalle_solicitud(db_session, id_solicitud, id_producto, cantidad):
    query = text("""
        INSERT INTO detalle_solicitud (id_solicitud, id_producto, cantidad)
        VALUES (:id_solicitud, :id_producto, :cantidad)
        RETURNING id;
    """)
    result = db_session.execute(query, {'id_solicitud': id_solicitud, 'id_producto': id_producto, 'cantidad': cantidad})
    id_detalle_solicitud = result.fetchone()[0]
    db_session.commit()
    db_session.close() 
    return id_detalle_solicitud
@app.route("/solicitudes",methods=['GET','POST'])
@login_required
@role_required([1,2,3])
def solicitudes():
    productos=obtener_productos_consumibles(db_session)
    solicitudes=obtener_solicitudes_con_trabajador(db_session)
    solicitud= obtener_solicitudes_(db_session)
    return render_template("solicitudes.html",productos=productos,solicitudes=solicitudes,solicitud=solicitud)

def obtener_detalles_solicitud(db_session, id_solicitud):
    query = text("""
    SELECT d.id, p.nombre AS nombre_producto, d.cantidad
    FROM detalle_solicitud d
    JOIN producto p ON d.id_producto = p.id
    WHERE d.id_solicitud = :id_solicitud;
    """)
    result = db_session.execute(query, {'id_solicitud': id_solicitud})
    
    db_session.close() 
    # Convertir manualmente los resultados a una lista de diccionarios
    detalles = []
    for row in result:
        detalles.append({'id': row.id, 'nombre_producto': row.nombre_producto, 'cantidad': row.cantidad})

    return detalles

@app.route('/detalles_solicitud/<int:id_solicitud>')
def detalles_solicitud(id_solicitud):
    detalles = obtener_detalles_solicitud(db_session, id_solicitud)
    print(detalles)
    
    return jsonify(detalles)
@app.route("/crearsolicitudes", methods=['POST'])
def crearsolicitudes():
    if request.method == "POST":
        data = request.json
        id_trabajador = data.get('trabajador')
        motivo = data.get('motivo')
        productos = data.get('productos', [])

        # Obtener la fecha y hora actual
        fecha_actual = datetime.now()

        # Formatear la fecha como una cadena con el formato para PostgreSQL
        fecha = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')

        # Insertar la solicitud de producto
        idsolicitud = insertar_solicitud_producto(db_session, id_trabajador, fecha, motivo)

        # Insertar detalles de solicitud para cada producto
        detalles_insertados = []
        for producto in productos:
            solicitud = insertar_detalle_solicitud(db_session, idsolicitud, producto.get('id'), producto.get('cantidad'))
            detalles_insertados.append(solicitud)

        # Devolver una respuesta JSON con estado 200
        response_data = {
            'message': 'Se ha creado correctamente la solicitud'
        }

        return jsonify(response_data), 200
    
@app.route('/cambiar_estado_solicitud', methods=['POST'])
def cambiar_estado_endpoint():
    try:
        # Obtener datos del formulario
        id_solicitud = request.form.get('solicitud_id')
        nuevo_estado = request.form.get('estado')

        # Convertir el ID a entero
        id_solicitud = int(id_solicitud)

        # Llamar a la función para cambiar el estado
        cambiar_estado_solicitud(db_session, id_solicitud, nuevo_estado)

        # Devolver respuesta exitosa
        flash("Se ha realizado la operación correctamente","success")
        return redirect('/solicitudes')

    except Exception as e:
        # Devolver respuesta de error en caso de fallo
        return jsonify({'error': str(e)}), 500

@app.route("/sucursales", methods=['GET', 'POST'])
@login_required
@role_required([1])
def sucursales():

    surcursales = obtener_sucursales(db_session)

    if request.method == 'POST':
        nombre_sucursal = request.form['nombre_sucursal']
        razon_social = request.form['razon_social']
        direccion_escrita = request.form['direccion_escrita']
        ubicacion_googleMaps = request.form['enlace_googleMaps']
        telefono = request.form['telefono']
        estado = 1
        archivo = request.files['foto']
        carpeta_destino = 'static/img/logos'
        logo = guardar_imagen(archivo, carpeta_destino)

        insertar_sucursal(db_session, nombre_sucursal, razon_social,
                          direccion_escrita, ubicacion_googleMaps, telefono, logo, estado)

        flash('Se ha creado la sucursal', 'success')
        return redirect(url_for('sucursales'))

    return render_template("sucursales.html", surcursales=surcursales)


def insertar_sucursal(db_session, nombre_sucursal, razon_social, direccion_escrita, ubicacion_googleMaps, telefono, logo, estado):
    query = text("""
    INSERT INTO sucursal (nombre, razon_social, ubicacion_escrita, ubicacion_googleMaps, telefono,logo, estado)
    VALUES (:nombre_sucursal, :razon_social, :direccion_escrita, :ubicacion_googleMaps, :telefono,:logo, :estado)
    RETURNING id
""")

    db_session.execute(query, {
        'nombre_sucursal': nombre_sucursal,
        'razon_social': razon_social,
        'direccion_escrita': direccion_escrita,
        'ubicacion_googleMaps': ubicacion_googleMaps,
        'telefono': telefono,
        'logo': logo,
        'estado': estado
    })

    db_session.commit()
    db_session.close() 
    return true


def obtener_sucursales(db_session):
    query = text("""
        SELECT id, nombre, razon_social, ubicacion_escrita, ubicacion_googleMaps, telefono, logo, estado
        FROM sucursal
    """)

    sucursales = db_session.execute(query).fetchall()
    db_session.close() 
    return sucursales


@app.route('/eliminar_sucursal/<int:id>', methods=['POST'])
def eliminar_sucursal(id):
    if request.method == 'POST':
        eliminar_sucursal(id)
        flash('Se ha eliminado la sucursal', 'success')
        return redirect(url_for('sucursales'))


@app.route('/editar_sucursal/<int:id>', methods=['POST'])
def editar_sucursal(id):
    if request.method == 'POST':
        print(id)

        id_sucursal = id
        nombre_sucursal = request.form['nombre_sucursal']
        razon_social = request.form['razon_social']
        direccion_escrita = request.form['direccion_escrita']
        ubicacion_googleMaps = request.form['enlace_googleMaps']
        telefono = request.form['telefono']
        estado = 1
        archivo = request.files['foto']
        logos = request.form['logos']

        if archivo:
            carpeta_destino = 'static/img/trabajadores'
            logo = guardar_imagen(archivo, carpeta_destino)
            actualizar_sucursal(db_session, id_sucursal, nombre_sucursal, razon_social,
                                direccion_escrita, ubicacion_googleMaps, telefono, logo, estado)

            try:
                os.remove(logos)
            except Exception as e:
                print(f"No se pudo eliminar la imagen anterior: {e}")
        else:
            actualizar_sucursal(db_session, id_sucursal, nombre_sucursal, razon_social,
                                direccion_escrita, ubicacion_googleMaps, telefono, logos, estado)

    flash('Se ha actualizado la sucursal', 'success')
    return redirect(url_for('sucursales'))


def actualizar_sucursal(db_session, id_sucursal, nombre_sucursal, razon_social, direccion_escrita, ubicacion_googleMaps, telefono, logo, estado):
    query = text("""
    UPDATE sucursal 
    SET nombre = :nombre_sucursal, 
        razon_social = :razon_social, 
        ubicacion_escrita = :direccion_escrita, 
        ubicacion_googleMaps = :ubicacion_googleMaps, 
        telefono = :telefono, 
        logo=:logo,
        estado = :estado
    WHERE id = :id_sucursal
""")

    db_session.execute(query, {
        'id_sucursal': id_sucursal,
        'nombre_sucursal': nombre_sucursal,
        'razon_social': razon_social,
        'direccion_escrita': direccion_escrita,
        'ubicacion_googleMaps': ubicacion_googleMaps,
        'telefono': telefono,
        'logo': logo,
        'estado': estado
    })

    db_session.commit()
    db_session.close()

    return true


def eliminar_sucursal(id):
    query = text("""
    DELETE FROM sucursal 
    WHERE id = :id_sucursal
""")

    db_session.execute(query, {
        'id_sucursal': id
    })

    db_session.commit()
    db_session.close()

    return true


@cross_origin()
@app.route('/api/obtener_sucursales_horarios', methods=['GET'])
def horarios():

    sucursales_horarios = obtener_sucursales_horarios(db_session)

    return jsonify(sucursales_horarios)


def obtener_sucursales_horarios(db_session):
    # Ejecuta la consulta SQL
    query = text("""
        
SELECT 
    s.id AS id_sucursal,
    s.nombre AS nombre_sucursal,
    s.razon_social,
    s.ubicacion_escrita,
    s.ubicacion_googleMaps,
    s.telefono,
    s.estado AS estado_sucursal,
    s.logo,
    h.id AS id_horario,
    h.dia,
    TO_CHAR(h.hora_apertura, 'HH:MI AM') AS hora_apertura_12h,
    TO_CHAR(h.hora_cierre, 'HH:MI AM') AS hora_cierre_12h,
    h.estado AS estado_horario
FROM 
    sucursal s
JOIN 
    horarios h ON s.id = h.id_sucursal
WHERE
    h.estado = '1'
ORDER BY 
    id_horario;

    """)

    # Obtiene los resultados
    rows = db_session.execute(query).fetchall()

    # Estructura de datos para almacenar las sucursales
    sucursales = []
    for row in rows:
        sucursal = next((s for s in sucursales if s['id'] == row[0]), None)
        if sucursal is None:
            sucursal = {
                'id': row[0],
                'nombre': row[1],
                'ubicacion_escrita': row[3],
                'ubicacion_googlemaps': row[4],
                'telefono': row[5],
                'estado': row[6],
                'horarios': []
            }
            sucursales.append(sucursal)

        horario = {
            'dia': row[9],
            'hora_apertura': row[10],
            'hora_cierre': row[11]
        }
        sucursal['horarios'].append(horario)
    db_session.close()    

    return sucursales


@app.route('/insertar_lote', methods=['POST'])
def insertar_lote():
    if request.method == 'POST':
        id_producto = request.form.get('idproducto')
        fecha_vencimiento_str = request.form.get('fecha_vencimiento')
        cantidad = request.form.get('cantidad')
        estado = int(request.form.get('estado'))
        query_max_id = text("""
    SELECT COALESCE(MAX(id), 0) FROM lote_producto;
""")
       

        # Ejecutar la consulta
      

        # Obtener el resultado
        resultado = db_session.execute(query_max_id).fetchone()

        # Obtener el valor máximo y establecer 1 si no hay registros
        maximo_id = max(resultado[0], 1)
        # Generar número de lote
        numero_lote = generar_numero_lote(maximo_id)
    
        # Convertir la cadena de fecha de vencimiento a objeto datetime
        fecha_vencimiento = None
        if fecha_vencimiento_str:
            fecha_vencimiento = datetime.strptime(
                fecha_vencimiento_str, '%Y-%m-%d')

        # Crear la consulta SQL base sin especificar fecha_vencimiento
        query_base = """
            INSERT INTO lote_producto (id_producto, numero_lote, fecha_vencimiento, fecha_registro, cantidad, estado)
            VALUES (:id_producto, :numero_lote, {}, :fecha_registro, :cantidad, :estado)
            RETURNING id
        """

        # Definir la consulta final dependiendo de la presencia de fecha_vencimiento
        if fecha_vencimiento is not None:
            query = text(query_base.format(":fecha_vencimiento"))
        else:
            query = text(query_base.format("NULL"))

        # Ejecutar la consulta y obtener el ID del nuevo lote
        lote_id = db_session.execute(query, {
            'id_producto': id_producto,
            'numero_lote': numero_lote,
            'fecha_vencimiento': fecha_vencimiento,
            'fecha_registro': datetime.now(),
            'cantidad': cantidad,
            'estado': estado  # Coloca :estado en el diccionario de parámetros
        }).scalar()

        # Insertar el movimiento en el inventario
        insertar_movimiento_inventario(
            db_session, lote_id, "Lote nuevo", cantidad)
        db_session.close()

        flash('Se ha creado el lote', 'success')
        return redirect(url_for('lotes'))


@app.route('/editar_lote/<int:lote_id>', methods=['POST'])
def editar_lote(lote_id):
    if request.method == 'POST':
        fecha_vencimiento_str = request.form['fecha_vencimiento']
        nueva_cantidad = int(request.form['cantidad'])  # Convertir a entero

        # Convertir la cadena de fecha de vencimiento a objeto datetime
        fecha_vencimiento = None
        if fecha_vencimiento_str:
            fecha_vencimiento = datetime.strptime(
                fecha_vencimiento_str, '%Y-%m-%d')

        query_cantidad_actual = text(
            "SELECT cantidad FROM lote_producto WHERE id = :lote_id")
        cantidad_actual = db_session.execute(
            query_cantidad_actual, {'lote_id': lote_id}).scalar()

        if nueva_cantidad != cantidad_actual:
            # Realiza la actualización en la base de datos
            query_actualizacion = text("""
                UPDATE lote_producto
                SET 
                    fecha_vencimiento = :fecha_vencimiento,
                    cantidad = :cantidad
                WHERE id = :lote_id
            """)
            db_session.execute(query_actualizacion, {
                'fecha_vencimiento': fecha_vencimiento,
                'cantidad': nueva_cantidad,
                'lote_id': lote_id
            })

            db_session.commit()
            # Determinar el tipo de movimiento
            tipo_movimiento = "Se incrementó la cantidad" if nueva_cantidad > cantidad_actual else "Se redujo la cantidad"
            db_session.close()
            # Calcular la cantidad de cambio en el inventario
            cantidad_cambio = abs(nueva_cantidad - cantidad_actual)

            # Registrar el movimiento en el inventario
            insertar_movimiento_inventario(
                db_session, lote_id, tipo_movimiento, cantidad_cambio)
        else:
            # Realiza la actualización en la base de datos
            query_actualizacion = text("""
                UPDATE lote_producto
                SET 
                    fecha_vencimiento = :fecha_vencimiento
                   
                WHERE id = :lote_id
            """)
            db_session.execute(query_actualizacion, {
                'fecha_vencimiento': fecha_vencimiento,
                'lote_id': lote_id
            })

            db_session.commit()
            db_session.close() 

        flash('Se ha actualizado el lote', 'success')
    return redirect(url_for('lotes'))
@app.route('/editar_lotes/<int:lote_id>', methods=['POST'])
def editar_lotees(lote_id):
    if request.method == 'POST':
        nueva_cantidad = int(request.form['cantidad'])  # Convertir a entero

        # Convertir la cadena de fecha de vencimiento a objeto datetime
        query_cantidad_actual = text(
            "SELECT cantidad FROM lote_producto WHERE id = :lote_id")
        cantidad_actual = db_session.execute(
            query_cantidad_actual, {'lote_id': lote_id}).scalar()

        if nueva_cantidad != cantidad_actual:
            # Realiza la actualización en la base de datos
            query_actualizacion = text("""
                UPDATE lote_producto
                SET 
                   
                    cantidad = :cantidad
                WHERE id = :lote_id
            """)
            db_session.execute(query_actualizacion, {
               
                'cantidad': nueva_cantidad,
                'lote_id': lote_id
            })

            db_session.commit()
            # Determinar el tipo de movimiento
            tipo_movimiento = "Para uso interno" if nueva_cantidad > cantidad_actual else "Uso interno"

            # Calcular la cantidad de cambio en el inventario
            cantidad_cambio = abs(nueva_cantidad - cantidad_actual)

            # Registrar el movimiento en el inventario
            insertar_movimiento_inventario(
                db_session, lote_id, tipo_movimiento, cantidad_cambio)
       
            db_session.commit()

        flash('Se ha actualizado el lote', 'success')
    return redirect(url_for('lotes'))

@app.route("/movimientos", methods=['GET', 'POST'])
@login_required
@role_required([1])
def movimientos():
    movimientos = obtener_movimientos_por_lote(db_session)
    productos=obtener_productos_consumibless(db_session)
    


   
    return render_template("movimientos.html", movimientos=movimientos,productos=productos)
@app.route("/consumibles_productos", methods=['POST'])
def consumibles():
    if request.method == 'POST':
        try:
            data = request.json
            productos = data.get('productos', [])
          

            for producto_info in productos:
                producto_id = producto_info.get('id')
               
                cantidad_venta = producto_info.get('cantidad', 0)
               
                result = obtener_info_lote_mas_antiguo(db_session, producto_id)

                if result and result["cantidad"] > 0:
                    id_lote = int(result["id_lote"])
                    cantidad_lote = int(result["cantidad"])

                    while cantidad_venta > 0:
                        # Determinar la cantidad a restar en este lote
                        cantidad_a_restar_lote = min(
                            cantidad_venta, cantidad_lote)

                        # Restar la cantidad del lote
                        restar_cantidad_lote(
                            db_session, id_lote, cantidad_a_restar_lote)

                        # Restar la cantidad vendida del inventario
                        insertar_movimiento_inventario(
                            db_session, id_lote, "Consumo", cantidad_a_restar_lote)

                        # Restar la cantidad restante
                        cantidad_venta -= cantidad_a_restar_lote

                        # Insertar detalles de venta
                       

                        # Obtener la información del lote más antiguo para la siguiente iteración
                        result = obtener_info_lote_mas_antiguo(
                            db_session, producto_id)

                        if result and result["cantidad"] > 0:
                            id_lote = int(result["id_lote"])
                            cantidad_lote = int(result["cantidad"])
                        else:
                            print(
                                "No hay más lotes disponibles para restar la cantidad vendida.")
                            break

                db_session.commit()

            return jsonify({"mensaje": "Success"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500
    return 'null', 400


@app.route("/clientes", methods=['GET', 'POST'])
@role_required([1,2])
def clientes():
    clientes = mostra_clientes(db_session)
    return render_template("clientes.html", clientes=clientes)


@app.route('/crear_cliente', methods=['POST'])
def procesar_formulario():
    # Obtener datos del formulario
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    cedula = request.form['cedula']
    fecha_nacimiento = request.form['fecha_nacimiento']
    correo = request.form['email']
    celular = request.form['celular']
    direccion = request.form['direccion']
    genero = request.form['genero']
    tipo_cliente = request.form['tipo']
    archivo = request.files['foto']
    carpeta_destino = 'static/img/trabajadores'
    logo = guardar_imagen(archivo, carpeta_destino)
    idpersona = insertar_persona(
        db_session, nombre, correo, direccion, celular)
    insertar_persona_natural(db_session, idpersona, apellido,
                             cedula, fecha_nacimiento, genero, "Persona natural")
    codigo = generar_codigo_cliente(nombre, idpersona, celular)
    insertar_cliente(db_session, idpersona, codigo, tipo_cliente, logo)
    return redirect('/clientes')


@app.route('/actualizar_cliente/<int:cliente_id>', methods=['POST'])
def procesar_formulario_actualizacion(cliente_id):
    persona = request.form['id_persona']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    celular = request.form['celular']
    direccion = request.form['direccion']
    tipo_cliente = request.form['tipo']
    estado = request.form['estado']
    archivo = request.files['foto']
    logos = request.form.get('logos')
    if archivo:
        carpeta_destino = 'static/img/clientes/'
        logo = guardar_imagen(archivo, carpeta_destino)

        update_persona(db_session, persona, nombre, correo, celular, direccion)
        update_persona_natural(db_session, persona,
                               apellido, "Persona natural")
        update_cliente(db_session, cliente_id, tipo_cliente, logo, estado)

        try:
            os.remove(logos)  # Elimina la imagen anterior
        except Exception as e:
            print(f"No se pudo eliminar la imagen anterior: {e}")

        flash("Se ha actualizado el cliente con una nueva imagen.", "success")

    else:
        # En caso de que no se haya proporcionado un nuevo archivo, simplemente actualiza la información sin cambiar la imagen
        update_persona(db_session, persona, nombre, correo, celular, direccion)
        update_persona_natural(db_session, persona,
                               apellido, "Persona natural")
        update_cliente(db_session, cliente_id, tipo_cliente, logos, estado)

        flash("Se ha actualizado el cliente sin cambiar la imagen.", "success")

    return redirect(url_for('clientes'))


@app.route('/eliminar_cliente/<int:cliente_id>', methods=['POST'])
def cambiarestadocliente(cliente_id):
    cambiar_estado_cliente(db_session, cliente_id, 2)

    return redirect(url_for('clientes'))


@app.route("/citas", methods=['GET', 'POST'])
@login_required
@role_required([1,2,3])
def reserva():
    reservaciones = obtener_reservacion(db_session)
    return render_template("reservacion.html", reservaciones=reservaciones)


@app.route("/ventas", methods=['GET'])
@login_required
@role_required([1,2])
def venta():
    ventas = obtener_ventas(db_session)

    reservaciones = obtener_reservacion_hoy(db_session)
    tipos = obtener_tipo_venta(db_session)
    cantidad = obtener_cantidad_reservaciones_hoy(db_session)
  
    return render_template("venta.html", ventas=ventas, reservaciones=reservaciones, tipos=tipos, cantidad=cantidad)


@app.route('/ventacitas', methods=['POST'])
def ventacitas():
    tipo_venta = request.form['tipo_venta']
    if tipo_venta ==  '3': #Todas las ventas
        estado = 3
    else:
        estado = 1
    cliente = request.form['idcliente']
    total = request.form['subtotal']
    id_reserva = request.form['id']
    codigo = generar_codigo_venta(db_session)
    id_venta = insertar_venta(db_session, tipo_venta,
                              cliente, codigo, 0, total, estado)
    insertar_detalle_venta_cita(db_session, id_venta, id_reserva, total, total)
    cambiar_estado_reservacion(db_session, id_reserva, 4)
    flash("Se ha realizado la venta con exito", "success")
    return redirect('/ventas')

@app.route('/cambiarestadoventa', methods=['POST'])
def cambiarestadoventa():
    id_venta = request.form['id']
    #cambiar_estado_reservacion(db_session, id_reserva, 4)
    cambiar_estado_venta(db_session,id_venta,3)
    flash("Se ha saldado la venta correctamente", "success")
    return redirect('/ventas')


@app.route("/ventasproductos", methods=['GET', 'POST'])
@login_required
@role_required([1,2])
def ventasproductos():
    productos = obtener_productos_ventas(db_session)
    clientes = mostra_clientes(db_session)
    tipos = obtener_tipo_venta(db_session)
    return render_template("venta_productos.html", productos=productos, clientes=clientes, tipos=tipos)


@app.route("/ventaservicios", methods=['GET', 'POST'])
@role_required([1,2])
def ventaservicios():
    clientes = mostra_clientes(db_session)
    tipos = obtener_tipo_venta(db_session)
    servicios = obtener_precios_servicios(db_session)
    return render_template("ventas_servicios.html", clientes=clientes, tipos=tipos, servicios=servicios)


@app.route("/venta_productos", methods=['POST'])
def procesar_venta():
    if request.method == 'POST':
        try:
            data = request.json
            productos = data.get('productos', [])
            persona_id = data.get('cliente')
            tipo_venta = data.get('tipo_venta')
            total = data.get('total')
            codigo = generar_codigo_venta(db_session)

            id_venta = insertar_venta(
                db_session, tipo_venta, persona_id, codigo, 0, total, 1)

            for producto_info in productos:
                producto_id = producto_info.get('id')
                precio = producto_info.get('precio', Decimal('0.00'))
                cantidad_venta = producto_info.get('cantidad', 0)
                subtotal = cantidad_venta * precio
                result = obtener_info_lote_mas_antiguo(db_session, producto_id)

                if result and result["cantidad"] > 0:
                    id_lote = int(result["id_lote"])
                    cantidad_lote = int(result["cantidad"])

                    while cantidad_venta > 0:
                        # Determinar la cantidad a restar en este lote
                        cantidad_a_restar_lote = min(
                            cantidad_venta, cantidad_lote)

                        # Restar la cantidad del lote
                        restar_cantidad_lote(
                            db_session, id_lote, cantidad_a_restar_lote)

                        # Restar la cantidad vendida del inventario
                        insertar_movimiento_inventario(
                            db_session, id_lote, "Por venta", cantidad_a_restar_lote)

                        # Restar la cantidad restante
                        cantidad_venta -= cantidad_a_restar_lote

                        # Insertar detalles de venta
                        insertar_venta_producto(
                            db_session, id_venta, producto_id, precio, cantidad_a_restar_lote, subtotal)

                        # Obtener la información del lote más antiguo para la siguiente iteración
                        result = obtener_info_lote_mas_antiguo(
                            db_session, producto_id)

                        if result and result["cantidad"] > 0:
                            id_lote = int(result["id_lote"])
                            cantidad_lote = int(result["cantidad"])
                        else:
                            print(
                                "No hay más lotes disponibles para restar la cantidad vendida.")
                            break

                db_session.commit()

            return jsonify({"mensaje": "Success"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"mensaje": "Error interno del servidor"}), 500
    return 'null', 400


@app.route("/venta_servicios", methods=["POST"])
def ventas_servicios():
    try:
        data = request.json
        persona_id = data.get('cliente')
        tipo_venta = data.get('tipo_venta')
        total = data.get('total')
        servicios = data.get('servicios', [])
        codigo = generar_codigo_venta(db_session)

        id_venta = insertar_venta(
            db_session, tipo_venta, persona_id, codigo, 0, total, 1)

        for servicios_info in servicios:
            servicios_id = servicios_info.get('id')
            precio = servicios_info.get('precio', Decimal('0.00'))
            cantidad_venta = servicios_info.get('cantidad', 0)
            subtotal = cantidad_venta * precio
            insertar_detalle_venta(
                db_session, id_venta, servicios_id, precio, cantidad_venta, subtotal)

        # Enviar respuesta JSON en caso de éxito
        return jsonify({"mensaje": "La venta se ha realizado correctamente", "tipo": "success"}), 200
    except Exception as e:
        print(f"Error en ventas_servicios: {e}")
        # Enviar respuesta JSON en caso de error
        return jsonify({"mensaje": "Hubo un error al procesar la venta de servicios. Por favor, inténtalo nuevamente.", "tipo": "error"}), 500


@app.route("/ver_productos_cliente", methods=['GET', 'POST'])
def ver_productos_cliente():
    productos = obtener_productos(db_session)

    return render_template("productos_generador.html", productos=productos)


def obtener_productos_activos(db_session):

    return productos


@app.route("/ver_servicios_clientes", methods=['GET', "POST"])
def ver_servicios_clientes():

    servicios = obtener_servicios_activos(db_session)
    print(servicios)

    flash("El PDF se ha generado correctamente, los usuarios ya podran visualizar los nuevos cambios!", "success")
    return render_template("servicios_generador.html", servicios=servicios)


def generar_pdf_servicios(db_session):
    # Aquí es donde se renderiza tu plantilla HTML con Jinja
    # Se obtiene la lista de productos
    servicios = obtener_servicios_activos(db_session)

    rendered = render_template('servicios_generador.html', servicios=servicios)
    # Aquí es donde se convierte el HTML renderizado a PDF
    options = {
        'enable-local-file-access': '',
        'quiet': '',
        'no-outline': None,
        'encoding': 'utf-8',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'no-outline': None
    }
    css = ['static/css/boostrap4.css',
           'static/css/style_servicios_generador.css']
    pdf = pdfkit.from_string(
        rendered, 'static/pdf/servicios/Servicios.pdf', options=options, css=css)
    return True


def generar_pdf_productos(db_session):
    # Aquí es donde se renderiza tu plantilla HTML con Jinja
    # Se obtiene la lista de productos
    productos = obtener_productos(db_session)

    rendered = render_template('productos_generador.html', productos=productos)
    # Aquí es donde se convierte el HTML renderizado a PDF
    options = {
        'enable-local-file-access': '',
        'quiet': '',
        'no-outline': None,
        'encoding': 'utf-8',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'no-outline': None
    }
    css = ['static/css/boostrap4.css',
           'static/css/style_servicios_generador.css']
    pdf = pdfkit.from_string(
        rendered, 'static/pdf/productos/Productos.pdf', options=options, css=css)
    return True


@app.route('/generarPDFServicios', methods=['GET'])
def pruebitaPDFServicios():

    generar_pdf_servicios(db_session)
    flash("Se ha actualizado correctamente el servicio, recuerda de actualizar el PDF para los usuarios del BOT!", "success")
    return redirect('/ver_servicios_clientes')


@app.route('/generarPDFProductos', methods=['GET'])
def pruebitaPDFProductos():

    generar_pdf_productos(db_session)
    flash("Se ha actualizado correctamente el servicio, recuerda de actualizar el PDF para los usuarios del BOT!", "success")
    return redirect('/ver_productos_cliente')

def obter_datos_cliente_celular(celular):
    query = text("""
                 SELECT 
    clientes.id AS id_cliente,
    clientes.codigo,
    persona.id AS id_persona,
    persona.nombre,
    persona_natural.apellido,
    persona.correo,
    persona_natural.tipo_persona
FROM 
    clientes
JOIN 
    persona ON clientes.id_persona = persona.id
JOIN 
    persona_natural ON persona_natural.id_persona = persona.id
WHERE 
    persona.celular = :celular;
""")
    resultado = db_session.execute(query, {'celular': celular}).fetchone()

    datosCliente = {
        'id_cliente': resultado[0],
        'codigo': resultado[1],
        'id_persona': resultado[2],
        'nombre': resultado[3],
        'apellido': resultado[4],
        'correo': resultado[5],
        'tipo_persona': resultado[6]
    }
    db_session.close()

    return datosCliente

def guardar_reservacion(db_session: Session, id_cliente, id_servicio, idevento_calendar, fecha, hora_inicio, hora_final, subtotal, estado,id_metodo_pago):
    codigo=generar_codigo_reservacion(db_session)
    query = text("""
        INSERT INTO reservacion (idcliente, idservicio, idevento_calendar, codigo, fecha, hora_inicio, hora_fin, subtotal, estado,id_metodo_pago)
        VALUES (:id_cliente, :id_servicio, :idevento_calendar, :codigo, :fecha, :hora_inicio, :hora_fin, :subtotal, :estado,:id_metodo_pago)
        RETURNING id
    """)
    result = db_session.execute(query, {"id_cliente": id_cliente,"id_servicio": id_servicio,"idevento_calendar":idevento_calendar,"codigo": codigo,"fecha": fecha,"hora_inicio": hora_inicio, "hora_fin":hora_final, "subtotal": subtotal,"estado": estado,"id_metodo_pago":id_metodo_pago})
    id_reservacion = result.fetchone()[0]


    db_session.commit()
    db_session.close()
    return codigo

    # Devolver el ID de la reservación

def recuperar_id_cliente(db_session, codigo_cliente):
    query = text("""
        SELECT id
        FROM clientes
        WHERE codigo = :codigo_cliente
    """)

    id_cliente = db_session.execute(query, {'codigo_cliente': codigo_cliente}).scalar()
    db_session.close()

    return id_cliente

def recuperar_id_servicio(db_session, nombre_servicio):
    query = text("""
        SELECT id
        FROM servicios
        WHERE nombre = :nombre_servicio
    """)

    id_servicio = db_session.execute(query, {'nombre_servicio': nombre_servicio}).scalar()
    db_session.close()

    return id_servicio

def recuperar_precio_servicio(db_session, id):
    query = text("""
        SELECT precio
        FROM precio_servicios
        WHERE id_servicios = :id AND estado = 1
    """)

    id_servicio = db_session.execute(query, {'id': id}).scalar()
    db_session.close()

    return id_servicio

def procesamiento_hora_string(bloque):
    # Separando las cadenas de tiempo
    inicio_reserva_str, final_reserva_str = [s.strip() for s in bloque.split('a')]

    # Convierte las cadenas a objetos datetime.time
    hora_inicio_reserva = arrow.get(inicio_reserva_str, 'h:mm A').time()
    hora_final_reserva = arrow.get(final_reserva_str, 'h:mm A').time()

    return hora_inicio_reserva, hora_final_reserva

def procesamiento_fecha_hora_string(fecha, bloque):
    # Convierte la fecha string a datetime
    fecha_formateada = formatear_fecha(fecha)
    print(fecha_formateada)

    # Separando las cadenas de tiempo
    inicio_reserva_str, final_reserva_str = [s.strip() for s in bloque.split('a')]
            
    #Convierte las cadenas a objetos datetime.time
    hora_inicio_reserva = arrow.get(inicio_reserva_str, 'h:mm A').time()
    hora_final_reserva = arrow.get(final_reserva_str, 'h:mm A').time()

    # Convierto el objeto arrow a datetime
    fecha_formateada = fecha_formateada.date()

    fechaHora_IncioReserva = datetime.combine(fecha_formateada, hora_inicio_reserva)
    fechaHora_FinalReserva = datetime.combine(fecha_formateada, hora_final_reserva)

    return fechaHora_IncioReserva, fechaHora_FinalReserva
    

@cross_origin()
@app.route('/api_consultaDatosCliente', methods=['POST'])
def api_consultaDatosCliente():
    try:
        data = request.json
        print(data)
        celular = data.get('celular')
        datosCliente = obter_datos_cliente_celular(celular)
        print(datosCliente)
        if datosCliente:
            return jsonify(datosCliente), 200
        else:
            return jsonify({"mensaje": "No se encontró ningún cliente con el teléfono ceular proporcionada"}), 404
    except Exception as e:
        print(f"Error en api_consultaDatosCliente: {e}")
        return jsonify({"mensaje": "Hubo un error al procesar la solicitud"}), 500

# Define los alcances de la API de Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

'''def obtener_servicio():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardar el refresh token junto con las credenciales
        if hasattr(creds, 'refresh_token'):
            token_info = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            with open('token.pickle', 'wb') as token_file:
                pickle.dump(token_info, token_file)
    
    service = build('calendar', 'v3', credentials=creds)
    return service'''
def obtener_APIKEY_GCALENDAR():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

"""def crear_evento(service, inicio, fin):
    evento = {
        'summary': 'AutoLavado',
        'start': {
            'dateTime': inicio.isoformat(),
            'timeZone': 'America/Managua',
        },
        'end': {
            'dateTime': fin.isoformat(),
            'timeZone': 'America/Managua',
        },
    }
    evento_creado = service.events().insert(calendarId='primary', body=evento).execute()
    print(f"Evento creado: {evento_creado['htmlLink']}")"""

def crear_evento(service, correo, nombre_servicio, servicio_realizacion, inicio, fin):


    try:
        # Crear el evento
        evento = {
            'summary': nombre_servicio,
            'start': {
                'dateTime': inicio.isoformat(),
                'timeZone': 'America/Managua',
            },
            'end': {
                'dateTime': fin.isoformat(),
                'timeZone': 'America/Managua',
            },
            'description': f'Servicio realizado por {correo}. Duración: {servicio_realizacion}.',
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'email', 'minutes': 30},
                ],
            },
        }

        # Crear el evento y obtener el ID
        evento_creado = service.events().insert(calendarId='primary', body=evento).execute()
        evento_id = evento_creado['id']

        print(f"Evento creado: {evento_id}")

        return evento_id

    except ValueError as e:
        print(f"Error al convertir la fecha/hora: {e}")
        return None


@app.route('/api_obtener_dias_disponibles/', methods=['GET', 'POST'])
def api_obtener_dias_disponibles():



    # # Obtiene el servicio de Google Calendar
    # service = obtener_servicio()

    # # Define las horas de inicio y fin del evento
    # inicio = datetime.now()
    # fin = inicio + timedelta(hours=1)

    # # Crea el evento
    # crear_evento(service, inicio, fin)

    rows = horariosistema(db_session)

    # Crear el diccionario
    tabla = {}
    for row in rows:
        tabla[row[2]] = {"estado": row[5], "apertura": row[3].strftime(
            "%H:%M"), "cierre": row[4].strftime("%H:%M")}

    dias_semana = ["Lunes", "Martes", "Miercoles",
                   "Jueves", "Viernes", "Sabado", "Domingo"]

    # ESTRUCTURA DE LA TABLA DEL SELECT
    # Tu tabla en forma de diccionario con horarios de apertura y cierre
    # tabla = {
    #     "Lunes": {"estado": 1, "apertura": "08:00", "cierre": "18:00"},
    #     "Martes": {"estado": 1, "apertura": "08:00", "cierre": "18:00"},
    #     "Miércoles": {"estado": 1, "apertura": "08:00", "cierre": "18:00"},
    #     "Jueves": {"estado": 1, "apertura": "08:00", "cierre": "18:00"},
    #     "Viernes": {"estado": 1, "apertura": "08:00", "cierre": "18:00"},
    #     "Sábado": {"estado": 1, "apertura": "08:00", "cierre": "18:00"},
    #     "Domingo": {"estado": 2, "apertura": "00:00", "cierre": "00:00"}
    # }

    # Lista de los días de la semana en orden
    dias_semana = ["Lunes", "Martes", "Miércoles",
                   "Jueves", "Viernes", "Sábado", "Domingo"]

    # Obtén el día de la semana y la hora actual
    hoy = datetime.now()
    dia_actual = dias_semana[hoy.weekday()]
    hora_actual = datetime.strptime(hoy.strftime("%H:%M"), "%H:%M")

    # Encuentra el índice del día de la semana actual en la lista
    indice_actual = dias_semana.index(dia_actual)

    # Reordena la lista de días de la semana para que comience desde el día actual
    dias_semana = dias_semana[indice_actual:] + dias_semana[:indice_actual]

    # Crea una lista para almacenar los próximos 7 días
    proximos_dias = []

    # Recorre la lista de días de la semana
    i = 0
    while len(proximos_dias) < 7 and i < 14:  # Limita el valor de i a 14
        # Calcula la fecha para el día de la semana actual
        fecha = hoy + timedelta(days=i)

        # Obtiene el nombre del día de la semana
        dia_semana = dias_semana[i % 7]

        # Verifica si el día está disponible y si la hora actual es antes de la hora de cierre
        hora_cierre = datetime.strptime(tabla[dia_semana]["cierre"], "%H:%M")
        if tabla[dia_semana]["estado"] == 1 and (hora_actual < hora_cierre or fecha.date() > hoy.date()):
            # Si el día está disponible y no ha pasado la hora de cierre, añádelo a la lista de próximos días
            proximos_dias.append(fecha.strftime("%A %d de %B de %Y"))
        i += 1

    # Imprime los próximos 7 días
    proximos_dias = [dia.encode('latin1').decode('utf8') for dia in proximos_dias]

    proximos_dias = [dia.lower().capitalize() for dia in proximos_dias]

    for dia in proximos_dias:
        print(dia)

    return jsonify(proximos_dias)



@cross_origin()
@app.route('/api_agregar_reserva', methods=['POST'])
def api_agregar_reserva():
    try:
        data = request.get_json()
        print(data)
        id_cliente = data['datos_personales']['id_cliente']
        codigo_cliente = data['datos_personales']['codigo_cliente']
        id_persona = data['datos_personales']['id_persona']
        nombre = data['datos_personales']['nombre']
        apellidos = data['datos_personales']['apellidos']
        correo = data['datos_personales']['correo']
        celular = data['datos_personales']['celular']
        fecha = data['datos_reserva']['fecha']
        nombre_servicio = data['datos_reserva']['nombre_servicio']
        servicio_realizacion = data['datos_reserva']['servicio_realizacion']
        bloque_horario = data['datos_reserva']['bloque_horario']
        id_metodo_pago=data['datos_reserva']['metodo']

        if not codigo_cliente or not id_persona or not id_cliente:
            id_persona = insertar_persona(db_session, nombre, correo,"En direccion", celular)
            
            insertar_persona_natural(db_session, id_persona, apellidos, None, None, None,"Natural")
            codigo = generar_codigo_cliente(nombre,id_persona,celular)
          
            codigo_cliente=insertar_cliente(db_session, id_persona,codigo,"Normal","No hay")
    
        fechaHora_IncioReserva, fechaHora_FinalReserva = procesamiento_fecha_hora_string(fecha, bloque_horario)

        nombre_reserva = 'Reserva de lavado para:  ' + nombre + ' ' + apellidos
        service = obtener_APIKEY_GCALENDAR() 

        id_evento = crear_evento(service, correo, nombre_servicio, servicio_realizacion, fechaHora_IncioReserva, fechaHora_FinalReserva)

        if id_evento:
            try:
              
                fecha_formateada = obtener_numero_dia(fecha)

                id_cliente = recuperar_id_cliente(db_session, codigo_cliente)

                id_servicio = recuperar_id_servicio(db_session, nombre_servicio)


                hora_inicio_reserva, hora_final_reserva = procesamiento_hora_string(bloque_horario)
                subtotal = recuperar_precio_servicio(db_session, id_servicio)
                codigo_reservacion = guardar_reservacion(db_session, id_cliente, id_servicio, id_evento, fecha_formateada, hora_inicio_reserva, hora_final_reserva, subtotal, '1',id_metodo_pago)

                print(codigo_reservacion)

                return jsonify({'sucess': True, 'codigo_reservacion': codigo_reservacion, 'message': 'Se ha agregado la reserva correctamente'})

            except Exception as e:
                print(e)
                return jsonify({'success': False, 'message': 'Ocurrió un error al guardar la reserva en la base de datos'})

        else:
            return jsonify({'success': False, 'message': 'Ocurrió un error al crear el evento en Google Calendar'})

        
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Ocurrió un error'})   



# Esta API es para obtener del bot el la duración del servicio seleccionado
# ademas de su dia


@cross_origin()
@app.route('/api_duracionLavado_dia', methods=['GET', 'POST'])
def api_duracionLavado_dia():
    if request.method == 'POST':
        try:
            data = request.get_json()
            realizacion = data['realizacion']
            fecha = data['fecha']
            nombre = data['nombre']

            # Divide la cadena en horas, minutos y segundos
            horas, minutos, segundos = estructurarTexto_a_variables(realizacion)

            # Convierte las horas y minutos a minutos
            total_minutos = convertirHoras_a_Minutos(horas, minutos, segundos)
            print(total_minutos)

            # Obtiene los horarios del sistema
            rows = horariosistema(db_session)


            # Crear el diccionario
            tabla = {}
            for row in rows:
                tabla[row[2]] = {"estado": row[5], "apertura": row[3].strftime("%H:%M"), "cierre": row[4].strftime("%H:%M")}
            
            dias_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
            
            print(tabla)
            # Convierte la fecha string a datetime
            fecha_formateada = formatear_fecha(fecha)

            # Obtiene solamente el día del mes
            dia = fecha_formateada.day


            # Obtiene el día de la semana en español
            ## NOTA
            ### Para evitar los problemas de codificación, se codifica el día de la semana a latin1
            dia_semana = fecha_formateada.strftime("%A")




            # Verifica si el día está disponible y si la hora actual es antes de la hora de cierre
            dia_semana = dia_semana.encode('latin1').decode('utf8') # Codifica el día de la semana para que aparezca acento
            dia_semana = dia_semana.lower().capitalize() #Le pone la primera letra en mayuscula
            hora_apertura = datetime.strptime(tabla[dia_semana]["apertura"], "%H:%M")
            hora_cierre = datetime.strptime(tabla[dia_semana]["cierre"], "%H:%M")

            hora_apertura_formateada = hora_apertura.time()  # Extrae solo la hora de apertura
            hora_cierre_formateada = hora_cierre.time()  # Extrae solo la hora de cierre

            service = obtener_APIKEY_GCALENDAR()  # Obtiene el servicio de Google Calendar TOKEN
            print(dia_semana)
            print(hora_apertura_formateada)
            print(hora_cierre_formateada)

            # Especifica la zona horaria
            tz = timezone('America/Managua')


            print("aquí viene la depuración")
            print(hora_apertura)
            print(hora_cierre)

            # Convertir las horas a formato de 24 horas
            hora_apertura = hora_apertura_formateada.hour
            hora_cierre = hora_cierre_formateada.hour

            print("aquí viene la depuración")
            print(hora_apertura)
            print(hora_cierre)

            # Mapeo de los días de la semana a números
            dias = {
                "Lunes": 1,
                "Martes": 2,
                "Miércoles": 3,
                "Jueves": 4,
                "Viernes": 5,
                "Sábado": 6,
                "Domingo": 7
            }

            # Asegúrate de usar la zona horaria correcta
            tz = timezone('America/Managua')

            # Obtener el año y el mes en curso
            anio_actual = datetime.now().year
            mes_actual = datetime.now().month

            print(dias)

            # Crear las fechas de inicio y fin
            # fecha_inicio = datetime(anio_actual, mes_actual, dias[dia_semana], hora_apertura, tzinfo=tz)
            # fecha_fin = datetime(anio_actual, mes_actual, dias[dia_semana], hora_cierre, tzinfo=tz)
            fecha_inicio = datetime(anio_actual, mes_actual, dia, hora_apertura_formateada.hour, hora_apertura_formateada.minute , tzinfo=tz)  # 8 AM del 11 de enero de 2024
            fecha_fin = datetime(anio_actual, mes_actual, dia, hora_cierre_formateada.hour, hora_apertura_formateada.minute, tzinfo=tz)  # 5 PM del mismo día

            # Obtiene los eventos en ese rango de tiempo
            events_result = service.events().list(
                calendarId='primary',
                timeMin=fecha_inicio.isoformat(),
                timeMax=fecha_fin.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Eventos existentes (hora inicio y fin en formato 'HH:MM')
            eventos_existentes = []

        

            for event in events:
                start = event['start'].get(
                    'dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                # Convierte la fecha y hora a un objeto datetime
                fecha_hora_inicio = datetime.fromisoformat(start)
                fecha_hora_fin = datetime.fromisoformat(end)

                # Formatea la hora y minuto en el formato 'HH:MM'
                hora_inicio = fecha_hora_inicio.strftime('%H:%M')
                hora_fin = fecha_hora_fin.strftime('%H:%M')

                # Agrega la hora de inicio y fin a la lista
                eventos_existentes.append((hora_inicio, hora_fin))

            print(eventos_existentes)

            bloques_disponibles = consultar_horarios_disponibles_googleCalendar(dia_semana, total_minutos, eventos_existentes)


            return jsonify(bloques_disponibles)
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'message': 'Ocurrió un error'})


    return jsonify({'success': True})



def consultar_horarios_disponibles_googleCalendar(dia_disponible, duracion_evento, eventos_existentes):
    # Tu diccionario
    rows = horariosistema(db_session)

    # Crear el diccionario
    horario = {}
    for row in rows:
        horario[row[2]] = {"estado": row[5], "apertura": row[3].strftime(
            "%H:%M"), "cierre": row[4].strftime("%H:%M")}

    # Duración del evento en minutos

    # Tiempo de margen en minutos
    margen = 10

    # Eventos existentes (hora inicio y fin en formato 'HH:MM')


    bloques_disponibles = []

    def obtener_horarios_disponibles(dia, duracion_evento, margen, eventos_existentes):
        apertura = datetime.strptime(horario[dia]['apertura'], '%H:%M')
        cierre = datetime.strptime(horario[dia]['cierre'], '%H:%M')
        duracion_evento = timedelta(minutes=duracion_evento)
        margen = timedelta(minutes=margen)

        horarios_disponibles = []
        hora_actual = apertura

        for inicio, fin in eventos_existentes:
            inicio = datetime.strptime(inicio, '%H:%M')
            fin = datetime.strptime(fin, '%H:%M')

            while hora_actual + duracion_evento <= inicio:
                horarios_disponibles.append(
                    (hora_actual.time(), (hora_actual + duracion_evento).time()))
                hora_actual += duracion_evento + margen

            hora_actual = fin + margen

        while hora_actual + duracion_evento <= cierre:
            horarios_disponibles.append(
                (hora_actual.time(), (hora_actual + duracion_evento).time()))
            hora_actual += duracion_evento + margen

        return horarios_disponibles

    horarios_disponibles = obtener_horarios_disponibles(
        dia_disponible, duracion_evento, margen, eventos_existentes)

    for inicio, fin in horarios_disponibles:
        inicio_str = convertir_a_12_horas(inicio)
        fin_str = convertir_a_12_horas(fin)

        horario = f'{inicio_str} a {fin_str}'
        bloques_disponibles.append(horario)

    # Ahora horarios_str contiene todas las cadenas de texto
    print(bloques_disponibles)
    return bloques_disponibles


def convertir_a_12_horas(hora):
    if hora.hour < 12:
        if hora.hour == 0:
            hora_str = '12:{:02d} AM'.format(hora.minute)
        else:
            hora_str = '{:02d}:{:02d} AM'.format(hora.hour, hora.minute)
    else:
        if hora.hour > 12:
            hora_str = '{:02d}:{:02d} PM'.format(hora.hour - 12, hora.minute)
        else:
            hora_str = '{:02d}:{:02d} PM'.format(hora.hour, hora.minute)
    return hora_str


@cross_origin()
@app.route('/obtener_reservaciones_estado_1/<telefono>', methods=['GET'])
def obtener_reservaciones_estado_1(telefono):
    # Query para obtener reservaciones en estado 1 filtradas por número de teléfono
    query = text("""
        SELECT r.codigo, r.fecha
        FROM reservacion r
        JOIN clientes c ON r.idcliente = c.id
        JOIN persona p ON c.id_persona = p.id
        WHERE r.estado = 1 AND p.celular = :telefono;
    """)

    reservaciones = db_session.execute(query, {"telefono": telefono}).fetchall()

    # Procesar los resultados según tu necesidad
    reservaciones_resultado = [
        {"codigo": reserva.codigo, "fecha": reserva.fecha}
        for reserva in reservaciones
    ]
    db_session.close()

    return jsonify(reservaciones_resultado)
def eliminar_evento_google_calendar(service, evento_id):
    # Eliminar el evento
    service.events().delete(
        calendarId='primary',
        eventId=evento_id
    ).execute()
@app.route('/cancelar_reserva/<codigo_reserva>', methods=['POST'])
def cancelar_reserva(codigo_reserva):
    try:
        # Realizar la actualización en la base de datos para cambiar el estado de la reserva
        query = text("UPDATE reservacion SET estado = 2 WHERE codigo = :codigo_reserva AND estado = 1")
        result = db_session.execute(query, {"codigo_reserva": codigo_reserva})
        db_session.commit()

        # Verificar si la reserva fue cancelada
        if result.rowcount > 0:
            # Obtener el idevento_calendar asociado a la reserva cancelada
            query_id_evento = text("SELECT idevento_calendar FROM reservacion WHERE codigo = :codigo_reserva")
            resultado_id_evento = db_session.execute(query_id_evento, {"codigo_reserva": codigo_reserva}).fetchone()
            print(resultado_id_evento)

            # Verifica si hay un resultado antes de intentar acceder a sus elementos
            if resultado_id_evento and len(resultado_id_evento) > 0:
                idevento_calendar = resultado_id_evento[0]
                
                # Obtener el servicio de Google Calendar
                service = obtener_APIKEY_GCALENDAR()

                # Llamar a la función para eliminar el evento de Google Calendar
                eliminar_evento_google_calendar(service, idevento_calendar)

      
            db_session.close()            
            return jsonify({"mensaje": "Reserva cancelada exitosamente."}), 200
        else:
            return jsonify({"mensaje": "No se pudo cancelar la reserva. Verifica el código de reserva o el estado actual."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@cross_origin()
@app.route('/reservaciones_hoy_admin', methods=['GET'])
def obtener_reservaciones_hoy_admin():
    try:
        # Obtener las reservaciones de hoy para el administrador
        reservaciones = obtener_reservacion_hoy_admin(db_session)
        print(reservaciones)
        # Procesar los resultados según tu necesidad
        reservaciones_resultado = [
            {
                "id": reserva.id,
                "codigo":reserva.codigo,
                "cliente": reserva.cliente,
                "servicio": reserva.servicio,
                "fecha": reserva.fecha.strftime("%Y-%m-%d"),
                "hora_inicio": str(reserva.hora_inicio),  # Convertir time a cadena
                "hora_fin": str(reserva.hora_fin),  # Convertir time a cadena
                "celular": reserva.celular
            }
            for reserva in reservaciones
        ]

        return jsonify(reservaciones_resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@cross_origin()
@app.route('/reservaciones_hoy_admin_estado', methods=['GET'])
def obtener_reservaciones_hoy_admin_estado():
    try:
        # Obtener las reservaciones de hoy para el administrador
        reservaciones =obtener_reservacion_hoy_admin_estado(db_session)
        print(reservaciones)
        # Procesar los resultados según tu necesidad
        reservaciones_resultado = [
            {
                "id": reserva.id,
                "codigo":reserva.codigo,
                "idcliente":reserva.idcliente,
                "cliente": reserva.cliente,
                "servicio": reserva.servicio,
                "subtotal":reserva.subtotal,
                "fecha": reserva.fecha.strftime("%Y-%m-%d"),
                "hora_inicio": str(reserva.hora_inicio),  # Convertir time a cadena
                "hora_fin": str(reserva.hora_fin),  # Convertir time a cadena
                "celular": reserva.celular
            }
            for reserva in reservaciones
        ]

        return jsonify(reservaciones_resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    
@cross_origin()
@app.route('/metododepago', methods=['GET'])
def metododepago():
    try:
        # Obtener las reservaciones de hoy para el administrador
        tipos = obtener_tipo_venta(db_session)
        print(tipos)
        # Procesar los resultados según tu necesidad
        reservaciones_resultado = [
            {
                "id": reserva.id,
                "nombre":reserva.nombre
            }
            for reserva in tipos
        ]

        return jsonify(reservaciones_resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500  
@cross_origin()
@app.route('/cambiar_estado_reserva', methods=['POST'])
def cambiar_estado_reserva():
    try:
        # Obtener el código de reserva del cuerpo de la solicitud
        codigo_reserva = request.json.get("codigo_reserva")

        # Validar si se proporcionó el código de reserva
        if not codigo_reserva:
            return jsonify({"error": "Se requiere el código de reserva"}), 400

        # Realizar la actualización en la base de datos para cambiar el estado de la reserva a 5
        query = text("UPDATE reservacion SET estado = 5 WHERE codigo = :codigo_reserva AND estado = 1")
        result = db_session.execute(query, {"codigo_reserva": codigo_reserva})
        db_session.commit()
        db_session.close()

        # Verificar si la reserva fue actualizada
        if result.rowcount > 0:
            return jsonify({"mensaje": "Estado de la reserva cambiado a 5 exitosamente."}), 200
        else:
            return jsonify({"mensaje": "No se pudo cambiar el estado de la reserva. Verifica el código de reserva o el estado actual."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def obtener_informacion_venta_por_codigo(db_session, codigo):
    # Lógica para obtener información necesaria para la venta usando el código
    query = text("SELECT idcliente, subtotal, id,id_metodo_pago FROM reservacion WHERE codigo = :codigo")
    result = db_session.execute(query, {"codigo": codigo}).fetchone()
    db_session.close()

    return result
@cross_origin()
@app.route('/realizar_venta', methods=['POST'])
def realizar_venta():
    data = request.json

    # Obtener código de la solicitud
    codigo= data['codigo']
    # Obtener información de la venta desde la base de datos usando el código
    info_venta = obtener_informacion_venta_por_codigo(db_session, codigo)

    if not info_venta:
        return jsonify({'error': 'Código de venta no válido'}), 400

    id_cliente, subtotal, id_reserva,id_metodo_pago = info_venta

    # Generar código de venta
    codigo_venta = generar_codigo_venta(db_session)

    # Insertar venta en la base de datos
    id_venta = insertar_venta(db_session,id_metodo_pago, id_cliente, codigo_venta, 0,subtotal, 1)

    # Insertar detalle de venta de cita en la base de datos
    insertar_detalle_venta_cita(db_session, id_venta, id_reserva, subtotal, subtotal)

    # Cambiar estado de la reservación
    cambiar_estado_reservacion(db_session, id_reserva, 4)

    db_session.commit()
    return jsonify({'message': 'Venta realizada exitosamente', 'id_venta': id_venta}), 200

@cross_origin()
@app.route("/cotizacionproducto", methods=['GET', 'POST'])
def cotizacionproducto():
    if request.method == 'GET':
        productos = obtener_productos(db_session)
        productos_as_dicts = [
            {
                "index":index+1,
                "id": reserva.id,
                "nombre":reserva.nombre
            }
            for index, reserva in enumerate(productos)
        ]
     
        return jsonify(productos_as_dicts), 200
    elif request.method == 'POST':
        # Aquí puedes manejar la lógica para el método POST si es necesario
        data = request.json
        codigo=data.get('codigoProducto')
        telefono=data.get('numero')
        insertar_notificacion(db_session,codigo,telefono,1)
        return jsonify({'message': 'Se ha consultado'}), 200
    else:
        return jsonify({'error': 'Método no permitido'}), 405

def verificar_telefono_en_lista_negra(db_session, telefono):
    query = text("SELECT COUNT(*) FROM lista_negra WHERE telefono = :telefono")
    resultado = db_session.execute(query, {"telefono": telefono}).fetchone()
    print(resultado)
    db_session.close()
    # Devuelve True si el teléfono está en la lista negra (resultado es mayor que 0), False en caso contrario
    return resultado[0] > 0
@cross_origin()
@app.route("/cambiarcotizacionproducto/<int:id>", methods=['GET', 'POST'])
def cambiarcotizacionproducto(id):
    if request.method == 'POST':
        telefono=request.form['telefono']
        telefono_en_lista_negra = verificar_telefono_en_lista_negra(db_session, telefono)
        if telefono_en_lista_negra:
            cambiar_estado_notificacion(db_session, id, 2)
            actualizar_estado_lista_negra(db_session, telefono,0)
            return redirect("/")
        else:
            cambiar_estado_notificacion(db_session, id, 2)
            insertar_lista_negra(db_session,telefono)
            return redirect("/")
    else:
        return jsonify({'error': 'Método no permitido'}), 405
@cross_origin()
@app.route("/cambiarlista/<int:id>", methods=['GET', 'POST'])
def lista(id):
    if request.method == 'POST':
        telefono=request.form['telefono']
        actualizar_estado_lista_negra(db_session, telefono,1)
        return redirect("/")
    else:
        return jsonify({'error': 'Método no permitido'}), 405

def mostrar_lista(db_session):
    try:
        query = text("SELECT * FROM lista_negra where estado=0")
        result = db_session.execute(query)
        lista_negra = result.fetchall()
        db_session.close()
        return lista_negra
    except Exception as e:
        print(f"Error al mostrar la lista negra: {str(e)}")
        return []



def insertar_notificacion(db_session, id_producto, telefono, estado):
    query = text("INSERT INTO notificarproducto (id_producto, telefono, estado) VALUES (:id_producto, :telefono, :estado)")
    db_session.execute(query, {"id_producto": id_producto, "telefono": telefono, "estado": estado})
    db_session.commit()
    db_session.close()

def cambiar_estado_notificacion(db_session, id_notificacion, nuevo_estado):
    query = text("UPDATE notificarproducto SET estado = :nuevo_estado WHERE id = :id_notificacion")
    db_session.execute(query, {"nuevo_estado": nuevo_estado, "id_notificacion": id_notificacion})
    db_session.commit()
    db_session.close()

def obtener_notificaciones(db_session):
    query = text("SELECT np.*, p.nombre AS nombre_producto, p.logo AS logo_producto FROM notificarproducto np "
                 "JOIN producto p ON np.id_producto = p.id WHERE np.estado = 1")
    result = db_session.execute(query)
    notificaciones = result.fetchall()
    db_session.close()
    db_session.close()
    return notificaciones

def contar_notificaciones_estado_1(db_session):
    query = text("SELECT COUNT(*) FROM notificarproducto WHERE estado = 1")
    result = db_session.execute(query)
    numero_notificaciones_estado_1 = result.scalar()
    db_session.close()
    return numero_notificaciones_estado_1

def contar_notificaciones_lista(db_session):
    query = text("SELECT COUNT(*) FROM lista_negra WHERE estado = 0")
    result = db_session.execute(query)
    numero_notificaciones_estado_1 = result.scalar()
    db_session.close()
    return numero_notificaciones_estado_1
def insertar_lista_negra(db_session, telefono):
    try:
        query = text("INSERT INTO lista_negra (telefono, estado) VALUES (:telefono, :estado)")
        db_session.execute(query, {"telefono": telefono, "estado": 0})  # Estado predeterminado 0
        db_session.commit()
        db_session.close()
        print("Número insertado correctamente en la lista negra.")
    except Exception as e:
        db_session.rollback()
        print(f"Error al insertar el número en la lista negra: {str(e)}")


def actualizar_estado_lista_negra(db_session, telefono, nuevo_estado):
    try:
        query = text("UPDATE lista_negra SET estado = :nuevo_estado WHERE telefono = :telefono")
        db_session.execute(query, {"nuevo_estado": nuevo_estado, "telefono": telefono})
        db_session.commit()
        db_session.close()
        print("Estado actualizado correctamente en la lista negra.")
    except Exception as e:
        db_session.rollback()
        print(f"Error al actualizar el estado en la lista negra: {str(e)}")
# Esa ruta debe de usarse si y solamente si el token de la API de Google Calendar expira
# O es primara instalación
# @app.route('/generar_API_KEY_CALENDAR', methods=['GET', 'POST'])
# def generar_API_KEY_CALENDAR():
#     try:
#         obtener_APIKEY_GCALENDAR()
#         return 'Se ha generado la API KEY de Google Calendar'
#     except Exception as e:
#         print(e)
#         return 'No se puedo generar la API KEY!'
        
@cross_origin()
@app.route('/lista_negra', methods=['GET'])
def obtener_lista_negra():
    try:
       
       query = text("SELECT telefono FROM lista_negra where estado = 0")
       result = db_session.execute(query)
       registros = result.fetchall()

        # Cerrar la sesión
       db_session.close()

       if not registros:  # Si la lista de registros está vacía
            lista_negra = [{'telefono': '12345678'}]
            return jsonify({'lista_negra': lista_negra})
       else:
            lista_negra = [{'telefono': registro.telefono} for registro in registros]    
            return jsonify({'lista_negra': lista_negra})
    except Exception as e:
        return jsonify({'error': str(e)}), 500  
    
@cross_origin()
@app.route("/validar_usuario_por_telefono", methods=['POST'])
def validar_usuario_por_telefono():
    if request.method == 'POST':
        # Obtener el número de teléfono del cuerpo de la solicitud
        telefono = request.json.get('telefono')
        # Consulta SQL para verificar si el número de teléfono está presente en la tabla persona
        query_persona = text("SELECT id, nombre FROM persona WHERE celular = :telefono")
        result_persona = db_session.execute(query_persona, {'telefono': telefono}).fetchone()
        
        if result_persona:
            id_persona, nombre = result_persona

            # Consulta SQL para verificar si el id_persona existe en la tabla usuario y tiene el rol número 3
            query_usuario = text("SELECT id FROM usuario WHERE id_persona = :id_persona AND rol = 3")
            result_usuario = db_session.execute(query_usuario, {'id_persona': id_persona}).fetchone()
            db_session.close()

            if result_usuario:
                return jsonify({'nombre': nombre}),200
            else:
                return jsonify({'mensaje': 'El usuario no tiene el rol número 3'})
        else:
            return jsonify({'mensaje': 'El número de teléfono no está asociado a ningún usuario'})
    else:
        return jsonify({'error': 'Método no permitido'}), 405

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True)
