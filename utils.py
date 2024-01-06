"""Archivos con funciones"""
from werkzeug.security import *
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import os
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