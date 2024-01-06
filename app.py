import os
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import random
from flask import Flask, send_file, session, redirect, url_for, render_template, request, flash, jsonify,make_response
from flask_mail import Mail, Message
from flask_cors import cross_origin, CORS
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from sqlalchemy import create_engine, text, not_, and_, func, select
from sqlalchemy.orm import *
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy
import pdfkit
from pdf2image import convert_from_path
from model import *
import requests

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
app.secret_key = 'tu_clave_secreta'
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


def generar_pdf_servicios():
    # Aquí es donde se renderiza tu plantilla HTML con Jinja
    # Se obtiene la lista de productos
    productos = obtener_productos()

    rendered = render_template('productos.html', productos=productos)
    # Aquí es donde se convierte el HTML renderizado a PDF
    options = {
        'enable-local-file-access': '',
        'page-size': 'A4',
        'no-outline': None,
        'encoding': 'utf-8',
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'no-outline': None
    }
    css = ['static/css/boostrap4.css', 'static/css/style.css']
    pdf = pdfkit.from_string(rendered, False, options=options, css=css)

    # Guardar el PDF en un archivo temporal
    with open('temp.pdf', 'wb') as f:
        f.write(pdf)

    # Convertir el PDF a imagen
    pages = convert_from_path('temp.pdf')
    pages[0].save('output.jpg', 'JPEG')

    return send_file('output.jpg', mimetype='image/jpeg')


@app.route('/pruebita', methods=['GET', 'POST'])
def pruebita():
    productos = obtener_productos()

    return render_template('productos.html', productos=productos)

@app.route('/')
def index():

    generar_pdf_servicios()

    return 'con exito'

def obtener_productos():
    query = text('SELECT s.id,s.descripcion, s.nombre, ps.precio FROM servicios s LEFT JOIN precio_servicios ps ON s.id = ps.id_servicios WHERE s.estado = 1 and ps.estado = 1')
    result = db_session.execute(query).fetchall()

    # Convertir los resultados a una lista de diccionarios
    servicios = []
    for row in result:
        servicio = {
                    "id":row.id,
                    "descripcion":row.descripcion,
                    "nombre": row.nombre,
                    "precio": row.precio
                }
        servicios.append(servicio)

            # Devolver los resultados en formato JSON
    return servicios

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 