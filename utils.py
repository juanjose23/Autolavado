"""Archivos con funciones"""
from werkzeug.security import *
from werkzeug.utils import secure_filename
from datetime import datetime

from flask import redirect,session
from functools import wraps
import uuid
import os
import string
import random
import arrow

def generar_codigo_cliente(nombre, id_persona, telefono):
    nombre_normalizado = nombre.lower()
    nombre_sin_espacios = nombre_normalizado.replace(' ', '_') # o '-' si prefieres guiones
    codigo = f"CL_{nombre_sin_espacios}_{id_persona}_{telefono}"
    return codigo


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_imagen(archivo, carpeta_destino):
    # Asegurarse de que la carpeta destino exista
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Verificar si el archivo es seguro y tiene una extensión válida
    if archivo and allowed_file(archivo.filename):
        # Obtener la marca de tiempo actual y un identificador único
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4().hex)[:8]

        # Obtener el nombre seguro del archivo
        filename = secure_filename(archivo.filename)

        # Construir un nombre único usando la marca de tiempo y el identificador único
        nombre_unico = f"{timestamp}_{unique_id}_{filename}"

        # Guardar el archivo en la carpeta destino
        ruta_destino = os.path.join(carpeta_destino, nombre_unico)
        archivo.save(ruta_destino)

        return ruta_destino

    return None

def generar_contraseña():
    # Letras mayúsculas, minúsculas y dígitos
    caracteres = string.ascii_letters + string.digits
    longitud = 8
    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))
    return contraseña

def generar_nombre_usuario(nombre, apellido, id_persona):
    # Eliminar espacios del nombre y apellido
    nombre_sin_espacios = nombre.replace(" ", "")
    apellido_sin_espacios = apellido.replace(" ", "")

    # Tomar las primeras tres letras del nombre y apellido (si no están vacíos)
    primeras_letras_nombre = nombre_sin_espacios[:3].lower() if nombre_sin_espacios else ""
    primeras_letras_apellido = apellido_sin_espacios[:3].lower() if apellido_sin_espacios else ""

    # Concatenar las primeras letras del nombre y apellido con el ID de la persona
    nombre_usuario = f"{primeras_letras_nombre}{primeras_letras_apellido}{id_persona}"

    return nombre_usuario

def generar_numero_lote():
    # Genera un UUID (por ejemplo, 'c5a0f3c8-03d8-4f9b-8c25-2a5117d7d1e6')
    uuid_str = str(uuid.uuid4())

    # Elimina guiones y toma los primeros 10 caracteres del UUID
    numero_lote = uuid_str.replace('-', '')[:10]

    return numero_lote

# Ejemplo de uso
nuevo_numero_lote = generar_numero_lote()

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("usuario_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Obtener el número del día de la semana por una cadnea de texto por ejemplo 'Lunes 15 de enero de 2024' = 1
def obtener_numero_dia(cadena):
    # Convertir la cadena a un objeto de fecha
    fecha = arrow.get(cadena, 'dddd D [de] MMMM [de] YYYY', locale='es')

    fecha_date = fecha.date()
    return fecha_date




def estructurarTexto_a_variables(realizacion):

    horas, minutos, segundos = map(int, realizacion.split(':'))

    return horas, minutos, segundos

#Crea una función para convertir un date time que está divido en horas, minutos y segundos al total de minutos

def convertirHoras_a_Minutos(horas, minutos, segundos):
    total_minutos = (horas * 60) + minutos + (segundos / 60)
    return total_minutos

def  formatear_fecha(fecha):
    fecha_formateada = arrow.get(fecha, 'dddd D [de] MMMM [de] YYYY', locale='es')
    return fecha_formateada