from collections import defaultdict
import os
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import random
from flask import Flask, send_file, session, redirect, url_for, render_template, request, flash, jsonify,make_response
from flask_mail import Mail, Message
from flask_cors import cross_origin, CORS
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from sqlalchemy import *
from sqlalchemy.orm import *
from model import *
import requests
import json
from datetime import time

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SESSION_PERMANENT"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ingsoftwar123@gmail.com'
app.config['MAIL_PASSWORD'] = 'xishvjfvtnrabdpj'
app.secret_key = '123'
mail = Mail(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db_session = scoped_session(sessionmaker(bind=engine))


def generar_codigo_cliente(nombre, id_persona, telefono):
    nombre_normalizado = nombre.lower()
    nombre_sin_espacios = nombre_normalizado.replace(' ', '_') # o '-' si prefieres guiones
    codigo = f"CL_{nombre_sin_espacios}_{id_persona}_{telefono}"
    return codigo

@cross_origin()
@app.route('/insertar_usuario', methods=['GET', 'POST'])
def insertar_usuario():
    request_data = request.get_json()
    print(request_data)

    if request.method == 'POST':

        query1 = text("INSERT INTO persona (nombre, correo, direccion, celular) VALUES (:nombre, :correo, :direccion, :celular) RETURNING id")
        id_persona = db_session.execute(query1,{"nombre": request_data['nombre'], "correo": request_data['correo'], "direccion": 'No hay', "celular": request_data['celular']}).fetchone()
        
        # Luego de inertar la persona, obtenemos el codigo del cliente mediante el retorno de id_persona
        codigo_cliente = generar_codigo_cliente(request_data['nombre'], id_persona[0], request_data['celular'])

        query2 = text("INSERT INTO persona_natural (id_persona, apellido, tipo_persona) VALUES (:id_persona, :apellido, :tipo_persona)")
        db_session.execute(query2,{"id_persona": id_persona[0], "apellido": request_data['apellidos'], "tipo_persona": request_data['tipo']})

        query3 = text("INSERT INTO clientes (id_persona, codigo, tipo_cliente, foto, estado) VALUES (:id_persona, :codigo, :tipo_cliente, :foto, :estado)")
        db_session.execute(query3,{"id_persona": id_persona[0], "codigo": codigo_cliente, "tipo_cliente": request_data['tipo'], "foto": 'No hay', "estado": '1'})

        # Aquí puedes insertar el código del cliente en tu base de datos

        db_session.commit()
        return codigo_cliente, 200
    return 'null', 400

@cross_origin()
@app.route('/insertarusuariosobligatorio', methods=['GET', 'POST'])
def insertar_usuarios():
    request_data = request.get_json()

    if request.method == 'POST':

        query1 = text("INSERT INTO persona (nombre, celular) VALUES (:nombre,:celular) RETURNING id")
        id_persona = db_session.execute(query1,{"nombre":request_data['celular'], "celular": request_data['celular']}).fetchone()
        
        # Luego de inertar la persona, obtenemos el codigo del cliente mediante el retorno de id_persona
        codigo_cliente = generar_codigo_cliente(request_data['nombre'], id_persona[0], request_data['celular'])

        query3 = text("INSERT INTO clientes (id_persona, codigo, tipo_cliente, foto, estado) VALUES (:id_persona, :codigo, :tipo_cliente, :foto, :estado)")
        db_session.execute(query3,{"id_persona": id_persona[0], "codigo": codigo_cliente, "tipo_cliente":'Normal', "foto": 'No hay', "estado": '1'})

        # Aquí puedes insertar el código del cliente en tu base de datos

        db_session.commit()
        return codigo_cliente, 200
    return 'null', 400


@app.route('/')
def index():
    print("Enlace de conexion",db_session)

    return render_template('index.html')


def serialize_time(obj):
    if isinstance(obj, time):
        return obj.strftime('%H:%M:%S')
    
@cross_origin()
@app.route('/gethorarios', methods=['GET'])
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
@app.route('/getservicios', methods=['GET'])
def obtener_servicios():
    try:
        query = text('SELECT s.id, s.nombre, ps.precio FROM servicios s LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios WHERE s.estado = 1 and ps.estado = 1')
        result = db_session.execute(query).fetchall()

        # Convertir los resultados a una lista de diccionarios
        servicios = []
        for row in result:
            servicio = {
                "id":row.id,
                "nombre": row.nombre,
                "precio": row.precio
            }
            servicios.append(servicio)

        # Devolver los resultados en formato JSON
        return jsonify(servicios)

    except Exception as error:
        # Manejar errores y devolver una respuesta apropiada
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al obtener los servicios'}), 500

@cross_origin()   
@app.route('/getserviciosdescripcion', methods=['POST'])
def obtener_servicios_descripcion():
    try:
        filtro = request.json.get('filtro', None)

        # Verificar si el filtro es un número entero
        try:
            filtro_id = int(filtro)
        except ValueError:
            # Si no se puede convertir a un número entero, asignar None
            filtro_id = None

        query = """
            SELECT s.nombre, s.descripcion, ps.precio
            FROM servicios s
            LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios
            WHERE s.estado = 1 AND ps.estado = 1
            AND (s.id = :filtro_id OR :filtro_id IS NULL)
        """

        # Ejecutar la consulta y obtener los resultados
        result = db_session.execute(text(query), {'filtro_id': filtro_id}).fetchall()

        # Convertir los resultados a una lista de diccionarios
        servicios = []
        for row in result:
            servicio = {
                "nombre": row.nombre,
                "descripcion": row.descripcion,
                "precio": row.precio
            }
            servicios.append(servicio)

        # Devolver los resultados en formato JSON
        return jsonify(servicios)

    except Exception as error:
        # Manejar errores y devolver una respuesta apropiada
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al obtener los servicios con descripción'}), 500

def ValidarNumeroCelularExistente(numero):
    query = text("SELECT id FROM persona WHERE celular = :numero")
    exists = db_session.execute(query, {"numero": numero}).scalar()
    return exists

@app.route('/validarnumerocelular', methods=['POST'])
def validar_numero_celular():
    try:
        numero_celular = request.json.get('numero_celular')
        existe = ValidarNumeroCelularExistente(numero_celular)

        
        return jsonify({'existe': existe})

    except Exception as error:
       
        print('Error:', str(error))
        return jsonify({'error': 'Ocurrió un error al validar el número de celular'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)