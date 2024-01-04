from collections import defaultdict
import os
from dotenv import load_dotenv
load_dotenv()
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import random
from flask import Flask, send_file, session, redirect, url_for, render_template, request, flash, jsonify,make_response
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from sqlalchemy import create_engine, text, not_, and_, func, select
from sqlalchemy.orm import *
from model import *
import requests
import json
from datetime import time

app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SESSION_PERMANENT"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ingsoftwar123@gmail.com'
app.config['MAIL_PASSWORD'] = 'xishvjfvtnrabdpj'
app.secret_key = 'tu_clave_secreta'
mail = Mail(app)

engine = create_engine("postgresql://postgres:root@localhost:5432/Autolavado")
db_session = scoped_session(sessionmaker(bind=engine))
def serialize_time(obj):
    if isinstance(obj, time):
        return obj.strftime('%H:%M:%S')
    
@app.route('/gethorarios', methods=['GET'])
def obtener_horarios():
    try:
        query = text('SELECT * FROM horarios')
        result = db_session.execute(query).fetchall()
        #print(result)
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

@app.route('/getservicios', methods=['GET'])
def obtener_servicios():
    try:
        query = text('SELECT s.nombre, ps.precio FROM servicios s LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios WHERE s.estado = 1 and ps.estado = 1')
        result = db_session.execute(query).fetchall()

        # Convertir los resultados a una lista de diccionarios
        servicios = []
        for row in result:
            servicio = {
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
    

@app.route('/getserviciosdescripcion', methods=['POST'])
def obtener_servicios_descripcion():
    try:
        # Obtener el filtro del cuerpo de la solicitud JSON
        filtro = request.json.get('filtro', None)

        # Construir la consulta SQL con el filtro si está presente
        query = text('SELECT s.nombre, s.descripcion, ps.precio FROM servicios s LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios WHERE s.estado = 1 AND ps.estado = 1')
        if filtro:
            query = query + text(f" AND LOWER(s.nombre) LIKE LOWER('%{filtro}%') LIMIT 1")

        # Ejecutar la consulta y obtener los resultados
        result = db_session.execute(query).fetchall()

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
    
    
if __name__ == '__main__':
    app.run(debug=True)